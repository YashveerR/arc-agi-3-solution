"""Compare two runs of the same games: did a change help, or is it noise?

    python3 research/compare_runs.py BASELINE_DIR_OR_JSON CANDIDATE_DIR_OR_JSON [--threshold 60000]

Prints, in markdown:
  1. mean scores and the paired per-game difference with its standard error
  2. levels stuck past the threshold: how many were completed later in each run,
     with a two-sided Fisher exact test
  3. how soon after the threshold those late completions came
  4. the same game-levels stuck past the threshold in both runs
  5. where generated tokens went

Uses the loader from audit_run.py, so both runs are read the same way.
"""
from __future__ import annotations

import argparse
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_run import Run, fisher_two_sided, load_runs, median, table  # noqa: E402


def _stuck(runs: list[Run], threshold: int) -> list[tuple[str, str, int, int, bool]]:
    """(game, pass, level number, tokens on level, completed) for every reached
    level that used more than `threshold` tokens."""
    out = []
    for r in runs:
        for lv in r.levels:
            reached = lv.completed or lv is r.stalled_level
            if reached and lv.tokens > threshold:
                out.append((r.game_id.split("-")[0], r.pass_id, lv.index + 1, lv.tokens, lv.completed))
    return out


def compare(base: list[Run], cand: list[Run], threshold: int) -> str:
    k = threshold // 1000
    lines: list[str] = ["# Run comparison", ""]

    # 1. scores
    by_game_b: dict[str, list[Run]] = defaultdict(list)
    by_game_c: dict[str, list[Run]] = defaultdict(list)
    for r in base:
        by_game_b[r.game_id].append(r)
    for r in cand:
        by_game_c[r.game_id].append(r)
    games = sorted(set(by_game_b) & set(by_game_c))
    rows, diffs = [], []
    for g in games:
        sb = sum(r.reported_score for r in by_game_b[g]) / len(by_game_b[g])
        sc = sum(r.reported_score for r in by_game_c[g]) / len(by_game_c[g])
        diffs.append(sc - sb)
        lb = ", ".join(str(r.levels_completed) for r in by_game_b[g])
        lc = ", ".join(str(r.levels_completed) for r in by_game_c[g])
        fired = ", ".join(
            name for name, hit in (
                ("fresh start", any(r.fresh_starts for r in by_game_c[g])),
                ("review", any(r.review_arm == "on" and r.reviews for r in by_game_c[g])),
            ) if hit
        )
        rows.append([g.split("-")[0], f"{sb:.1f}", f"{sc:.1f}", f"{sc - sb:+.1f}", lb, lc, fired])
    rows.sort(key=lambda row: float(row[3]))
    mb = sum(r.reported_score for r in base) / len(base)
    mc = sum(r.reported_score for r in cand) / len(cand)
    mean_diff = sum(diffs) / len(diffs)
    se = (sum((d - mean_diff) ** 2 for d in diffs) / (len(diffs) - 1)) ** 0.5 / len(diffs) ** 0.5
    lines += [
        "## 1. Score", "",
        f"Baseline mean **{mb:.2f}** ({len(base)} runs), candidate mean **{mc:.2f}** ({len(cand)} runs).",
        f"Paired over {len(games)} games: difference **{mean_diff:+.2f}** (standard error {se:.2f}, "
        f"so roughly {mean_diff - 2 * se:+.1f} to {mean_diff + 2 * se:+.1f}).", "",
        table(["game", "baseline", "candidate", "difference", "levels (baseline)", "levels (candidate)", "intervention fired"], rows),
        "",
    ]

    # 2. stuck levels
    sb_, sc_ = _stuck(base, threshold), _stuck(cand, threshold)
    db, dc = sum(1 for s in sb_ if s[4]), sum(1 for s in sc_ if s[4])
    nb, nc = len(sb_), len(sc_)
    p = fisher_two_sided(dc, nc - dc, db, nb - db)
    rb, rc = db / max(1, nb), dc / max(1, nc)
    se2 = (rb * (1 - rb) / max(1, nb) + rc * (1 - rc) / max(1, nc)) ** 0.5
    lines += [
        f"## 2. Levels stuck past {k}k tokens", "",
        f"Baseline: {db} of {nb} completed later ({rb:.0%}). Candidate: {dc} of {nc} ({rc:.0%}).",
        f"Difference {rc - rb:+.0%} (95% interval about {rc - rb - 1.96 * se2:+.0%} to {rc - rb + 1.96 * se2:+.0%}); "
        f"Fisher exact two-sided p = {p:.2f}.", "",
    ]

    # 3. speed of late completions
    def after(stuck):
        done = [s[3] - threshold for s in stuck if s[4]]
        undone = [s[3] - threshold for s in stuck if not s[4]]
        return done, undone

    rows = []
    for name, stuck in (("baseline", sb_), ("candidate", sc_)):
        done, undone = after(stuck)
        rows.append([
            name,
            f"{median(done) / 1000:.0f}k" if done else "n/a",
            sum(1 for t in done if t <= 30000),
            f"{median(undone) / 1000:.0f}k" if undone else "n/a",
        ])
    lines += [
        f"## 3. What happened after {k}k", "",
        table(["run", "completed later: median tokens after the threshold", "completed within 30k after it",
               "never completed: median tokens spent after it"], rows),
        "",
    ]

    # 4. matched game-levels
    mb_: dict[tuple[str, int], list[bool]] = defaultdict(list)
    mc_: dict[tuple[str, int], list[bool]] = defaultdict(list)
    for s in sb_:
        mb_[(s[0], s[2])].append(s[4])
    for s in sc_:
        mc_[(s[0], s[2])].append(s[4])
    common = sorted(set(mb_) & set(mc_))
    if common:
        cb = sum(sum(mb_[key]) for key in common)
        tb = sum(len(mb_[key]) for key in common)
        cc = sum(sum(mc_[key]) for key in common)
        tc = sum(len(mc_[key]) for key in common)
        lines += [
            f"## 4. The same game-levels, stuck past {k}k in both runs", "",
            f"{len(common)} game-levels. Baseline completed {cb} of {tb} attempts ({cb / tb:.0%}); "
            f"candidate {cc} of {tc} ({cc / tc:.0%}).", "",
        ]

    # 5. tokens
    def token_split(runs):
        total = sum(r.total_tokens for r in runs)
        stalled = sum(r.stalled_level.tokens for r in runs if r.stalled_level is not None)
        return total, stalled

    tb_, sb2 = token_split(base)
    tc_, sc2 = token_split(cand)
    lines += [
        "## 5. Generated tokens", "",
        table(["run", "total", "on the level each run ended stuck on", "everything else"], [
            ["baseline", f"{tb_ / 1e6:.2f}M", f"{sb2 / 1e6:.2f}M ({sb2 / tb_:.0%})", f"{(tb_ - sb2) / 1e6:.2f}M"],
            ["candidate", f"{tc_ / 1e6:.2f}M", f"{sc2 / 1e6:.2f}M ({sc2 / tc_:.0%})", f"{(tc_ - sc2) / 1e6:.2f}M"],
        ]),
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("baseline", type=Path)
    ap.add_argument("candidate", type=Path)
    ap.add_argument("--threshold", type=int, default=60000, help="tokens on a level that count as stuck")
    args = ap.parse_args(argv)
    _, base = load_runs(args.baseline)
    _, cand = load_runs(args.candidate)
    print(compare(base, cand, args.threshold))
    return 0


if __name__ == "__main__":
    sys.exit(main())
