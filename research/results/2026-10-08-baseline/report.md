# Run audit

Source: `benchmark.json` from Kaggle notebook version run 2026-10-08 21:26 → 2026-10-09 01:32 (unmodified Franzen configuration) · label `duck-harness-kaggle` · 25 games × 2 passes = 50 runs

## 1. Score

- Mean score: **47.19** (recomputed from per-level actions: 47.19; 0 of 50 runs disagree with the reported score)
- One full pass over these 25 games scored between 42.59 and 51.79 (sd 6.51, i.e. ±14% of the mean).
- Passes needed per version to detect an improvement of +10%: ~30, +20%: ~8, +30%: ~4.

## 2. Where the points go

Every game is worth 100 points. On average a game's 100 points split like this:

|  | points | meaning |
|---|---|---|
| earned | 47.2 | the score |
| lost to inefficiency | 3.7 | levels completed, but with more actions than the human baseline |
| lost on the stalled level | 9.1 | the level the run was stuck on when it ended |
| lost on unreached levels | 41.8 | levels after the stalled one |
| bonus | 5.9 | beating the baseline (up to 115 per level) |

The official cap removed 4.11 points on average: a game can never score more than the weight of the levels it completed, so beating the human baseline only offsets slow levels and never makes up for unfinished ones.

If every level these runs completed had been done in exactly the human number of actions, the score would be about **49.1** instead of 47.2. Everything else that is missing comes from levels that were never completed.

## 3. Action efficiency on completed levels

208 completed levels; median actions used = **0.67×** the human baseline.

| actions vs human | levels | share | mean level score |
|---|---|---|---|
| at or under human (≤1×) | 170 | 82% | 115 |
| 1–2× | 31 | 15% | 64 |
| 2–4× | 7 | 3% | 17 |
| over 4× | 0 | 0% | n/a |

Completed levels contained 26 RESET actions in total (9% of completed levels had at least one).

## 4. By level number

A level counts as *attempted* if the run reached it.

| level | attempted | completed | median actions vs human | median k tokens to complete |
|---|---|---|---|---|
| 1 | 50 | 96% | 0.69 | 13.9 |
| 2 | 48 | 77% | 0.58 | 19.8 |
| 3 | 37 | 89% | 0.68 | 20.0 |
| 4 | 33 | 88% | 0.78 | 23.0 |
| 5 | 29 | 83% | 0.54 | 29.5 |
| 6 | 24 | 75% | 0.60 | 22.0 |
| 7 | 11 | 91% | 0.42 | 15.3 |
| 8 | 8 | 100% | 0.99 | 18.5 |
| 9 | 2 | 50% | 0.30 | 55.0 |

## 5. Where generated tokens go

8.9M generated tokens in total, 179k per run.

| spent on | tokens | share |
|---|---|---|
| levels that were completed | 5.5M | 62% |
| the stalled level (never converted to points) | 3.4M | 38% |

Of the stalled-level tokens, about **1.6M (17% of all tokens)** were spent after the run had already used more tokens on that level than 90% of successful completions of the same level number needed. That is the compute a smarter scheduler could most plausibly have moved to another game.

## 6. Per game

Means over passes. *Stall* = the level number the run was on when it ended (median over passes).

| game | score | levels | stall | actions vs human | lost: efficiency | lost: not completed | tokens on stalled level | tokens/run |
|---|---|---|---|---|---|---|---|---|
| ar25 | 100.0 | 8.0/8 | done | 0.44 | 0.0 | 0.0 | 0% | 115k |
| lp85 | 100.0 | 8.0/8 | done | 0.54 | 0.0 | 0.0 | 0% | 126k |
| tr87 | 99.1 | 6.0/6 | done | 0.73 | 5.9 | 0.0 | 0% | 95k |
| sb26 | 94.7 | 8.0/8 | done | 0.81 | 16.2 | 0.0 | 0% | 87k |
| tu93 | 77.8 | 8.5/9 | 9 | 1.02 | 18.0 | 10.0 | 19% | 330k |
| cn04 | 73.8 | 5.0/6 | 5 | 0.40 | 0.5 | 26.2 | 30% | 241k |
| ft09 | 73.8 | 5.0/6 | 5 | 0.58 | 0.0 | 26.2 | 47% | 99k |
| sc25 | 67.2 | 5.0/6 | 6 | 0.83 | 8.0 | 28.6 | 29% | 205k |
| vc33 | 60.6 | 5.0/7 | 4 | 0.67 | 2.5 | 39.3 | 35% | 170k |
| r11l | 57.1 | 4.0/6 | 3 | 0.57 | 1.9 | 42.9 | 19% | 272k |
| cd82 | 56.7 | 4.0/6 | 3 | 0.78 | 1.5 | 42.9 | 34% | 163k |
| m0r0 | 52.4 | 3.5/6 | 2 | 0.43 | 2.4 | 47.6 | 28% | 201k |
| tn36 | 45.9 | 4.0/7 | 2 | 0.89 | 9.4 | 48.2 | 31% | 198k |
| re86 | 41.7 | 5.0/8 | 6 | 0.71 | 0.8 | 58.3 | 50% | 179k |
| ls20 | 34.9 | 3.0/7 | 4 | 0.64 | 5.8 | 62.5 | 45% | 182k |
| dc22 | 29.3 | 3.0/6 | 4 | 0.80 | 2.8 | 69.0 | 46% | 229k |
| g50t | 26.8 | 2.5/7 | 4 | 0.53 | 0.0 | 73.2 | 30% | 229k |
| sp80 | 26.2 | 2.5/6 | 4 | 0.28 | 0.0 | 73.8 | 63% | 181k |
| ka59 | 23.6 | 4.0/7 | 5 | 1.10 | 15.5 | 62.5 | 24% | 182k |
| su15 | 17.8 | 3.5/9 | 4 | 0.71 | 0.1 | 82.2 | 58% | 208k |
| s5i5 | 12.5 | 2.5/8 | 4 | 0.51 | 0.0 | 87.5 | 66% | 257k |
| wa30 | 2.2 | 1.0/9 | 2 | 0.59 | 0.0 | 97.8 | 80% | 120k |
| sk48 | 2.1 | 1.0/8 | 2 | 0.84 | 0.7 | 97.2 | 61% | 132k |
| bp35 | 1.8 | 1.0/9 | 2 | 1.12 | 0.4 | 97.8 | 73% | 168k |
| lf52 | 1.8 | 1.0/10 | 2 | 0.44 | 0.0 | 98.2 | 86% | 102k |

## 7. Same game, different pass

Over the 25 games played more than once (2 passes each): mean **47.2**; if every game had got its best of those passes **63.4**; its worst 31.0. The gap between mean and best is score the agent is demonstrably capable of on these games but only reaches sometimes. (The best-of figure rises with the number of passes, so compare it only between runs with equal passes.)

12 of 25 games differ by two or more completed levels between passes:

| game | levels completed | score |
|---|---|---|
| cd82 | 2–6 of 6 | 13.3–100.0 |
| cn04 | 4–6 of 6 | 47.6–100.0 |
| dc22 | 2–4 of 6 | 14.3–44.3 |
| ft09 | 4–6 of 6 | 47.6–100.0 |
| g50t | 0–5 of 7 | 0.0–53.6 |
| ka59 | 3–5 of 7 | 13.2–34.0 |
| ls20 | 0–6 of 7 | 0.0–69.9 |
| m0r0 | 1–6 of 6 | 4.8–100.0 |
| r11l | 2–6 of 6 | 14.3–100.0 |
| sp80 | 1–4 of 6 | 4.8–47.6 |
| tn36 | 1–7 of 7 | 3.6–88.1 |
| vc33 | 3–7 of 7 | 21.1–100.0 |

Never got past level 1 on any pass: bp35, lf52, sk48, wa30.

## 8. When does a level count as stuck?

Tokens a level took when it was completed: median 19k, 75th percentile 37k, 90th 55k. Tokens spent on the level a run ended stuck on: median 103k.

A level *crosses* a threshold when it uses more tokens than that without being completed yet. The completion rate after crossing is what any 'get unstuck' change must beat.

| threshold | levels that crossed it | of those, later completed | tokens spent past it on levels never completed |
|---|---|---|---|
| 40k | 78 | 47 (60%) | 2.10M (24%) |
| 60k | 47 | 17 (36%) | 1.49M (17%) |
| 80k | 35 | 9 (26%) | 0.93M (10%) |
| 100k | 21 | 2 (10%) | 0.46M (5%) |

