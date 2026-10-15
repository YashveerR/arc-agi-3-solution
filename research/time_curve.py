"""Score, levels and generated tokens over the course of a run.

    python3 research/time_curve.py RUN [RUN ...] [--every 0.5] [--labels a,b,...]

RUN is a run directory (with benchmark.json) or the file itself, gzipped or
not. For each checkpoint (hours since the benchmark started) prints, per run:
the mean score the run would have had if it had stopped then, the levels
completed by then, and the generated tokens by then. Runs of different
lengths (a crash) are compared over the time they share.

A level counts from the moment of its last action. Its score is fixed then
(the official per-level formula and the completed-weight cap, as in
audit_run.py). Tokens are counted at the action they preceded, so tokens
spent after a run's last action are missing from the curve (they are in the
final totals). Standard library only.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from datetime import datetime
from pathlib import Path

LEVEL_CAP = 115.0


def _load(path: Path) -> dict:
    if path.is_dir():
        for name in ("benchmark.json", "benchmark.json.gz"):
            if (path / name).exists():
                path = path / name
                break
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as handle:
        return json.load(handle)


def events(bench: dict) -> list[dict]:
    """Per game run: start offset (s), level completion times and the
    cumulative-token timeline, all in seconds since the benchmark start."""
    t0 = datetime.fromisoformat(bench["start_time"])
    out = []
    for raw in bench["game_runs"]:
        hist = raw.get("history") or []
        apl = raw.get("actions_per_level") or []
        base = raw.get("base_actions_per_level") or []
        n = int(raw.get("number_of_levels") or 0)
        lc = int(raw.get("levels_completed") or 0)
        if not base or not n:
            continue
        start = (datetime.fromisoformat(raw["started_at"]) - t0).total_seconds() if raw.get("started_at") else 0.0
        times = [start + float(h.get("wallclock_seconds") or 0.0) for h in hist]
        tokens = []
        total = 0
        for h in hist:
            total += int(h.get("generated_tokens") or 0)
            tokens.append(total)
        done = []  # (time, level index, level score)
        pos = 0
        consistent = sum(apl) == len(hist)
        for i in range(min(lc, len(apl))):
            a = int(apl[i])
            pos += a
            if not consistent or a <= 0 or pos == 0:
                continue
            done.append((times[pos - 1], i, min(LEVEL_CAP, (base[i] / a) ** 2 * 100)))
        out.append({"n": n, "done": done, "times": times, "tokens": tokens,
                    "end": start + float(raw.get("final_wallclock_seconds") or (times[-1] if times else 0))})
    return out


def score_at(run: dict, t: float) -> float:
    n = run["n"]
    weight = n * (n + 1) / 2
    got = [(i, s) for (tt, i, s) in run["done"] if tt <= t]
    uncapped = sum((i + 1) * s for i, s in got) / weight
    cap = sum(i + 1 for i, _ in got) / weight * 100
    return min(uncapped, cap)


def tokens_at(run: dict, t: float) -> int:
    best = 0
    for tt, tok in zip(run["times"], run["tokens"]):
        if tt > t:
            break
        best = tok
    return best


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--every", type=float, default=0.5, help="hours between checkpoints")
    ap.add_argument("--labels", default="")
    args = ap.parse_args(argv)
    labels = args.labels.split(",") if args.labels else [p.parent.name if p.is_file() else p.name for p in args.runs]
    data = []
    for p in args.runs:
        bench = _load(p)
        dur = (datetime.fromisoformat(bench["end_time"]) - datetime.fromisoformat(bench["start_time"])).total_seconds()
        data.append((events(bench), dur))
    longest = max(d for _, d in data)
    checkpoints = []
    t = args.every
    while t * 3600 <= longest + 1:
        checkpoints.append(t)
        t += args.every
    if not checkpoints or checkpoints[-1] * 3600 < longest - 60:
        checkpoints.append(longest / 3600)
    print("| hours | " + " | ".join(f"{lab}: score / levels / M tokens" for lab in labels) + " |")
    print("|---|" + "---|" * len(labels))
    for h in checkpoints:
        cells = []
        for runs, dur in data:
            if h * 3600 > dur + 1:
                cells.append("ended")
                continue
            sec = h * 3600
            score = sum(score_at(r, sec) for r in runs) / len(runs)
            levels = sum(1 for r in runs for (tt, _, _) in r["done"] if tt <= sec)
            toks = sum(tokens_at(r, sec) for r in runs) / 1e6
            cells.append(f"{score:.1f} / {levels} / {toks:.2f}")
        print(f"| {h:.2f} | " + " | ".join(cells) + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
