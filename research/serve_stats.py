"""Summarise a model-server log from a notebook run: how busy the GPU was.

    python3 research/serve_stats.py path/to/serve.log [more logs ...]

Reads SGLang's serve.log (Franzen's server) and vLLM's vllm-openai-server.log
(lordhansolo's server, research/vllm_server/); the format is detected per file.

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


# vLLM logs one line like this every 10 s while the engine is busy:
#   ... INFO 10-17 03:12:45 [loggers.py:321] Engine 000: Avg prompt throughput: 1234.5 tokens/s,
#   Avg generation throughput: 987.6 tokens/s, Running: 12 reqs, Waiting: 0 reqs, [Preemptions: 2,]
#   GPU KV cache usage: 85.2%, Prefix cache hit rate: 93.1%
_VLLM_STATS = re.compile(
    r"(\d\d-\d\d \d\d:\d\d:\d\d) \[[^\]]*\] Engine \d+: Avg prompt throughput: ([0-9.]+) tokens/s, "
    r"Avg generation throughput: ([0-9.]+) tokens/s, Running: (\d+) reqs, Waiting: (\d+) reqs"
    r"(?:, Deferred: \d+ reqs)?(?:, Preemptions: (\d+))?, GPU KV cache usage: ([0-9.]+)%"
    r"(?:, Prefix cache hit rate: ([0-9.]+)%)?"
)
_VLLM_SPEC = re.compile(r"SpecDecoding metrics: Mean acceptance length: ([0-9.]+)")


def _parse_vllm(path: Path) -> dict:
    rows, accept = [], []
    capacity = max_running = None
    year = datetime.now().year
    for line in path.open(errors="replace"):
        if capacity is None:
            m = re.search(r"KV cache size: ([0-9,]+) tokens", line)
            if m:
                capacity = int(m.group(1).replace(",", ""))
        if max_running is None:
            m = re.search(r"--max-num-seqs[ =](\d+)|'max_num_seqs': (\d+)", line)
            if m:
                max_running = int(m.group(1) or m.group(2))
        m = _VLLM_STATS.search(line)
        if m:
            t = datetime.strptime(f"{year}-{m.group(1)}", "%Y-%m-%d %H:%M:%S").timestamp()
            rows.append({
                "t": t, "prompt_tps": float(m.group(2)), "gen_tps": float(m.group(3)),
                "running": int(m.group(4)), "waiting": int(m.group(5)),
                "preemptions": int(m.group(6) or 0), "kv": float(m.group(7)) / 100,
                "hit": float(m.group(8)) / 100 if m.group(8) else None,
            })
            continue
        m = _VLLM_SPEC.search(line)
        if m:
            accept.append(float(m.group(1)))
    return {"rows": rows, "capacity": capacity, "max_running": max_running, "accept": accept}


def summarise_vllm(path: Path) -> tuple[str, dict]:
    d = _parse_vllm(path)
    rows = d["rows"]
    if not rows:
        return f"## {path}\n\nNo decode statistics found.\n", {}
    t0 = rows[0]["t"]
    # Each line averages the interval since the previous one; a gap (an idle
    # engine logs nothing) is counted as one 10 s interval, not as busy time.
    for i, r in enumerate(rows):
        r["dt"] = min(30.0, r["t"] - rows[i - 1]["t"]) if i else 10.0
    span_h = (rows[-1]["t"] - t0) / 3600
    limit = d["max_running"] or max(r["running"] for r in rows)
    cap = f"{d['capacity']:,}" if d["capacity"] else "unknown"
    lines = [f"## {path}", "",
             f"vLLM. KV cache: {cap} tokens; server limit {limit} running requests; "
             f"{span_h:.2f} h of statistics.", "",
             "| from | requests generating (mean) | share of time at the limit | KV used (mean / max) | "
             "generated tokens/s (mean) | prefix cache hit rate |",
             "|---|---|---|---|---|---|"]
    windows: dict[int, list[dict]] = defaultdict(list)
    for r in rows:
        windows[int((r["t"] - t0) // 1800)].append(r)
    for w in sorted(windows):
        rs = windows[w]
        hits = [r["hit"] for r in rs if r["hit"] is not None]
        lines.append(f"| {w * 0.5:.1f} h | {st.mean(r['running'] for r in rs):.1f} | "
                     f"{sum(r['running'] >= limit for r in rs) / len(rs):.0%} | "
                     f"{st.mean(r['kv'] for r in rs):.2f} / {max(r['kv'] for r in rs):.2f} | "
                     f"{st.mean(r['gen_tps'] for r in rs):.0f} | {st.mean(hits):.1%} |" if hits else
                     f"| {w * 0.5:.1f} h | {st.mean(r['running'] for r in rs):.1f} | "
                     f"{sum(r['running'] >= limit for r in rs) / len(rs):.0%} | "
                     f"{st.mean(r['kv'] for r in rs):.2f} / {max(r['kv'] for r in rs):.2f} | "
                     f"{st.mean(r['gen_tps'] for r in rs):.0f} | n/a |")
    lines.append("")
    by_running: dict[int, list[float]] = defaultdict(list)
    for r in rows:
        by_running[r["running"]].append(r["gen_tps"])
    lines.append("Generated tokens/s by requests running: " + ", ".join(
        f"{k}: {st.median(v):.0f}" for k, v in sorted(by_running.items()) if len(v) >= 20))
    mean_gen = st.mean(r["gen_tps"] for r in rows)
    full = st.median(by_running[limit]) if by_running.get(limit) else float("nan")
    generated = sum(r["gen_tps"] * r["dt"] for r in rows)
    prompt = sum(r["prompt_tps"] * r["dt"] for r in rows)
    preempt = sum(r["preemptions"] for r in rows)
    lines.append(f"Mean generation throughput {mean_gen:.0f} tokens/s; with every slot busy {full:.0f} "
                 f"(+{full / mean_gen - 1:.0%}). About {generated / 1e6:.1f}M tokens generated.")
    lines.append(f"Prompt tokens processed (not served from the prefix cache): about {prompt / 1e6:.1f}M. "
                 f"Preemptions: {preempt}. Waiting requests (mean): {st.mean(r['waiting'] for r in rows):.2f}.")
    if d["accept"]:
        lines.append(f"Speculative decoding: mean acceptance length {st.mean(d['accept']):.2f} tokens per step.")
    lines.append("")
    stats = {
        "hours": span_h, "mean_running": st.mean(r["running"] for r in rows), "mean_gen": mean_gen,
        "full_gen": full, "kv_max": max(r["kv"] for r in rows), "kv_mean": st.mean(r["kv"] for r in rows),
        "new_M": prompt / 1e6, "miss_M": float("nan"), "misses": None, "preemptions": preempt,
    }
    return "\n".join(lines), stats


def summarise(path: Path) -> tuple[str, dict]:
    d = _parse(path)
    dec, pre = d["decode"], d["prefill"]
    if not dec:
        vllm_text, vllm_stats = summarise_vllm(path)
        if vllm_stats:
            return vllm_text, vllm_stats
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
                misses = "n/a (vLLM)" if s["misses"] is None else f"{s['misses']} ({s['miss_M']:.1f}M)"
                print(f"| {arg} | {s['mean_running']:.2f} | {s['mean_gen']:.0f} | {s['kv_mean']:.2f} / {s['kv_max']:.2f} | "
                      f"{s['new_M']:.1f}M | {misses} |")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
