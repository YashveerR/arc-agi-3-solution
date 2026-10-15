# Run audit

Source: `research/results/2026-10-14-hicache-12games-guard/benchmark.json` · label `duck-harness-kaggle` · 25 games × 2 passes = 50 runs

## 1. Score

- Mean score: **52.38** (recomputed from per-level actions: 52.38; 0 of 50 runs disagree with the reported score)
- One full pass over these 25 games scored between 51.49 and 53.27 (sd 1.26, i.e. ±2% of the mean).
- Passes needed per version to detect an improvement of +10%: ~1, +20%: ~1, +30%: ~1.

## 2. Where the points go

Every game is worth 100 points. On average a game's 100 points split like this:

|  | points | meaning |
|---|---|---|
| earned | 52.4 | the score |
| lost to inefficiency | 3.3 | levels completed, but with more actions than the human baseline |
| lost on the stalled level | 8.1 | the level the run was stuck on when it ended |
| lost on unreached levels | 38.2 | levels after the stalled one |
| bonus | 6.7 | beating the baseline (up to 115 per level) |

The official cap removed 4.69 points on average: a game can never score more than the weight of the levels it completed, so beating the human baseline only offsets slow levels and never makes up for unfinished ones.

If every level these runs completed had been done in exactly the human number of actions, the score would be about **53.7** instead of 52.4. Everything else that is missing comes from levels that were never completed.

## 3. Action efficiency on completed levels

219 completed levels; median actions used = **0.66×** the human baseline.

| actions vs human | levels | share | mean level score |
|---|---|---|---|
| at or under human (≤1×) | 180 | 82% | 115 |
| 1–2× | 37 | 17% | 63 |
| 2–4× | 2 | 1% | 20 |
| over 4× | 0 | 0% | n/a |

Completed levels contained 22 RESET actions in total (9% of completed levels had at least one).

## 4. By level number

A level counts as *attempted* if the run reached it.

| level | attempted | completed | median actions vs human | median k tokens to complete |
|---|---|---|---|---|
| 1 | 50 | 98% | 0.77 | 15.7 |
| 2 | 49 | 78% | 0.65 | 17.6 |
| 3 | 38 | 84% | 0.72 | 20.2 |
| 4 | 32 | 100% | 0.78 | 19.5 |
| 5 | 32 | 84% | 0.55 | 22.4 |
| 6 | 27 | 81% | 0.63 | 33.2 |
| 7 | 12 | 83% | 0.33 | 17.9 |
| 8 | 8 | 100% | 0.78 | 10.8 |
| 9 | 2 | 50% | 0.56 | 91.5 |

## 5. Where generated tokens go

9.6M generated tokens in total, 191k per run.

| spent on | tokens | share |
|---|---|---|
| levels that were completed | 6.1M | 64% |
| the stalled level (never converted to points) | 3.5M | 36% |

Of the stalled-level tokens, about **1.5M (16% of all tokens)** were spent after the run had already used more tokens on that level than 90% of successful completions of the same level number needed. That is the compute a smarter scheduler could most plausibly have moved to another game.

## 6. Per game

Means over passes. *Stall* = the level number the run was on when it ended (median over passes).

| game | score | levels | stall | actions vs human | lost: efficiency | lost: not completed | tokens on stalled level | tokens/run |
|---|---|---|---|---|---|---|---|---|
| ar25 | 100.0 | 8.0/8 | done | 0.48 | 0.0 | 0.0 | 0% | 136k |
| cd82 | 100.0 | 6.0/6 | done | 0.84 | 4.3 | 0.0 | 0% | 120k |
| ft09 | 100.0 | 6.0/6 | done | 0.65 | 5.0 | 0.0 | 0% | 147k |
| lp85 | 100.0 | 8.0/8 | done | 0.35 | 2.0 | 0.0 | 0% | 148k |
| r11l | 100.0 | 6.0/6 | done | 0.61 | 2.8 | 0.0 | 0% | 223k |
| sb26 | 100.0 | 8.0/8 | done | 0.79 | 3.3 | 0.0 | 0% | 34k |
| tr87 | 100.0 | 6.0/6 | done | 0.63 | 5.9 | 0.0 | 0% | 118k |
| vc33 | 100.0 | 7.0/7 | done | 0.60 | 1.6 | 0.0 | 0% | 171k |
| tu93 | 88.9 | 8.5/9 | 9 | 0.79 | 8.4 | 10.0 | 28% | 319k |
| sc25 | 79.5 | 5.5/6 | 6 | 0.70 | 10.8 | 14.3 | 17% | 199k |
| cn04 | 59.5 | 4.5/6 | 6 | 0.44 | 0.3 | 40.5 | 31% | 251k |
| ka59 | 59.4 | 5.5/7 | 6 | 0.94 | 10.0 | 35.7 | 20% | 267k |
| m0r0 | 57.1 | 4.0/6 | 3 | 0.45 | 0.5 | 42.9 | 31% | 182k |
| re86 | 50.0 | 5.5/8 | 6 | 0.58 | 2.5 | 50.0 | 48% | 225k |
| dc22 | 42.1 | 4.0/6 | 5 | 0.90 | 8.2 | 52.4 | 31% | 288k |
| su15 | 22.2 | 4.0/9 | 5 | 0.51 | 0.0 | 77.8 | 55% | 256k |
| ls20 | 17.2 | 3.0/7 | 4 | 1.23 | 11.9 | 71.4 | 44% | 223k |
| g50t | 10.7 | 2.0/7 | 3 | 0.86 | 0.7 | 89.3 | 35% | 239k |
| s5i5 | 5.6 | 1.5/8 | 2 | 0.75 | 0.0 | 94.4 | 82% | 242k |
| sp80 | 4.8 | 1.0/6 | 2 | 0.26 | 0.0 | 95.2 | 92% | 153k |
| sk48 | 4.0 | 1.5/8 | 2 | 1.74 | 2.0 | 94.4 | 52% | 207k |
| bp35 | 3.2 | 1.5/9 | 2 | 1.17 | 1.3 | 95.6 | 58% | 234k |
| tn36 | 2.3 | 1.0/7 | 2 | 1.36 | 1.2 | 96.4 | 72% | 156k |
| lf52 | 1.8 | 1.0/10 | 2 | 0.38 | 0.0 | 98.2 | 88% | 111k |
| wa30 | 1.1 | 0.5/9 | 2 | 0.69 | 0.0 | 98.9 | 90% | 128k |

## 7. Same game, different pass

Over the 25 games played more than once (2 passes each): mean **52.4**; if every game had got its best of those passes **57.1**; its worst 47.6. The gap between mean and best is score the agent is demonstrably capable of on these games but only reaches sometimes. (The best-of figure rises with the number of passes, so compare it only between runs with equal passes.)

2 of 25 games differ by two or more completed levels between passes:

| game | levels completed | score |
|---|---|---|
| ls20 | 1–5 of 7 | 2.1–32.4 |
| m0r0 | 2–6 of 6 | 14.3–100.0 |

Never got past level 1 on any pass: lf52, sp80, tn36, wa30.

## 8. When does a level count as stuck?

Tokens a level took when it was completed: median 19k, 75th percentile 38k, 90th 66k. Tokens spent on the level a run ended stuck on: median 110k.

A level *crosses* a threshold when it uses more tokens than that without being completed yet. The completion rate after crossing is what any 'get unstuck' change must beat.

| threshold | levels that crossed it | of those, later completed | tokens spent past it on levels never completed |
|---|---|---|---|
| 40k | 78 | 49 (63%) | 2.30M (24%) |
| 60k | 56 | 28 (50%) | 1.72M (18%) |
| 80k | 35 | 10 (29%) | 1.18M (12%) |
| 100k | 23 | 2 (9%) | 0.72M (7%) |

## 9. Fresh starts

No fresh starts recorded: the fresh-start switch was off, or no level reached its threshold.

## 10. Stuck reviews

No stuck reviews recorded: the stuck-review switch was off.

