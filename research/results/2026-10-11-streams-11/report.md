# Run audit

Source: `research/results/2026-10-11-streams-11/benchmark.json` · label `duck-harness-kaggle` · 25 games × 2 passes = 50 runs

## 1. Score

- Mean score: **46.06** (recomputed from per-level actions: 46.06; 0 of 50 runs disagree with the reported score)
- One full pass over these 25 games scored between 40.88 and 51.24 (sd 7.33, i.e. ±16% of the mean).
- Passes needed per version to detect an improvement of +10%: ~40, +20%: ~10, +30%: ~5.

## 2. Where the points go

Every game is worth 100 points. On average a game's 100 points split like this:

|  | points | meaning |
|---|---|---|
| earned | 46.1 | the score |
| lost to inefficiency | 3.8 | levels completed, but with more actions than the human baseline |
| lost on the stalled level | 10.1 | the level the run was stuck on when it ended |
| lost on unreached levels | 42.3 | levels after the stalled one |
| bonus | 5.8 | beating the baseline (up to 115 per level) |

The official cap removed 3.61 points on average: a game can never score more than the weight of the levels it completed, so beating the human baseline only offsets slow levels and never makes up for unfinished ones.

If every level these runs completed had been done in exactly the human number of actions, the score would be about **47.6** instead of 46.1. Everything else that is missing comes from levels that were never completed.

## 3. Action efficiency on completed levels

204 completed levels; median actions used = **0.71×** the human baseline.

| actions vs human | levels | share | mean level score |
|---|---|---|---|
| at or under human (≤1×) | 162 | 79% | 115 |
| 1–2× | 38 | 19% | 56 |
| 2–4× | 4 | 2% | 16 |
| over 4× | 0 | 0% | n/a |

Completed levels contained 17 RESET actions in total (7% of completed levels had at least one).

## 4. By level number

A level counts as *attempted* if the run reached it.

| level | attempted | completed | median actions vs human | median k tokens to complete |
|---|---|---|---|---|
| 1 | 50 | 92% | 0.79 | 13.4 |
| 2 | 46 | 83% | 0.67 | 22.7 |
| 3 | 38 | 89% | 0.79 | 23.7 |
| 4 | 34 | 85% | 0.79 | 16.1 |
| 5 | 29 | 79% | 0.55 | 22.8 |
| 6 | 23 | 70% | 0.44 | 22.9 |
| 7 | 10 | 90% | 0.36 | 12.0 |
| 8 | 8 | 100% | 0.81 | 22.9 |
| 9 | 2 | 50% | 0.29 | 95.3 |

## 5. Where generated tokens go

8.7M generated tokens in total, 174k per run.

| spent on | tokens | share |
|---|---|---|
| levels that were completed | 5.4M | 62% |
| the stalled level (never converted to points) | 3.3M | 38% |

Of the stalled-level tokens, about **1.3M (15% of all tokens)** were spent after the run had already used more tokens on that level than 90% of successful completions of the same level number needed. That is the compute a smarter scheduler could most plausibly have moved to another game.

## 6. Per game

Means over passes. *Stall* = the level number the run was on when it ended (median over passes).

| game | score | levels | stall | actions vs human | lost: efficiency | lost: not completed | tokens on stalled level | tokens/run |
|---|---|---|---|---|---|---|---|---|
| ar25 | 100.0 | 8.0/8 | done | 0.55 | 0.0 | 0.0 | 0% | 157k |
| r11l | 100.0 | 6.0/6 | done | 0.45 | 0.0 | 0.0 | 0% | 210k |
| lp85 | 99.7 | 8.0/8 | done | 0.49 | 5.7 | 0.0 | 0% | 120k |
| cd82 | 99.5 | 6.0/6 | done | 0.75 | 7.0 | 0.0 | 0% | 93k |
| sb26 | 94.1 | 8.0/8 | done | 0.83 | 16.7 | 0.0 | 0% | 64k |
| tu93 | 90.0 | 8.5/9 | 9 | 0.85 | 4.0 | 10.0 | 24% | 300k |
| m0r0 | 85.7 | 5.5/6 | 6 | 0.41 | 5.7 | 14.3 | 14% | 233k |
| ft09 | 73.8 | 5.0/6 | 5 | 0.65 | 5.7 | 26.2 | 35% | 141k |
| vc33 | 60.7 | 5.0/7 | 4 | 0.64 | 2.0 | 39.3 | 34% | 162k |
| ka59 | 50.3 | 5.5/7 | 6 | 1.21 | 17.5 | 35.7 | 16% | 268k |
| sc25 | 47.6 | 4.0/6 | 5 | 0.90 | 1.7 | 52.4 | 45% | 172k |
| ls20 | 42.4 | 5.0/7 | 6 | 1.03 | 14.4 | 46.4 | 30% | 297k |
| re86 | 41.7 | 5.0/8 | 6 | 0.68 | 1.9 | 58.3 | 52% | 182k |
| tr87 | 38.1 | 3.0/6 | 4 | 0.66 | 0.5 | 61.9 | 65% | 138k |
| dc22 | 38.1 | 3.5/6 | 4 | 0.82 | 2.7 | 61.9 | 41% | 263k |
| cn04 | 29.9 | 3.0/6 | 4 | 0.50 | 1.4 | 69.0 | 29% | 191k |
| sp80 | 26.2 | 2.5/6 | 4 | 0.38 | 0.0 | 73.8 | 60% | 237k |
| su15 | 13.3 | 3.0/9 | 4 | 0.57 | 0.0 | 86.7 | 65% | 165k |
| tn36 | 6.0 | 1.5/7 | 2 | 0.71 | 1.6 | 92.9 | 69% | 142k |
| s5i5 | 5.1 | 1.5/8 | 2 | 0.80 | 0.5 | 94.4 | 67% | 186k |
| lf52 | 3.2 | 1.5/10 | 2 | 0.31 | 0.6 | 96.4 | 65% | 127k |
| bp35 | 3.1 | 2.0/9 | 3 | 1.76 | 4.6 | 92.2 | 39% | 195k |
| g50t | 1.8 | 0.5/7 | 2 | 0.40 | 0.0 | 98.2 | 84% | 118k |
| wa30 | 1.1 | 0.5/9 | 2 | 0.65 | 0.0 | 98.9 | 84% | 105k |
| sk48 | 0.0 | 0.0/8 | 1 | n/a | 0.0 | 100.0 | 100% | 81k |

## 7. Same game, different pass

Over the 25 games played more than once (2 passes each): mean **46.1**; if every game had got its best of those passes **53.8**; its worst 38.3. The gap between mean and best is score the agent is demonstrably capable of on these games but only reaches sometimes. (The best-of figure rises with the number of passes, so compare it only between runs with equal passes.)

6 of 25 games differ by two or more completed levels between passes:

| game | levels completed | score |
|---|---|---|
| bp35 | 1–3 of 9 | 0.7–5.6 |
| cn04 | 2–4 of 6 | 12.3–47.6 |
| ft09 | 4–6 of 6 | 47.6–100.0 |
| sp80 | 1–4 of 6 | 4.8–47.6 |
| tr87 | 1–5 of 6 | 4.8–71.4 |
| vc33 | 3–7 of 7 | 21.4–100.0 |

Never got past level 1 on any pass: g50t, sk48, wa30.

## 8. When does a level count as stuck?

Tokens a level took when it was completed: median 21k, 75th percentile 38k, 90th 56k. Tokens spent on the level a run ended stuck on: median 94k.

A level *crosses* a threshold when it uses more tokens than that without being completed yet. The completion rate after crossing is what any 'get unstuck' change must beat.

| threshold | levels that crossed it | of those, later completed | tokens spent past it on levels never completed |
|---|---|---|---|
| 40k | 81 | 47 (58%) | 1.92M (22%) |
| 60k | 47 | 15 (32%) | 1.25M (14%) |
| 80k | 31 | 5 (16%) | 0.67M (8%) |
| 100k | 15 | 1 (7%) | 0.28M (3%) |

## 9. Fresh starts

No fresh starts recorded: the fresh-start switch was off, or no level reached its threshold.

## 10. Stuck reviews

No stuck reviews recorded: the stuck-review switch was off.

