# Fresh start at 60k: result

**Run:** 2026-10-09 on Kaggle. Franzen's published configuration plus the [fresh-start cell](../../fresh_start/README.md), with `FRESH_START_TOKENS = 60000` and `FRESH_START_MAX = 1`. 25 public games × 2 passes, the same setup as the [baseline](../2026-10-08-baseline/report.md).

**Files:** [audit report](report.md), [comparison with the baseline](comparison.md) (made with `research/compare_runs.py`), and the raw `benchmark.json`.

## Verdict

No measurable gain. Don't submit with it switched on.

## What the run shows

**The feature fired as built.**
- 38 fresh starts on 38 levels, in 28 of the 50 runs.
- Each fired between 60k and 72k tokens on the level: at the next turn after crossing 60k.
- Every level that passed 60k got exactly one fresh start.
- None fired after a game was won.

**The target metric moved slightly, within noise.**
- Of restarted levels, 42% were completed later (16 of 38). In the baseline, 36% of levels that passed 60k were completed later (17 of 47).
- Fisher exact p = 0.66. The 95% interval for the difference runs from −15 to +27 points.
- On the 18 game-levels that got stuck past 60k in both runs, the completion rate was 29% with fresh starts versus 22% without.
- The target of about 55%, which would have been a clear signal, was not reached.

**The mean score fell, also within noise.**
- 43.7 versus 47.2 for the baseline.
- Paired over games, the difference is −3.5 with a standard error of 5.0.
- The biggest swings were in games where the feature never fired:
  - sc25: −57
  - ls20: −28
  - r11l: +43
  - cd82: +35
- One run per arm can't separate a few points from noise.

## Two design problems

**1. It throws away attempts that were nearly solved.**
- In the baseline, the levels that passed 60k and still got completed mostly did so soon after: 11 of the 17 within 30k more tokens (median 21k).
- After a fresh start, completion took a median 60k more tokens, and only 2 came within 30k.
- Clearing the conversation discards real progress along with the wrong ideas. The restarted attempt then has to solve a hard level from scratch.

**2. It gave stuck games more compute.**
- The fresh start reset the level's token and action counters. Franzen's priority scheduler uses those same counters. Its priority for a game falls as tokens and actions pile up on the current level; at 60k tokens the token term has about halved.
- After the reset, a restarted game looked like it was on a new level and moved back up the queue.
- The level each run ended stuck on took 42% of all generated tokens, against 38% in the baseline.
- Levels that were never completed absorbed a median 84k tokens after the 60k mark, against 50k.
- Tokens on everything else were the same in both runs (5.5M). One run can't show whether this cost other games levels.

## How much it could ever be worth

- In the baseline, completing one of the stuck levels was worth about 13 points of its run's score.
- At the hoped-for 55%, the fresh start would complete about 7 more levels per 50 runs, about +1.8 points of mean score, plus whatever levels follow them.
- The observed +6 points of completion rate is worth about +0.6.
- Effects that size can't be confirmed with one or two runs per arm.

## If it is revisited

1. Keep the scheduler's counters running through a fresh start, so a restarted attempt only gets compute the scheduler would otherwise give a stuck level. Track the trigger with a separate counter.
2. Raise the threshold so that fewer nearly-solved attempts are thrown away. In the baseline, only 10% of levels past 100k were completed later, compared with 36% past 60k.

Both changes reduce the feature's reach as well as its cost. Expect a small effect either way.
