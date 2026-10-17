# Run audit

Source: `research/results/2026-10-17-vllm-14games/benchmark.json` · label `duck-harness-kaggle` · 25 games × 2 passes = 50 runs

## 1. Score

- Mean score: **48.71** (recomputed from per-level actions: 48.71; 0 of 50 runs disagree with the reported score)
- One full pass over these 25 games scored between 45.38 and 52.03 (sd 4.70, i.e. ±10% of the mean).
- Passes needed per version to detect an improvement of +10%: ~15, +20%: ~4, +30%: ~2.

## 2. Where the points go

Every game is worth 100 points. On average a game's 100 points split like this:

|  | points | meaning |
|---|---|---|
| earned | 48.7 | the score |
| lost to inefficiency | 4.8 | levels completed, but with more actions than the human baseline |
| lost on the stalled level | 11.1 | the level the run was stuck on when it ended |
| lost on unreached levels | 37.6 | levels after the stalled one |
| bonus | 6.0 | beating the baseline (up to 115 per level) |

The official cap removed 3.77 points on average: a game can never score more than the weight of the levels it completed, so beating the human baseline only offsets slow levels and never makes up for unfinished ones.

If every level these runs completed had been done in exactly the human number of actions, the score would be about **51.3** instead of 48.7. Everything else that is missing comes from levels that were never completed.

## 3. Action efficiency on completed levels

221 completed levels; median actions used = **0.72×** the human baseline.

| actions vs human | levels | share | mean level score |
|---|---|---|---|
| at or under human (≤1×) | 175 | 79% | 114 |
| 1–2× | 36 | 16% | 60 |
| 2–4× | 9 | 4% | 16 |
| over 4× | 1 | 0% | 5 |

Completed levels contained 38 RESET actions in total (12% of completed levels had at least one).

## 4. By level number

A level counts as *attempted* if the run reached it.

| level | attempted | completed | median actions vs human | median k tokens to complete |
|---|---|---|---|---|
| 1 | 50 | 94% | 0.86 | 14.5 |
| 2 | 47 | 91% | 0.59 | 22.0 |
| 3 | 43 | 88% | 0.74 | 21.3 |
| 4 | 38 | 87% | 0.86 | 28.0 |
| 5 | 33 | 76% | 0.45 | 24.0 |
| 6 | 25 | 76% | 0.79 | 36.3 |
| 7 | 13 | 69% | 0.29 | 15.5 |
| 8 | 7 | 100% | 0.74 | 30.5 |
| 9 | 1 | 0% | n/a | n/a |

## 5. Where generated tokens go

10.7M generated tokens in total, 215k per run.

| spent on | tokens | share |
|---|---|---|
| levels that were completed | 6.8M | 64% |
| the stalled level (never converted to points) | 3.9M | 36% |

Of the stalled-level tokens, about **1.7M (16% of all tokens)** were spent after the run had already used more tokens on that level than 90% of successful completions of the same level number needed. That is the compute a smarter scheduler could most plausibly have moved to another game.

## 6. Per game

Means over passes. *Stall* = the level number the run was on when it ended (median over passes).

| game | score | levels | stall | actions vs human | lost: efficiency | lost: not completed | tokens on stalled level | tokens/run |
|---|---|---|---|---|---|---|---|---|
| ar25 | 100.0 | 8.0/8 | done | 0.49 | 0.0 | 0.0 | 0% | 143k |
| lp85 | 100.0 | 8.0/8 | done | 0.43 | 3.0 | 0.0 | 0% | 159k |
| tr87 | 100.0 | 6.0/6 | done | 0.59 | 0.0 | 0.0 | 0% | 114k |
| cd82 | 99.3 | 6.0/6 | done | 0.89 | 6.5 | 0.0 | 0% | 123k |
| vc33 | 96.5 | 7.0/7 | done | 0.78 | 13.5 | 0.0 | 0% | 258k |
| sb26 | 94.8 | 8.0/8 | done | 0.81 | 14.3 | 0.0 | 0% | 68k |
| ft09 | 73.8 | 5.0/6 | 5 | 0.58 | 2.7 | 26.2 | 58% | 123k |
| m0r0 | 71.4 | 5.0/6 | 6 | 0.51 | 1.6 | 28.6 | 19% | 273k |
| re86 | 58.3 | 6.0/8 | 7 | 0.55 | 0.0 | 41.7 | 39% | 263k |
| s5i5 | 57.1 | 6.0/8 | 7 | 0.66 | 4.9 | 41.7 | 44% | 457k |
| r11l | 52.4 | 3.5/6 | 2 | 0.52 | 5.5 | 47.6 | 35% | 170k |
| dc22 | 46.6 | 4.0/6 | 5 | 0.89 | 5.1 | 52.4 | 32% | 273k |
| tu93 | 45.8 | 6.5/9 | 8 | 0.91 | 13.5 | 43.3 | 33% | 400k |
| sc25 | 45.4 | 4.5/6 | 6 | 1.29 | 17.3 | 40.5 | 34% | 201k |
| ka59 | 37.0 | 5.0/7 | 6 | 1.15 | 19.2 | 46.4 | 33% | 238k |
| cn04 | 31.0 | 3.0/6 | 4 | 0.77 | 0.0 | 69.0 | 48% | 253k |
| sp80 | 31.0 | 3.0/6 | 4 | 0.54 | 0.0 | 69.0 | 34% | 300k |
| ls20 | 23.2 | 3.5/7 | 4 | 1.05 | 6.3 | 71.4 | 38% | 259k |
| tn36 | 20.1 | 3.0/7 | 4 | 0.81 | 3.1 | 76.8 | 40% | 211k |
| su15 | 13.3 | 3.0/9 | 4 | 0.75 | 0.0 | 86.7 | 59% | 173k |
| lf52 | 7.9 | 2.5/10 | 4 | 0.59 | 0.6 | 91.8 | 60% | 226k |
| bp35 | 5.3 | 2.0/9 | 3 | 1.26 | 2.5 | 92.2 | 51% | 262k |
| g50t | 5.1 | 1.0/7 | 2 | 0.81 | 0.8 | 94.6 | 69% | 186k |
| sk48 | 1.4 | 0.5/8 | 2 | 0.89 | 0.0 | 98.6 | 79% | 129k |
| wa30 | 1.1 | 0.5/9 | 2 | 0.41 | 0.0 | 98.9 | 94% | 106k |

## 7. Same game, different pass

Over the 25 games played more than once (2 passes each): mean **48.7**; if every game had got its best of those passes **56.1**; its worst 41.4. The gap between mean and best is score the agent is demonstrably capable of on these games but only reaches sometimes. (The best-of figure rises with the number of passes, so compare it only between runs with equal passes.)

8 of 25 games differ by two or more completed levels between passes:

| game | levels completed | score |
|---|---|---|
| bp35 | 1–3 of 9 | 1.2–9.4 |
| cn04 | 2–4 of 6 | 14.3–47.6 |
| ft09 | 4–6 of 6 | 47.6–100.0 |
| g50t | 0–2 of 7 | 0.0–10.1 |
| r11l | 1–6 of 6 | 4.8–100.0 |
| sp80 | 2–4 of 6 | 14.3–47.6 |
| tn36 | 2–4 of 7 | 4.5–35.7 |
| tu93 | 5–8 of 9 | 33.3–58.3 |

Never got past level 1 on any pass: sk48, wa30.

## 8. When does a level count as stuck?

Tokens a level took when it was completed: median 22k, 75th percentile 43k, 90th 71k. Tokens spent on the level a run ended stuck on: median 105k.

A level *crosses* a threshold when it uses more tokens than that without being completed yet. The completion rate after crossing is what any 'get unstuck' change must beat.

| threshold | levels that crossed it | of those, later completed | tokens spent past it on levels never completed |
|---|---|---|---|
| 40k | 97 | 63 (65%) | 2.54M (24%) |
| 60k | 64 | 31 (48%) | 1.87M (17%) |
| 80k | 42 | 13 (31%) | 1.24M (12%) |
| 100k | 25 | 6 (24%) | 0.75M (7%) |

## 9. Fresh starts

No fresh starts recorded: the fresh-start switch was off, or no level reached its threshold.

## 10. Stuck reviews

No stuck reviews recorded: the stuck-review switch was off.

