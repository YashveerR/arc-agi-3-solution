# Run audit

Source: `research/results/2026-10-10-stuck-review-ab/benchmark.json` · label `duck-harness-kaggle` · 25 games × 2 passes = 50 runs

## 1. Score

- Mean score: **46.09** (recomputed from per-level actions: 46.09; 0 of 50 runs disagree with the reported score)
- One full pass over these 25 games scored between 42.13 and 50.05 (sd 5.60, i.e. ±12% of the mean).
- Passes needed per version to detect an improvement of +10%: ~24, +20%: ~6, +30%: ~3.

## 2. Where the points go

Every game is worth 100 points. On average a game's 100 points split like this:

|  | points | meaning |
|---|---|---|
| earned | 46.1 | the score |
| lost to inefficiency | 3.9 | levels completed, but with more actions than the human baseline |
| lost on the stalled level | 10.8 | the level the run was stuck on when it ended |
| lost on unreached levels | 41.0 | levels after the stalled one |
| bonus | 5.7 | beating the baseline (up to 115 per level) |

The official cap removed 3.89 points on average: a game can never score more than the weight of the levels it completed, so beating the human baseline only offsets slow levels and never makes up for unfinished ones.

If every level these runs completed had been done in exactly the human number of actions, the score would be about **48.3** instead of 46.1. Everything else that is missing comes from levels that were never completed.

## 3. Action efficiency on completed levels

210 completed levels; median actions used = **0.64×** the human baseline.

| actions vs human | levels | share | mean level score |
|---|---|---|---|
| at or under human (≤1×) | 174 | 83% | 114 |
| 1–2× | 30 | 14% | 59 |
| 2–4× | 6 | 3% | 11 |
| over 4× | 0 | 0% | n/a |

Completed levels contained 25 RESET actions in total (9% of completed levels had at least one).

## 4. By level number

A level counts as *attempted* if the run reached it.

| level | attempted | completed | median actions vs human | median k tokens to complete |
|---|---|---|---|---|
| 1 | 50 | 94% | 0.69 | 15.4 |
| 2 | 47 | 81% | 0.57 | 20.1 |
| 3 | 38 | 92% | 0.63 | 22.4 |
| 4 | 35 | 91% | 0.83 | 21.0 |
| 5 | 32 | 72% | 0.37 | 28.9 |
| 6 | 23 | 78% | 0.57 | 21.8 |
| 7 | 12 | 75% | 0.35 | 13.3 |
| 8 | 8 | 100% | 0.83 | 11.3 |
| 9 | 2 | 0% | n/a | n/a |

## 5. Where generated tokens go

9.2M generated tokens in total, 183k per run.

| spent on | tokens | share |
|---|---|---|
| levels that were completed | 5.5M | 60% |
| the stalled level (never converted to points) | 3.7M | 40% |

Of the stalled-level tokens, about **1.7M (18% of all tokens)** were spent after the run had already used more tokens on that level than 90% of successful completions of the same level number needed. That is the compute a smarter scheduler could most plausibly have moved to another game.

## 6. Per game

Means over passes. *Stall* = the level number the run was on when it ended (median over passes).

| game | score | levels | stall | actions vs human | lost: efficiency | lost: not completed | tokens on stalled level | tokens/run |
|---|---|---|---|---|---|---|---|---|
| ar25 | 100.0 | 8.0/8 | done | 0.52 | 0.0 | 0.0 | 0% | 173k |
| ft09 | 100.0 | 6.0/6 | done | 0.58 | 4.9 | 0.0 | 0% | 106k |
| lp85 | 100.0 | 8.0/8 | done | 0.33 | 4.9 | 0.0 | 0% | 119k |
| sb26 | 100.0 | 8.0/8 | done | 0.81 | 1.3 | 0.0 | 0% | 49k |
| cd82 | 90.3 | 6.0/6 | done | 0.86 | 17.3 | 0.0 | 0% | 131k |
| vc33 | 84.7 | 6.5/7 | 7 | 0.67 | 8.8 | 12.5 | 16% | 210k |
| tu93 | 77.5 | 8.0/9 | 9 | 0.95 | 8.5 | 20.0 | 30% | 325k |
| m0r0 | 69.6 | 5.0/6 | 5 | 0.44 | 6.3 | 26.2 | 3% | 210k |
| s5i5 | 58.3 | 6.0/8 | 7 | 0.50 | 1.1 | 41.7 | 43% | 378k |
| cn04 | 52.4 | 3.5/6 | 2 | 0.55 | 0.0 | 47.6 | 35% | 156k |
| tr87 | 42.9 | 3.5/6 | 4 | 0.65 | 4.0 | 57.1 | 49% | 148k |
| re86 | 41.7 | 5.0/8 | 6 | 0.68 | 0.7 | 58.3 | 64% | 156k |
| sp80 | 38.1 | 3.5/6 | 4 | 0.26 | 0.5 | 61.9 | 49% | 285k |
| ls20 | 35.9 | 4.5/7 | 6 | 1.00 | 11.7 | 55.4 | 32% | 265k |
| sc25 | 35.9 | 4.0/6 | 5 | 0.98 | 11.8 | 52.4 | 49% | 184k |
| ka59 | 30.2 | 4.5/7 | 6 | 1.27 | 15.8 | 55.4 | 24% | 244k |
| g50t | 28.6 | 3.5/7 | 4 | 0.38 | 0.0 | 71.4 | 39% | 247k |
| r11l | 26.2 | 2.5/6 | 4 | 0.45 | 0.0 | 73.8 | 57% | 274k |
| dc22 | 14.3 | 2.0/6 | 3 | 0.64 | 0.0 | 85.7 | 67% | 161k |
| su15 | 12.2 | 2.5/9 | 4 | 0.65 | 0.8 | 87.8 | 59% | 180k |
| wa30 | 7.8 | 2.0/9 | 3 | 0.51 | 0.0 | 92.2 | 63% | 148k |
| bp35 | 2.1 | 1.0/9 | 2 | 1.00 | 0.1 | 97.8 | 70% | 155k |
| lf52 | 1.8 | 1.0/10 | 2 | 0.50 | 0.0 | 98.2 | 85% | 110k |
| tn36 | 1.8 | 0.5/7 | 2 | 0.34 | 0.0 | 98.2 | 92% | 90k |
| sk48 | 0.0 | 0.0/8 | 1 | n/a | 0.0 | 100.0 | 100% | 82k |

## 7. Same game, different pass

Over the 25 games played more than once (2 passes each): mean **46.1**; if every game had got its best of those passes **54.6**; its worst 37.6. The gap between mean and best is score the agent is demonstrably capable of on these games but only reaches sometimes. (The best-of figure rises with the number of passes, so compare it only between runs with equal passes.)

6 of 25 games differ by two or more completed levels between passes:

| game | levels completed | score |
|---|---|---|
| cn04 | 1–6 of 6 | 4.8–100.0 |
| m0r0 | 4–6 of 6 | 39.2–100.0 |
| r11l | 1–4 of 6 | 4.8–47.6 |
| su15 | 1–4 of 9 | 2.2–22.2 |
| tr87 | 2–5 of 6 | 14.3–71.4 |
| wa30 | 1–3 of 9 | 2.2–13.3 |

Never got past level 1 on any pass: bp35, lf52, sk48, tn36.

## 8. When does a level count as stuck?

Tokens a level took when it was completed: median 20k, 75th percentile 38k, 90th 58k. Tokens spent on the level a run ended stuck on: median 97k.

A level *crosses* a threshold when it uses more tokens than that without being completed yet. The completion rate after crossing is what any 'get unstuck' change must beat.

| threshold | levels that crossed it | of those, later completed | tokens spent past it on levels never completed |
|---|---|---|---|
| 40k | 80 | 46 (58%) | 2.23M (24%) |
| 60k | 52 | 18 (35%) | 1.55M (17%) |
| 80k | 33 | 3 (9%) | 0.90M (10%) |
| 100k | 19 | 2 (11%) | 0.43M (5%) |

## 9. Fresh starts

No fresh starts recorded: the fresh-start switch was off, or no level reached its threshold.

## 10. Stuck reviews

| arm | runs | mean score | levels that reached a checkpoint | of those, later completed | checkpoints in total |
|---|---|---|---|---|---|
| on: reviews sent | 25 | 46.1 | 41 | 23 (56%) | 59 |
| off: no reviews (checkpoints recorded only) | 25 | 46.1 | 37 | 21 (57%) | 49 |

Levels completed after reaching a checkpoint: 56% with reviews, 57% without (Fisher exact two-sided p = 1.00).
Score, paired by game over 25 games: with reviews minus without = **+0.04** (standard error 5.93).
Both arms ran in the same run, so they shared the GPU, the scheduler and the clock; pool several runs before drawing conclusions.

| game | pass | arm | level | checkpoints at | completed later | actions vs human | level score | tokens on level (total) |
|---|---|---|---|---|---|---|---|---|
| ar25 | p1 | on | 7 | 41k | yes | 0.22 | 115 | 59k |
| bp35 | p1 | on | 1 | 48k | yes | 1.05 | 91 | 58k |
| bp35 | p1 | on | 2 | 41k, 88k | no |  |  | 97k |
| cd82 | p0 | on | 1 | 43k | yes | 0.69 | 115 | 60k |
| cd82 | p0 | on | 5 | 40k | yes | 2.70 | 14 | 45k |
| cn04 | p1 | on | 2 | 42k | yes | 0.80 | 115 | 75k |
| dc22 | p1 | on | 3 | 43k, 82k | no |  |  | 110k |
| g50t | p1 | on | 1 | 44k | yes | 0.54 | 115 | 48k |
| g50t | p1 | on | 3 | 41k | yes | 0.42 | 115 | 42k |
| g50t | p1 | on | 4 | 41k, 81k | no |  |  | 83k |
| ka59 | p0 | on | 2 | 42k | yes | 0.79 | 115 | 56k |
| ka59 | p0 | on | 4 | 40k | yes | 1.49 | 45 | 41k |
| ka59 | p0 | on | 6 | 52k, 80k | no |  |  | 97k |
| lf52 | p0 | on | 2 | 42k, 81k | no |  |  | 107k |
| ls20 | p0 | on | 3 | 41k | yes | 1.96 | 26 | 74k |
| ls20 | p0 | on | 4 | 41k | yes | 0.75 | 115 | 43k |
| ls20 | p0 | on | 5 | 41k | no |  |  | 76k |
| m0r0 | p0 | on | 3 | 43k, 81k | yes | 0.48 | 115 | 88k |
| m0r0 | p0 | on | 4 | 41k | yes | 1.73 | 33 | 57k |
| r11l | p0 | on | 2 | 45k | yes | 0.45 | 115 | 55k |
| r11l | p0 | on | 3 | 45k, 81k | yes | 0.37 | 115 | 107k |
| r11l | p0 | on | 5 | 42k, 91k | no |  |  | 153k |
| re86 | p0 | on | 6 | 45k, 87k | no |  |  | 106k |
| s5i5 | p1 | on | 2 | 40k | yes | 0.37 | 115 | 44k |
| s5i5 | p1 | on | 3 | 40k | yes | 0.42 | 115 | 42k |
| s5i5 | p1 | on | 4 | 49k | yes | 1.00 | 100 | 68k |
| s5i5 | p1 | on | 6 | 50k | yes | 0.97 | 105 | 56k |
| s5i5 | p1 | on | 7 | 41k, 86k | no |  |  | 125k |
| sc25 | p0 | on | 5 | 41k, 80k | no |  |  | 107k |
| sk48 | p0 | on | 1 | 42k | no |  |  | 84k |
| sp80 | p1 | on | 2 | 41k | yes | 0.22 | 115 | 42k |
| sp80 | p1 | on | 4 | 42k, 81k | yes | 0.81 | 115 | 101k |
| sp80 | p1 | on | 5 | 43k, 86k | no |  |  | 134k |
| su15 | p1 | on | 2 | 44k, 83k | no |  |  | 86k |
| tn36 | p1 | on | 2 | 41k, 84k | no |  |  | 93k |
| tr87 | p0 | on | 3 | 44k, 80k | no |  |  | 109k |
| tu93 | p1 | on | 9 | 41k, 81k | no |  |  | 102k |
| vc33 | p0 | on | 4 | 40k | yes | 1.30 | 60 | 60k |
| vc33 | p0 | on | 5 | 41k | yes | 0.53 | 115 | 52k |
| vc33 | p0 | on | 7 | 42k | no |  |  | 68k |
| wa30 | p1 | on | 4 | 41k, 82k | no |  |  | 92k |
| ar25 | p0 | off | 7 | 41k | yes | 0.20 | 115 | 62k |
| bp35 | p0 | off | 2 | 41k, 80k | no |  |  | 121k |
| cn04 | p0 | off | 2 | 42k, 82k | no |  |  | 111k |
| dc22 | p0 | off | 3 | 41k, 85k | no |  |  | 104k |
| ft09 | p1 | off | 5 | 45k | yes | 1.31 | 58 | 78k |
| g50t | p0 | off | 1 | 40k | yes | 0.60 | 115 | 63k |
| g50t | p0 | off | 4 | 42k | yes | 0.17 | 115 | 74k |
| g50t | p0 | off | 5 | 43k, 84k | no |  |  | 111k |
| ka59 | p1 | off | 1 | 46k | yes | 2.68 | 14 | 71k |
| ka59 | p1 | off | 4 | 41k | yes | 1.29 | 60 | 54k |
| lf52 | p1 | off | 2 | 43k | no |  |  | 81k |
| ls20 | p1 | off | 1 | 42k | yes | 3.00 | 11 | 50k |
| ls20 | p1 | off | 2 | 40k | yes | 1.16 | 74 | 41k |
| ls20 | p1 | off | 6 | 41k, 81k | no |  |  | 91k |
| m0r0 | p1 | off | 3 | 44k | yes | 0.39 | 115 | 45k |
| m0r0 | p1 | off | 5 | 41k | yes | 0.14 | 115 | 59k |
| m0r0 | p1 | off | 6 | 42k | yes | 0.31 | 115 | 54k |
| r11l | p1 | off | 2 | 40k, 81k | no |  |  | 160k |
| re86 | p1 | off | 6 | 40k, 88k | no |  |  | 94k |
| s5i5 | p0 | off | 3 | 41k | yes | 0.44 | 115 | 48k |
| s5i5 | p0 | off | 7 | 42k, 81k | no |  |  | 198k |
| sc25 | p1 | off | 3 | 44k | yes | 2.69 | 14 | 62k |
| sc25 | p1 | off | 5 | 42k | no |  |  | 75k |
| sk48 | p1 | off | 1 | 40k | no |  |  | 80k |
| sp80 | p0 | off | 2 | 41k | yes | 0.26 | 115 | 44k |
| sp80 | p0 | off | 3 | 40k | yes | 1.04 | 92 | 54k |
| sp80 | p0 | off | 4 | 51k, 80k | no |  |  | 144k |
| su15 | p0 | off | 4 | 42k | yes | 0.38 | 115 | 64k |
| su15 | p0 | off | 5 | 50k, 83k | no |  |  | 127k |
| tn36 | p0 | off | 1 | 47k | no |  |  | 71k |
| tr87 | p1 | off | 1 | 44k | yes | 0.93 | 115 | 62k |
| tu93 | p0 | off | 5 | 45k | yes | 0.28 | 115 | 53k |
| tu93 | p0 | off | 6 | 41k | yes | 0.96 | 108 | 71k |
| tu93 | p0 | off | 8 | 41k | yes | 1.48 | 46 | 61k |
| tu93 | p0 | off | 9 | 41k, 83k | no |  |  | 95k |
| vc33 | p1 | off | 4 | 43k | yes | 1.18 | 72 | 61k |
| wa30 | p0 | off | 2 | 43k, 82k | no |  |  | 95k |

