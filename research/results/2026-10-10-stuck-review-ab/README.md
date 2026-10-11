# Stuck review, A/B in one run: result

**Run:** 2026-10-10 on Kaggle. Franzen's published configuration plus the [stuck-review cell](../../stuck_review/README.md):
- `REVIEW_TOKENS = 40000`, `REVIEW_MAX = 2`;
- `AB_TEST = True`: each game had reviews on one pass and not on the other, and both passes logged their checkpoints.

25 public games × 2 passes.

**Files:** [audit report](report.md) (section 10 has the arm comparison), [levels.csv](levels.csv), `benchmark.json`.

## Verdict

No effect. Don't submit with it.

The rule set before the run asked for:
- at least 15 points more checkpoint levels completed in the arm with reviews;
- no drop in score.

| | with reviews | without |
|---|---|---|
| runs | 25 | 25 |
| mean score | 46.1 | 46.1 |
| levels that reached a 40k checkpoint | 41 | 37 |
| of those, later completed | 23 (56%) | 21 (57%) |

- The paired score difference by game is +0.04, with a standard error of 5.9.
- The completion difference is −1 point; Fisher p = 1.00.
- To pool to +15 points, a second run would have to show about +31. That is unlikely given this result, so the review is dropped rather than re-run.

**It fired as built.** There were 59 reviews on 41 levels in the arm with reviews, and 49 recorded checkpoints in the arm without. Every review fired between 40k and 52k tokens, or at 80k–91k for a second review.

**Not checked:** whether the model engaged with the note. No transcripts from this run were read. A flat result could mean the note was ignored, or that it was followed without helping.

## Two runs, two nulls

Neither the fresh start nor the stuck review moved the needle. Both tried to change how the model reasons about a stuck level through its context. Franzen reported the same for verification hints, notes and summaries. This model's handling of hard levels does not seem steerable by a note.

## Franzen's configuration, locally

This run's two arms scored the same. That makes three measurements of essentially the published configuration on the 25 public games:
- 47.2 (baseline run);
- 46.1 (each arm here).

Each 2-pass run has a spread of about ±12–14%.

## What more compute is worth

The table shows each run's score recomputed as if it had stopped earlier, using only the levels completed by then:

| stopped at | 1 h | 2 h | 2.5 h | 3 h | 3.5 h | 4.1 h (end) |
|---|---|---|---|---|---|---|
| baseline | 9.9 | 25.6 | 31.9 | 38.2 | 43.2 | 47.2 |
| fresh start run | 9.7 | 27.9 | 31.1 | 36.3 | 40.5 | 43.7 |
| this run | 11.5 | 27.5 | 32.7 | 38.9 | 43.5 | 46.1 |
| average | 10.4 | 27.0 | 31.9 | 37.8 | 42.4 | 45.7 |

**The score is still rising at the end.**
- The rise was about 7 points per hour over the last hour.
- It is flattening only slowly: 11.8/h, then 9.2/h, then 5.5/h over the last three intervals.
- Token output is constant at about 2.2M per hour all run.

**The estimate.** Each 10% more throughput is worth roughly 2–3 points (about 5% relative), and about +5 points for +20%. This is an estimate: a run with more time would also be scheduled differently, since the endgame rules key off the deadline.

**Why throughput is the next lever.** It can be measured directly, in tokens per hour, from a short run. That avoids the score noise that hides every prompt-level change.

**Where the throughput could come from.**
- **Idle and prefill time.** Franzen measured 837 tokens/s of server decode but 609 tokens/s reaching the games. Our runs match: 2.2M per hour is 611 tokens/s. The gap is prefill plus slots idling while a game runs its Python tool.
- **More parallel streams.** The server is capped at 10 parallel requests (`--max-running-requests 10`, CUDA graphs up to batch 10), and the harness admits 10 games.
