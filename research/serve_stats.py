"""Summarise an SGLang serve.log from a notebook run: how busy the GPU was.

    python3 research/serve_stats.py path/to/serve.log [more serve.log ...]

For each log, prints in markdown:
  - KV-cache capacity and how full it got, per half hour
  - how many requests were generating at once (the server's max is the limit)
  - decode throughput, overall and by number of running requests, and the
    gain if every slot had always been busy
  - prompt tokens processed from scratch versus served from the prefix cache
Several logs are summarised side by side in a final comparison table.
"""
from __future__ import annotations

import re
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

_LINE = re.compile(r"\[(\S+ \S+)\] (Decode|Prefill) batch, (.*)")
_FIELD = re.compile(r"([#a-z ()/-]+?): ([0-9.]+|True|False)")


def _parse(path: Path) -> dict:
    decode, prefill = [], []
    capacity = max_running = None
    for line in path.open(errors="replace"):
        if capacity is None:
            m = re.search(r"max_total_num_tokens=(\d+)", line)
            if m:
                capacity = int(m.group(1))
                r = re.search(r"max_running_requests=(\d+)", line)
                max_running = int(r.group(1)) if r else None
        m = _LINE.match(line)
        if not m:
            continue
        t = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").timestamp()
        fields = {k.strip(): float(v) for k, v in _FIELD.findall(m.group(3)) if v not in ("True", "False")}
        (decode if m.group(2) == "Decode" else prefill).append((t, fields))
    return {"decode": decode, "prefill": prefill, "capacity": capacity, "max_running": max_running}


def summarise(path: Path) -> tuple[str, dict]:
    d = _parse(path)
    dec, pre = d["decode"], d["prefill"]
    if not dec:
        return f"## {path}\n\nNo decode statistics found.\n", {}
    t0 = dec[0][0]
    span_h = (dec[-1][0] - t0) / 3600
    lines = [f"## {path}", ""]
    lines.append(f"KV cache: {d['capacity']:,} tokens; server limit {d['max_running']} running requests; "
                 f"{span_h:.2f} h of decoding statistics.")
    lines.append("")
    lines.append("| from | requests generating (mean) | share of time at the limit | KV used (mean / max) | decode tokens/s (median) |")
    lines.append("|---|---|---|---|---|")
    windows: dict[int, list[dict]] = defaultdict(list)
    for t, f in dec:
        windows[int((t - t0) // 1800)].append(f)
    limit = d["max_running"] or max(f.get("#running-req", 0) for _, f in dec)
    for w in sorted(windows):
        fs = windows[w]
        running = [f.get("#running-req", 0) for f in fs]
        kv = [f.get("full token usage", 0) for f in fs]
        gen = [f.get("gen throughput (token/s)", 0) for f in fs]
        lines.append(f"| {w * 0.5:.1f} h | {st.mean(running):.1f} | {sum(r >= limit for r in running) / len(running):.0%} | "
                     f"{st.mean(kv):.2f} / {max(kv):.2f} | {st.median(gen):.0f} |")
    lines.append("")
    by_running: dict[int, list[float]] = defaultdict(list)
    for _, f in dec:
        by_running[int(f.get("#running-req", 0))].append(f.get("gen throughput (token/s)", 0))
    lines.append("Decode tokens/s by requests generating: " + ", ".join(
        f"{k}: {st.median(v):.0f}" for k, v in sorted(by_running.items()) if len(v) >= 20))
    mean_gen = st.mean(f.get("gen throughput (token/s)", 0) for _, f in dec)
    full = st.median(by_running[limit]) if by_running.get(limit) else float("nan")
    lines.append(f"Mean decode throughput {mean_gen:.0f} tokens/s; with every slot busy {full:.0f} "
                 f"(+{full / mean_gen - 1:.0%}).")
    new = sum(f.get("#new-token", 0) for _, f in pre)
    cached = sum(f.get("#cached-token", 0) for _, f in pre)
    misses = [f for _, f in pre if f.get("#new-token", 0) >= 8000 and f.get("#cached-token", 0) < f.get("#new-token", 0)]
    miss_tokens = sum(f.get("#new-token", 0) for f in misses)
    lines.append(f"Prompt tokens: {cached / 1e6:.1f}M from cache, {new / 1e6:.1f}M processed "
                 f"({cached / (new + cached):.1%} cached); {len(misses)} large prompts mostly not cached "
                 f"({miss_tokens / 1e6:.1f}M tokens).")
    lines.append("")
    stats = {
        "hours": span_h, "mean_running": st.mean(f.get("#running-req", 0) for _, f in dec),
        "mean_gen": mean_gen, "full_gen": full, "kv_max": max(f.get("full token usage", 0) for _, f in dec),
        "kv_mean": st.mean(f.get("full token usage", 0) for _, f in dec),
        "new_M": new / 1e6, "miss_M": miss_tokens / 1e6, "misses": len(misses),
    }
    return "\n".join(lines), stats


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    all_stats = []
    for arg in argv[1:]:
        text, stats = summarise(Path(arg))
        print(text)
        all_stats.append((arg, stats))
    if len(all_stats) > 1:
        print("## Comparison\n")
        print("| log | requests generating | mean decode tokens/s | KV mean / max | prompt tokens processed | large uncached prompts |")
        print("|---|---|---|---|---|---|")
        for arg, s in all_stats:
            if s:
                print(f"| {arg} | {s['mean_running']:.2f} | {s['mean_gen']:.0f} | {s['kv_mean']:.2f} / {s['kv_max']:.2f} | "
                      f"{s['new_M']:.1f}M | {s['misses']} ({s['miss_M']:.1f}M) |")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
