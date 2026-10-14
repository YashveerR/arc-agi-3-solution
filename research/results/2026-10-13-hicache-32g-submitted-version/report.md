# Run audit

Source: `research/results/2026-10-13-hicache-32g-submitted-version/benchmark.json` · 25 games × 2 passes = 50 runs

## 1. Score

- Mean score: **44.45** (recomputed from per-level actions: 44.45; 0 of 50 runs disagree with the reported score)
- One full pass over these 25 games scored between 41.69 and 47.20 (sd 3.90, i.e. ±9% of the mean).
- Passes needed per version to detect an improvement of +10%: ~13, +20%: ~4, +30%: ~2.

## 2. Where the points go

Every game is worth 100 points. On average a game's 100 points split like this:

|  | points | meaning |
|---|---|---|
| earned | 44.4 | the score |
| lost to inefficiency | 4.6 | levels completed, but with more actions than the human baseline |
| lost on the stalled level | 11.8 | the level the run was stuck on when it ended |
| lost on unreached levels | 41.1 | levels after the stalled one |
| bonus | 5.4 | beating the baseline (up to 115 per level) |

The official cap removed 3.35 points on average: a game can never score more than the weight of the levels it completed, so beating the human baseline only offsets slow levels and never makes up for unfinished ones.

If every level these runs completed had been done in exactly the human number of actions, the score would be about **47.1** instead of 44.4. Everything else that is missing comes from levels that were never completed.

## 3. Action efficiency on completed levels

204 completed levels; median actions used = **0.65×** the human baseline.

| actions vs human | levels | share | mean level score |
|---|---|---|---|
| at or under human (≤1×) | 159 | 78% | 114 |
| 1–2× | 34 | 17% | 64 |
| 2–4× | 9 | 4% | 15 |
| over 4× | 2 | 1% | 5 |

Completed levels contained 22 RESET actions in total (7% of completed levels had at least one).

## 4. By level number

A level counts as *attempted* if the run reached it.

| level | attempted | completed | median actions vs human | median k tokens to complete |
|---|---|---|---|---|
| 1 | 50 | 92% | 0.72 | 13.1 |
| 2 | 46 | 85% | 0.62 | 26.7 |
| 3 | 39 | 87% | 0.66 | 18.7 |
| 4 | 34 | 94% | 0.79 | 18.3 |
| 5 | 32 | 69% | 0.51 | 29.5 |
| 6 | 22 | 73% | 0.76 | 30.9 |
| 7 | 11 | 82% | 0.32 | 16.2 |
| 8 | 8 | 75% | 1.19 | 25.7 |
| 9 | 1 | 0% | n/a | n/a |

## 5. Where generated tokens go

9.2M generated tokens in total, 183k per run.

| spent on | tokens | share |
|---|---|---|
| levels that were completed | 5.5M | 61% |
| the stalled level (never converted to points) | 3.6M | 39% |

Of the stalled-level tokens, about **1.7M (18% of all tokens)** were spent after the run had already used more tokens on that level than 90% of successful completions of the same level number needed. That is the compute a smarter scheduler could most plausibly have moved to another game.

## 6. Per game

Means over passes. *Stall* = the level number the run was on when it ended (median over passes).

| game | score | levels | stall | actions vs human | lost: efficiency | lost: not completed | tokens on stalled level | tokens/run |
|---|---|---|---|---|---|---|---|---|
| ar25 | 100.0 | 8.0/8 | done | 0.56 | 0.0 | 0.0 | 0% | 155k |
| cd82 | 95.3 | 6.0/6 | done | 0.89 | 12.0 | 0.0 | 0% | 114k |
| sb26 | 94.0 | 8.0/8 | done | 0.81 | 17.1 | 0.0 | 0% | 68k |
| r11l | 85.7 | 5.5/6 | 6 | 0.46 | 0.0 | 14.3 | 26% | 334k |
| tr87 | 85.7 | 5.5/6 | 6 | 0.72 | 0.0 | 14.3 | 22% | 128k |
| lp85 | 84.3 | 7.5/8 | 8 | 0.35 | 9.0 | 11.1 | 11% | 221k |
| ft09 | 73.8 | 5.0/6 | 5 | 0.60 | 2.7 | 26.2 | 53% | 111k |
| tu93 | 61.2 | 7.5/9 | 8 | 0.95 | 14.8 | 28.9 | 25% | 350k |
| vc33 | 60.6 | 5.0/7 | 4 | 0.60 | 2.2 | 39.3 | 26% | 187k |
| ka59 | 53.1 | 5.0/7 | 6 | 0.76 | 4.7 | 46.4 | 44% | 236k |
| re86 | 50.0 | 5.5/8 | 6 | 0.58 | 0.0 | 50.0 | 39% | 195k |
| cn04 | 47.6 | 4.0/6 | 5 | 0.45 | 2.6 | 52.4 | 28% | 203k |
| dc22 | 47.6 | 4.0/6 | 5 | 0.92 | 2.4 | 52.4 | 39% | 271k |
| m0r0 | 41.7 | 3.5/6 | 4 | 0.44 | 4.1 | 57.1 | 16% | 207k |
| sc25 | 32.9 | 4.0/6 | 5 | 1.31 | 16.1 | 52.4 | 46% | 185k |
| sp80 | 26.2 | 2.5/6 | 4 | 0.24 | 0.0 | 73.8 | 62% | 185k |
| ls20 | 23.0 | 3.0/7 | 4 | 0.78 | 1.9 | 76.8 | 38% | 185k |
| tn36 | 18.5 | 3.5/7 | 4 | 1.38 | 21.5 | 60.7 | 29% | 213k |
| wa30 | 9.4 | 2.5/9 | 4 | 0.59 | 3.9 | 87.8 | 37% | 152k |
| su15 | 7.8 | 2.0/9 | 3 | 0.80 | 0.3 | 92.2 | 69% | 135k |
| s5i5 | 5.6 | 1.5/8 | 2 | 0.90 | 0.2 | 94.4 | 79% | 184k |
| lf52 | 5.5 | 2.0/10 | 3 | 0.44 | 0.0 | 94.5 | 76% | 163k |
| bp35 | 1.7 | 1.0/9 | 2 | 1.14 | 0.5 | 97.8 | 71% | 190k |
| g50t | 0.0 | 0.0/7 | 1 | n/a | 0.0 | 100.0 | 100% | 109k |
| sk48 | 0.0 | 0.0/8 | 1 | n/a | 0.0 | 100.0 | 100% | 103k |

## 7. Same game, different pass

Over the 25 games played more than once (2 passes each): mean **44.4**; if every game had got its best of those passes **53.6**; its worst 35.3. The gap between mean and best is score the agent is demonstrably capable of on these games but only reaches sometimes. (The best-of figure rises with the number of passes, so compare it only between runs with equal passes.)

8 of 25 games differ by two or more completed levels between passes:

| game | levels completed | score |
|---|---|---|
| ft09 | 4–6 of 6 | 47.6–100.0 |
| ls20 | 2–4 of 7 | 10.7–35.2 |
| m0r0 | 2–5 of 6 | 12.0–71.4 |
| sp80 | 1–4 of 6 | 4.8–47.6 |
| su15 | 1–3 of 9 | 2.2–13.3 |
| tn36 | 1–6 of 7 | 1.1–36.0 |
| vc33 | 3–7 of 7 | 21.1–100.0 |
| wa30 | 1–4 of 9 | 2.2–16.5 |

Never got past level 1 on any pass: bp35, g50t, sk48.

## 8. When does a level count as stuck?

Tokens a level took when it was completed: median 19k, 75th percentile 37k, 90th 57k. Tokens spent on the level a run ended stuck on: median 97k.

A level *crosses* a threshold when it uses more tokens than that without being completed yet. The completion rate after crossing is what any 'get unstuck' change must beat.

| threshold | levels that crossed it | of those, later completed | tokens spent past it on levels never completed |
|---|---|---|---|
| 40k | 82 | 48 (59%) | 2.14M (23%) |
| 60k | 50 | 19 (38%) | 1.48M (16%) |
| 80k | 33 | 7 (21%) | 0.91M (10%) |
| 100k | 18 | 2 (11%) | 0.45M (5%) |

## 9. Fresh starts

No fresh starts recorded: the fresh-start switch was off, or no level reached its threshold.

## 10. Stuck reviews

No stuck reviews recorded: the stuck-review switch was off.

