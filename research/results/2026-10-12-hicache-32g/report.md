# Run audit

Source: `research/results/2026-10-12-hicache-32g/benchmark.json` · label `duck-harness-kaggle` · 25 games × 2 passes = 50 runs

## 1. Score

- Mean score: **47.66** (recomputed from per-level actions: 47.66; 0 of 50 runs disagree with the reported score)
- One full pass over these 25 games scored between 42.85 and 52.48 (sd 6.81, i.e. ±14% of the mean).
- Passes needed per version to detect an improvement of +10%: ~33, +20%: ~9, +30%: ~4.

## 2. Where the points go

Every game is worth 100 points. On average a game's 100 points split like this:

|  | points | meaning |
|---|---|---|
| earned | 47.7 | the score |
| lost to inefficiency | 3.0 | levels completed, but with more actions than the human baseline |
| lost on the stalled level | 9.8 | the level the run was stuck on when it ended |
| lost on unreached levels | 41.4 | levels after the stalled one |
| bonus | 6.0 | beating the baseline (up to 115 per level) |

The official cap removed 4.12 points on average: a game can never score more than the weight of the levels it completed, so beating the human baseline only offsets slow levels and never makes up for unfinished ones.

If every level these runs completed had been done in exactly the human number of actions, the score would be about **48.8** instead of 47.7. Everything else that is missing comes from levels that were never completed.

## 3. Action efficiency on completed levels

211 completed levels; median actions used = **0.70×** the human baseline.

| actions vs human | levels | share | mean level score |
|---|---|---|---|
| at or under human (≤1×) | 178 | 84% | 114 |
| 1–2× | 29 | 14% | 63 |
| 2–4× | 4 | 2% | 12 |
| over 4× | 0 | 0% | n/a |

Completed levels contained 21 RESET actions in total (9% of completed levels had at least one).

## 4. By level number

A level counts as *attempted* if the run reached it.

| level | attempted | completed | median actions vs human | median k tokens to complete |
|---|---|---|---|---|
| 1 | 50 | 94% | 0.79 | 14.3 |
| 2 | 47 | 87% | 0.78 | 24.7 |
| 3 | 41 | 88% | 0.78 | 22.5 |
| 4 | 36 | 78% | 0.73 | 28.1 |
| 5 | 28 | 79% | 0.47 | 23.2 |
| 6 | 22 | 91% | 0.55 | 26.6 |
| 7 | 13 | 69% | 0.34 | 12.5 |
| 8 | 8 | 88% | 0.73 | 10.3 |
| 9 | 1 | 100% | 0.26 | 66.1 |

## 5. Where generated tokens go

9.3M generated tokens in total, 185k per run.

| spent on | tokens | share |
|---|---|---|
| levels that were completed | 6.0M | 65% |
| the stalled level (never converted to points) | 3.2M | 35% |

Of the stalled-level tokens, about **1.3M (14% of all tokens)** were spent after the run had already used more tokens on that level than 90% of successful completions of the same level number needed. That is the compute a smarter scheduler could most plausibly have moved to another game.

## 6. Per game

Means over passes. *Stall* = the level number the run was on when it ended (median over passes).

| game | score | levels | stall | actions vs human | lost: efficiency | lost: not completed | tokens on stalled level | tokens/run |
|---|---|---|---|---|---|---|---|---|
| ar25 | 100.0 | 8.0/8 | done | 0.54 | 0.0 | 0.0 | 0% | 160k |
| lp85 | 100.0 | 8.0/8 | done | 0.42 | 6.7 | 0.0 | 0% | 185k |
| sb26 | 100.0 | 8.0/8 | done | 0.81 | 0.2 | 0.0 | 0% | 49k |
| tr87 | 100.0 | 6.0/6 | done | 0.62 | 0.0 | 0.0 | 0% | 137k |
| ft09 | 98.1 | 6.0/6 | done | 0.58 | 13.7 | 0.0 | 0% | 112k |
| sc25 | 83.5 | 5.5/6 | 6 | 0.83 | 7.2 | 14.3 | 18% | 182k |
| tu93 | 78.3 | 8.0/9 | 8 | 0.83 | 8.5 | 18.9 | 20% | 250k |
| r11l | 64.3 | 4.5/6 | 4 | 0.41 | 0.0 | 35.7 | 4% | 160k |
| vc33 | 60.7 | 5.0/7 | 4 | 0.69 | 0.8 | 39.3 | 29% | 195k |
| cd82 | 58.9 | 4.5/6 | 4 | 0.80 | 10.1 | 35.7 | 32% | 195k |
| ka59 | 58.6 | 5.5/7 | 6 | 0.93 | 10.8 | 35.7 | 28% | 305k |
| re86 | 58.3 | 6.0/8 | 7 | 0.65 | 0.0 | 41.7 | 35% | 201k |
| cn04 | 47.6 | 4.0/6 | 5 | 0.52 | 0.0 | 52.4 | 41% | 245k |
| sp80 | 35.5 | 3.5/6 | 4 | 0.49 | 5.1 | 61.9 | 32% | 292k |
| ls20 | 34.5 | 4.0/7 | 5 | 0.83 | 3.5 | 64.3 | 36% | 234k |
| s5i5 | 33.3 | 4.0/8 | 5 | 0.58 | 0.0 | 66.7 | 57% | 299k |
| dc22 | 31.0 | 3.0/6 | 4 | 0.73 | 0.4 | 69.0 | 49% | 239k |
| su15 | 13.0 | 3.0/9 | 4 | 0.86 | 0.9 | 86.7 | 59% | 178k |
| g50t | 10.7 | 2.0/7 | 3 | 0.51 | 0.0 | 89.3 | 7% | 147k |
| m0r0 | 7.1 | 1.0/6 | 2 | 0.60 | 0.0 | 92.9 | 84% | 129k |
| bp35 | 6.7 | 2.0/9 | 3 | 1.04 | 1.1 | 92.2 | 50% | 258k |
| tn36 | 6.7 | 1.5/7 | 2 | 1.00 | 4.3 | 89.3 | 55% | 135k |
| wa30 | 2.2 | 1.0/9 | 2 | 0.75 | 0.0 | 97.8 | 77% | 106k |
| lf52 | 1.8 | 1.0/10 | 2 | 0.42 | 0.0 | 98.2 | 85% | 96k |
| sk48 | 0.7 | 0.5/8 | 2 | 1.43 | 0.7 | 98.6 | 68% | 139k |

## 7. Same game, different pass

Over the 25 games played more than once (2 passes each): mean **47.7**; if every game had got its best of those passes **56.5**; its worst 38.8. The gap between mean and best is score the agent is demonstrably capable of on these games but only reaches sometimes. (The best-of figure rises with the number of passes, so compare it only between runs with equal passes.)

9 of 25 games differ by two or more completed levels between passes:

| game | levels completed | score |
|---|---|---|
| bp35 | 1–3 of 9 | 2.2–11.2 |
| cd82 | 3–6 of 6 | 28.3–89.5 |
| dc22 | 2–4 of 6 | 14.3–47.6 |
| m0r0 | 0–2 of 6 | 0.0–14.3 |
| r11l | 3–6 of 6 | 28.6–100.0 |
| s5i5 | 2–6 of 8 | 8.3–58.3 |
| tn36 | 0–3 of 7 | 0.0–13.3 |
| tu93 | 7–9 of 9 | 62.2–94.4 |
| vc33 | 3–7 of 7 | 21.4–100.0 |

Never got past level 1 on any pass: lf52, sk48, wa30.

## 8. When does a level count as stuck?

Tokens a level took when it was completed: median 21k, 75th percentile 38k, 90th 63k. Tokens spent on the level a run ended stuck on: median 94k.

A level *crosses* a threshold when it uses more tokens than that without being completed yet. The completion rate after crossing is what any 'get unstuck' change must beat.

| threshold | levels that crossed it | of those, later completed | tokens spent past it on levels never completed |
|---|---|---|---|
| 40k | 80 | 49 (61%) | 1.96M (21%) |
| 60k | 57 | 26 (46%) | 1.34M (14%) |
| 80k | 32 | 10 (31%) | 0.78M (8%) |
| 100k | 20 | 4 (20%) | 0.40M (4%) |

## 9. Fresh starts

No fresh starts recorded: the fresh-start switch was off, or no level reached its threshold.

## 10. Stuck reviews

No stuck reviews recorded: the stuck-review switch was off.

