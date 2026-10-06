#!/usr/bin/env python3
"""Audit a TAAF benchmark run: where actions and generated tokens go, and where score is lost.

Reads the ``benchmark.json`` that every TAAF / Duck-harness run writes to its job
directory (``/kaggle/working`` on Kaggle) and prints a Markdown report.
Standard library only, so it runs anywhere.

    python3 research/audit_run.py /path/to/run_dir            # report to stdout
    python3 research/audit_run.py /path/to/run_dir --out out/  # also writes report.md + levels.csv

Scoring follows ``taaf.game.GameRun._compute_final_score`` (which mirrors the
official ARC-AGI-3 scorecard): a completed level scores min(115, (baseline /
actions)^2 * 100); level i has weight i (1-indexed); the game score is the
weighted mean, capped at (weights of scoring levels / all weights) * 100.

Every run's score is split into percentage points that add up to 100:

  earned       the score the run actually got
  efficiency   points lost on levels it DID complete, because it used more
               actions than the human baseline
  stalled      the weight of the level it was on when the run ended
  unreached    the weight of the levels after that one
  (bonus)      points gained by beating the baseline (counted against the loss)

so ``earned = 100 - efficiency - stalled - unreached + bonus`` (before the
official cap, which only binds in rare cases and is reported separately).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

LEVEL_CAP = 115.0


# --------------------------------------------------------------------------- data


@dataclass
class Level:
    index: int  # 0-based
    weight: int
    baseline: int
    actions: int
    completed: bool
    tokens: int  # generated tokens attributed to this level
    resets: int
    score: float  # 0..115

    @property
    def ratio(self) -> float:
        """Actions used per human-baseline action (only meaningful if completed)."""
        return self.actions / self.baseline if self.baseline else math.nan


@dataclass
class Run:
    game_id: str
    pass_id: str
    n_levels: int
    levels_completed: int
    reported_score: float
    total_tokens: int
    levels: list[Level] = field(default_factory=list)
    trailing_tokens: int = 0  # generated after the last action

    # -- decomposition, in percentage points of the game score
    @property
    def total_weight(self) -> int:
        return sum(lv.weight for lv in self.levels)

    def score_uncapped(self) -> float:
        return sum(lv.score * lv.weight for lv in self.levels) / self.total_weight

    def score_capped(self) -> float:
        max_w = sum(lv.weight for lv in self.levels if lv.score > 0)
        return min(self.score_uncapped(), max_w / self.total_weight * 100.0)

    def parts(self) -> dict[str, float]:
        W = self.total_weight
        eff = bonus = stalled = unreached = 0.0
        for lv in self.levels:
            if lv.completed and lv.actions > 0:
                if lv.score < 100:
                    eff += (100 - lv.score) * lv.weight / W
                else:
                    bonus += (lv.score - 100) * lv.weight / W
            elif lv.index == self.levels_completed:
                stalled += 100 * lv.weight / W
            else:
                unreached += 100 * lv.weight / W
        return {
            "earned": self.score_capped(),
            "efficiency": eff,
            "stalled": stalled,
            "unreached": unreached,
            "bonus": bonus,
            "cap_cut": self.score_uncapped() - self.score_capped(),
        }

    @property
    def stalled_level(self) -> Level | None:
        if self.levels_completed < self.n_levels:
            return self.levels[self.levels_completed]
        return None


def _pass_id(raw: dict, seen: Counter) -> str:
    html = raw.get("solver_analysis_html") or ""
    m = re.search(r"_p(\d+)\.html$", html)
    if m:
        return f"p{m.group(1)}"
    gid = raw["game_id"]
    seen[gid] += 1
    return f"p{seen[gid] - 1}"


def _total_tokens(raw: dict, history_tokens: int) -> int:
    note = raw.get("solver_note") or ""
    m = re.search(r"tokens=(\d+)", note)
    return int(m.group(1)) if m else history_tokens


def load_runs(path: Path) -> tuple[dict, list[Run]]:
    bench_path = path / "benchmark.json" if path.is_dir() else path
    bench = json.loads(bench_path.read_text())
    runs: list[Run] = []
    seen: Counter = Counter()
    skipped = 0
    for raw in bench.get("game_runs", []):
        base = raw.get("base_actions_per_level")
        apl = raw.get("actions_per_level") or []
        hist = raw.get("history") or []
        n = int(raw.get("number_of_levels") or 0)
        if not base or n == 0:
            skipped += 1
            continue
        lc = int(raw.get("levels_completed") or 0)
        hist_tokens = sum(int(h.get("generated_tokens") or 0) for h in hist)
        run = Run(
            game_id=raw["game_id"],
            pass_id=_pass_id(raw, seen),
            n_levels=n,
            levels_completed=lc,
            reported_score=float(raw.get("final_score") or 0.0),
            total_tokens=_total_tokens(raw, hist_tokens),
        )
        run.trailing_tokens = max(0, run.total_tokens - hist_tokens)
        # History is in order and actions_per_level partitions it exactly, so a
        # running offset attributes each action (and the tokens generated before
        # it) to the level it was taken on.
        consistent = sum(apl) == len(hist)
        start = 0
        for i in range(n):
            a = apl[i] if i < len(apl) else 0
            chunk = hist[start : start + a] if consistent else []
            start += a
            completed = i < lc
            if completed and a > 0:
                score = min(LEVEL_CAP, (base[i] / a) ** 2 * 100)
            else:
                score = 0.0
            run.levels.append(
                Level(
                    index=i,
                    weight=i + 1,
                    baseline=int(base[i]),
                    actions=int(a),
                    completed=completed,
                    tokens=sum(int(h.get("generated_tokens") or 0) for h in chunk),
                    resets=sum(1 for h in chunk if (h.get("action") or {}).get("id") == "RESET"),
                    score=score,
                )
            )
        # Tokens generated after the last action belong to the level the run
        # was stuck on when it ended.
        stalled = run.stalled_level
        if stalled is not None:
            stalled.tokens += run.trailing_tokens
        elif run.levels:
            run.levels[-1].tokens += run.trailing_tokens
        runs.append(run)
    meta = {
        "label": bench.get("label"),
        "n_passes": bench.get("n_passes"),
        "start_time": bench.get("start_time"),
        "end_time": bench.get("end_time"),
        "skipped_runs": skipped,
        "source": str(bench_path),
    }
    return meta, runs


# --------------------------------------------------------------------------- helpers


def mean(xs) -> float:
    xs = list(xs)
    return st.mean(xs) if xs else math.nan


def median(xs) -> float:
    xs = list(xs)
    return st.median(xs) if xs else math.nan


def pct(x: float, total: float) -> str:
    return f"{100 * x / total:.0f}%" if total else "n/a"


def fmt(x: float, nd: int = 1) -> str:
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}"


def quantile(xs, q: float) -> float:
    xs = sorted(xs)
    if not xs:
        return math.nan
    k = (len(xs) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def table(headers: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


# --------------------------------------------------------------------------- report


def report(meta: dict, runs: list[Run]) -> str:
    if not runs:
        return "No scorable runs found."
    by_game: dict[str, list[Run]] = defaultdict(list)
    for r in runs:
        by_game[r.game_id].append(r)
    games = sorted(by_game)
    passes = sorted({r.pass_id for r in runs}, key=lambda p: int(p[1:]) if p[1:].isdigit() else p)

    # Equal weight per game (as the official score), averaging that game's passes.
    def game_mean(fn) -> float:
        return mean(mean(fn(r) for r in by_game[g]) for g in games)

    L: list[str] = []
    L.append("# Run audit")
    L.append("")
    L.append(
        f"Source: `{meta['source']}` · label `{meta.get('label')}` · "
        f"{len(games)} games × {len(passes)} passes = {len(runs)} runs"
        + (f" · {meta['skipped_runs']} runs skipped (no baseline)" if meta["skipped_runs"] else "")
    )
    L.append("")

    # ---------------------------------------------------------- 1. headline + check
    official = game_mean(lambda r: r.reported_score)
    recomputed = game_mean(lambda r: r.score_capped())
    mismatches = sum(1 for r in runs if abs(r.reported_score - r.score_capped()) > 1e-6)
    L.append("## 1. Score")
    L.append("")
    L.append(f"- Mean score: **{official:.2f}** (recomputed from per-level actions: {recomputed:.2f}; "
             f"{mismatches} of {len(runs)} runs disagree with the reported score)")
    pass_means = []
    for p in passes:
        vals = [r.score_capped() for r in runs if r.pass_id == p]
        if len(vals) == len(games):
            pass_means.append(mean(vals))
    if len(pass_means) >= 2:
        sd = st.stdev(pass_means)
        m = mean(pass_means)
        cv = sd / m if m else math.nan
        L.append(
            f"- One full pass over these {len(games)} games scored between {min(pass_means):.2f} and "
            f"{max(pass_means):.2f} (sd {sd:.2f}, i.e. ±{100 * cv:.0f}% of the mean)."
        )
        z = 1.96 + 0.84  # two-sided 5% test, 80% power
        need = [(rel, math.ceil(2 * z * z * cv * cv / (rel * rel))) for rel in (0.1, 0.2, 0.3)]
        L.append(
            "- Passes needed per version to detect an improvement of "
            + ", ".join(f"+{int(rel * 100)}%: ~{n}" for rel, n in need)
            + "."
        )
    else:
        L.append("- Only one complete pass: run-to-run noise cannot be measured from this run.")
    L.append("")

    # ---------------------------------------------------------- 2. where points go
    parts = {k: game_mean(lambda r, k=k: r.parts()[k]) for k in
             ("earned", "efficiency", "stalled", "unreached", "bonus", "cap_cut")}
    L.append("## 2. Where the points go")
    L.append("")
    L.append("Every game is worth 100 points. On average a game's 100 points split like this:")
    L.append("")
    L.append(table(
        ["", "points", "meaning"],
        [
            ["earned", fmt(parts["earned"]), "the score"],
            ["lost to inefficiency", fmt(parts["efficiency"]), "levels completed, but with more actions than the human baseline"],
            ["lost on the stalled level", fmt(parts["stalled"]), "the level the run was stuck on when it ended"],
            ["lost on unreached levels", fmt(parts["unreached"]), "levels after the stalled one"],
            ["bonus", fmt(parts["bonus"]), "beating the baseline (up to 115 per level)"],
        ],
    ))
    if parts["cap_cut"] > 0.005:
        L.append(f"\n(The official cap removed a further {parts['cap_cut']:.2f} points on average.)")
    perfect_eff = parts["earned"] + parts["efficiency"] - parts["bonus"]
    L.append("")
    L.append(
        f"If every level these runs completed had been done in exactly the human number of actions, "
        f"the score would be about **{perfect_eff:.1f}** instead of {parts['earned']:.1f}. "
        f"Everything else that is missing comes from levels that were never completed."
    )
    L.append("")

    # ---------------------------------------------------------- 3. efficiency
    done = [lv for r in runs for lv in r.levels if lv.completed and lv.actions > 0]
    L.append("## 3. Action efficiency on completed levels")
    L.append("")
    if done:
        ratios = [lv.ratio for lv in done]
        buckets = [("at or under human (≤1×)", lambda x: x <= 1.0), ("1–2×", lambda x: 1 < x <= 2),
                   ("2–4×", lambda x: 2 < x <= 4), ("over 4×", lambda x: x > 4)]
        rows = []
        for name, f in buckets:
            sel = [lv for lv in done if f(lv.ratio)]
            lost = sum((100 - min(lv.score, 100)) * lv.weight for lv in sel)
            rows.append([name, len(sel), pct(len(sel), len(done)), fmt(mean(lv.score for lv in sel), 0)])
        L.append(f"{len(done)} completed levels; median actions used = **{median(ratios):.2f}×** the human baseline.")
        L.append("")
        L.append(table(["actions vs human", "levels", "share", "mean level score"], rows))
        L.append("")
        resets = [lv.resets for lv in done]
        L.append(f"Completed levels contained {sum(resets)} RESET actions in total "
                 f"({pct(sum(1 for x in resets if x), len(done))} of completed levels had at least one).")
    else:
        L.append("No completed levels.")
    L.append("")

    # ---------------------------------------------------------- 4. by level number
    L.append("## 4. By level number")
    L.append("")
    max_n = max(r.n_levels for r in runs)
    rows = []
    for i in range(max_n):
        att = [r.levels[i] for r in runs if i < r.n_levels and i <= r.levels_completed]
        if not att:
            continue
        comp = [lv for lv in att if lv.completed]
        rows.append([
            i + 1,
            len(att),
            pct(len(comp), len(att)),
            fmt(median(lv.ratio for lv in comp), 2) if comp else "n/a",
            fmt(median(lv.tokens for lv in comp) / 1000, 1) if comp else "n/a",
        ])
    L.append("A level counts as *attempted* if the run reached it.")
    L.append("")
    L.append(table(["level", "attempted", "completed", "median actions vs human", "median k tokens to complete"], rows))
    L.append("")

    # ---------------------------------------------------------- 5. tokens
    tot_tok = sum(r.total_tokens for r in runs)
    tok_done = sum(lv.tokens for r in runs for lv in r.levels if lv.completed)
    tok_stall = sum(lv.tokens for r in runs for lv in r.levels if not lv.completed)
    L.append("## 5. Where generated tokens go")
    L.append("")
    L.append(f"{tot_tok / 1e6:.1f}M generated tokens in total, {tot_tok / len(runs) / 1000:.0f}k per run.")
    L.append("")
    L.append(table(
        ["spent on", "tokens", "share"],
        [
            ["levels that were completed", f"{tok_done / 1e6:.1f}M", pct(tok_done, tot_tok)],
            ["the stalled level (never converted to points)", f"{tok_stall / 1e6:.1f}M", pct(tok_stall, tot_tok)],
        ],
    ))
    L.append("")
    # Late stall: tokens on a stalled level beyond what 90% of completions of
    # that level number needed. A scheduler could in principle move these.
    p90 = {}
    for i in range(max_n):
        comp_tok = [r.levels[i].tokens for r in runs if i < r.levels_completed]
        if len(comp_tok) >= 5:
            p90[i] = quantile(comp_tok, 0.9)
    late = 0
    for r in runs:
        lv = r.stalled_level
        if lv is not None and lv.index in p90:
            late += max(0.0, lv.tokens - p90[lv.index])
    L.append(
        f"Of the stalled-level tokens, about **{late / 1e6:.1f}M ({pct(late, tot_tok)} of all tokens)** were spent "
        f"after the run had already used more tokens on that level than 90% of successful completions of the "
        f"same level number needed. That is the compute a smarter scheduler could most plausibly have moved "
        f"to another game."
    )
    L.append("")

    # ---------------------------------------------------------- 6. per game
    L.append("## 6. Per game")
    L.append("")
    L.append("Means over passes. *Stall* = the level number the run was on when it ended (median over passes).")
    L.append("")
    rows = []
    for g in sorted(games, key=lambda g: -mean(r.score_capped() for r in by_game[g])):
        rs = by_game[g]
        pm = [r.parts() for r in rs]
        comp = [lv for r in rs for lv in r.levels if lv.completed and lv.actions > 0]
        stall_lv = [r.levels_completed + 1 for r in rs if r.levels_completed < r.n_levels]
        stall_tok = sum(r.stalled_level.tokens for r in rs if r.stalled_level is not None)
        all_tok = sum(r.total_tokens for r in rs)
        rows.append([
            g.split("-")[0],
            fmt(mean(r.score_capped() for r in rs)),
            f"{mean(r.levels_completed for r in rs):.1f}/{rs[0].n_levels}",
            fmt(median(stall_lv), 0) if stall_lv else "done",
            fmt(median(lv.ratio for lv in comp), 2) if comp else "n/a",
            fmt(mean(p["efficiency"] for p in pm)),
            fmt(mean(p["stalled"] + p["unreached"] for p in pm)),
            pct(stall_tok, all_tok),
            f"{mean(r.total_tokens for r in rs) / 1000:.0f}k",
        ])
    L.append(table(
        ["game", "score", "levels", "stall", "actions vs human", "lost: efficiency", "lost: not completed",
         "tokens on stalled level", "tokens/run"],
        rows,
    ))
    L.append("")
    return "\n".join(L)


def write_levels_csv(runs: list[Run], path: Path) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["game_id", "pass", "level", "weight", "baseline", "actions", "completed", "stalled_here",
                    "level_score", "actions_vs_human", "tokens", "resets"])
        for r in runs:
            for lv in r.levels:
                w.writerow([r.game_id, r.pass_id, lv.index + 1, lv.weight, lv.baseline, lv.actions,
                            int(lv.completed), int(lv.index == r.levels_completed and not lv.completed),
                            f"{lv.score:.3f}", f"{lv.ratio:.3f}" if lv.completed else "", lv.tokens, lv.resets])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("run", type=Path, help="run directory containing benchmark.json, or the file itself")
    ap.add_argument("--out", type=Path, help="directory to write report.md and levels.csv")
    args = ap.parse_args(argv)
    meta, runs = load_runs(args.run)
    text = report(meta, runs)
    print(text)
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "report.md").write_text(text + "\n")
        write_levels_csv(runs, args.out / "levels.csv")
        print(f"\nwrote {args.out / 'report.md'} and {args.out / 'levels.csv'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
