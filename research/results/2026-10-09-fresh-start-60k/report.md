# Run audit

Source: `research/results/2026-10-09-fresh-start-60k/benchmark.json` · label `duck-harness-kaggle` · 25 games × 2 passes = 50 runs

## 1. Score

- Mean score: **43.73** (recomputed from per-level actions: 43.73; 0 of 50 runs disagree with the reported score)
- One full pass over these 25 games scored between 41.24 and 46.21 (sd 3.52, i.e. ±8% of the mean).
- Passes needed per version to detect an improvement of +10%: ~11, +20%: ~3, +30%: ~2.

## 2. Where the points go

Every game is worth 100 points. On average a game's 100 points split like this:

|  | points | meaning |
|---|---|---|
| earned | 43.7 | the score |
| lost to inefficiency | 3.4 | levels completed, but with more actions than the human baseline |
| lost on the stalled level | 8.3 | the level the run was stuck on when it ended |
| lost on unreached levels | 46.5 | levels after the stalled one |
| bonus | 5.6 | beating the baseline (up to 115 per level) |

The official cap removed 3.67 points on average: a game can never score more than the weight of the levels it completed, so beating the human baseline only offsets slow levels and never makes up for unfinished ones.

If every level these runs completed had been done in exactly the human number of actions, the score would be about **45.2** instead of 43.7. Everything else that is missing comes from levels that were never completed.

## 3. Action efficiency on completed levels

192 completed levels; median actions used = **0.61×** the human baseline.

| actions vs human | levels | share | mean level score |
|---|---|---|---|
| at or under human (≤1×) | 164 | 85% | 114 |
| 1–2× | 23 | 12% | 60 |
| 2–4× | 5 | 3% | 17 |
| over 4× | 0 | 0% | n/a |

Completed levels contained 15 RESET actions in total (6% of completed levels had at least one).

## 4. By level number

A level counts as *attempted* if the run reached it.

| level | attempted | completed | median actions vs human | median k tokens to complete |
|---|---|---|---|---|
| 1 | 50 | 92% | 0.71 | 14.7 |
| 2 | 46 | 72% | 0.58 | 15.1 |
| 3 | 33 | 97% | 0.61 | 20.4 |
| 4 | 32 | 78% | 0.79 | 12.4 |
| 5 | 25 | 84% | 0.43 | 27.4 |
| 6 | 21 | 86% | 0.55 | 22.2 |
| 7 | 10 | 90% | 0.31 | 22.1 |
| 8 | 8 | 100% | 0.78 | 18.6 |
| 9 | 2 | 0% | n/a | n/a |

## 5. Where generated tokens go

9.4M generated tokens in total, 189k per run.

| spent on | tokens | share |
|---|---|---|
| levels that were completed | 5.5M | 58% |
| the stalled level (never converted to points) | 3.9M | 42% |

Of the stalled-level tokens, about **2.1M (22% of all tokens)** were spent after the run had already used more tokens on that level than 90% of successful completions of the same level number needed. That is the compute a smarter scheduler could most plausibly have moved to another game.

## 6. Per game

Means over passes. *Stall* = the level number the run was on when it ended (median over passes).

| game | score | levels | stall | actions vs human | lost: efficiency | lost: not completed | tokens on stalled level | tokens/run |
|---|---|---|---|---|---|---|---|---|
| ar25 | 100.0 | 8.0/8 | done | 0.47 | 0.0 | 0.0 | 0% | 136k |
| ft09 | 100.0 | 6.0/6 | done | 0.55 | 4.6 | 0.0 | 0% | 73k |
| lp85 | 100.0 | 8.0/8 | done | 0.55 | 3.7 | 0.0 | 0% | 205k |
| r11l | 100.0 | 6.0/6 | done | 0.45 | 0.0 | 0.0 | 0% | 155k |
| sb26 | 98.6 | 8.0/8 | done | 0.83 | 13.0 | 0.0 | 0% | 49k |
| cd82 | 91.9 | 6.0/6 | done | 0.77 | 17.7 | 0.0 | 0% | 103k |
| m0r0 | 83.5 | 5.5/6 | 6 | 0.41 | 11.8 | 14.3 | 0% | 303k |
| tu93 | 69.0 | 8.0/9 | 9 | 0.93 | 14.6 | 20.0 | 17% | 322k |
| vc33 | 60.6 | 5.0/7 | 4 | 0.63 | 3.0 | 39.3 | 45% | 191k |
| cn04 | 52.4 | 3.5/6 | 2 | 0.43 | 0.0 | 47.6 | 44% | 189k |
| tr87 | 47.6 | 4.0/6 | 5 | 0.62 | 0.0 | 52.4 | 60% | 157k |
| re86 | 41.7 | 5.0/8 | 6 | 0.61 | 0.0 | 58.3 | 69% | 248k |
| dc22 | 34.3 | 3.5/6 | 4 | 0.91 | 5.2 | 61.9 | 37% | 254k |
| s5i5 | 30.3 | 3.5/8 | 4 | 0.89 | 0.2 | 69.4 | 38% | 362k |
| sp80 | 26.2 | 2.5/6 | 4 | 0.29 | 0.0 | 73.8 | 63% | 342k |
| ka59 | 17.9 | 3.0/7 | 4 | 0.82 | 5.0 | 78.6 | 39% | 252k |
| sc25 | 10.4 | 1.5/6 | 2 | 1.33 | 3.9 | 85.7 | 57% | 80k |
| su15 | 7.8 | 2.0/9 | 3 | 0.57 | 0.0 | 92.2 | 76% | 158k |
| ls20 | 7.1 | 1.5/7 | 2 | 0.91 | 0.0 | 92.9 | 58% | 88k |
| lf52 | 6.4 | 2.0/10 | 3 | 0.55 | 0.0 | 93.6 | 35% | 228k |
| wa30 | 2.2 | 1.0/9 | 2 | 0.47 | 0.0 | 97.8 | 76% | 68k |
| tn36 | 2.1 | 1.0/7 | 2 | 1.64 | 1.5 | 96.4 | 73% | 205k |
| bp35 | 1.8 | 1.0/9 | 2 | 1.12 | 0.4 | 97.8 | 71% | 180k |
| sk48 | 1.4 | 0.5/8 | 2 | 0.85 | 0.0 | 98.6 | 73% | 222k |
| g50t | 0.0 | 0.0/7 | 1 | n/a | 0.0 | 100.0 | 100% | 145k |

## 7. Same game, different pass

Over the 25 games played more than once (2 passes each): mean **43.7**; if every game had got its best of those passes **51.8**; its worst 35.7. The gap between mean and best is score the agent is demonstrably capable of on these games but only reaches sometimes. (The best-of figure rises with the number of passes, so compare it only between runs with equal passes.)

7 of 25 games differ by two or more completed levels between passes:

| game | levels completed | score |
|---|---|---|
| cn04 | 1–6 of 6 | 4.8–100.0 |
| lf52 | 1–3 of 10 | 1.8–10.9 |
| s5i5 | 1–6 of 8 | 2.3–58.3 |
| sc25 | 0–3 of 6 | 0.0–20.8 |
| sp80 | 1–4 of 6 | 4.8–47.6 |
| su15 | 1–3 of 9 | 2.2–13.3 |
| vc33 | 3–7 of 7 | 21.1–100.0 |

Never got past level 1 on any pass: bp35, g50t, sk48, tn36, wa30.

## 8. When does a level count as stuck?

Tokens a level took when it was completed: median 18k, 75th percentile 33k, 90th 55k. Tokens spent on the level a run ended stuck on: median 129k.

A level *crosses* a threshold when it uses more tokens than that without being completed yet. The completion rate after crossing is what any 'get unstuck' change must beat.

| threshold | levels that crossed it | of those, later completed | tokens spent past it on levels never completed |
|---|---|---|---|
| 40k | 64 | 33 (52%) | 2.63M (28%) |
| 60k | 38 | 16 (42%) | 2.06M (22%) |
| 80k | 37 | 15 (41%) | 1.62M (17%) |
| 100k | 33 | 13 (39%) | 1.20M (13%) |

## 9. Fresh starts

38 fresh starts on 38 levels, in 28 of 50 runs. They fired after 60k–72k generated tokens on the level.

**16 of 38 restarted levels (42%) were later completed.**

For comparison, in the baseline run levels that went past 60k tokens without being completed were later completed 17 of 47 times (36%). That is the rate a fresh start has to beat.

| game | pass | level | fired at | completed later | actions vs human | level score | tokens on level (total) |
|---|---|---|---|---|---|---|---|
| bp35 | p0 | 2 | 62k | no |  |  | 82k |
| bp35 | p1 | 2 | 65k | no |  |  | 174k |
| cn04 | p1 | 2 | 61k | no |  |  | 165k |
| dc22 | p1 | 4 | 63k | yes | 1.48 | 46 | 171k |
| dc22 | p1 | 5 | 65k | no |  |  | 129k |
| g50t | p0 | 1 | 60k | no |  |  | 154k |
| g50t | p1 | 1 | 62k | no |  |  | 135k |
| ka59 | p0 | 3 | 62k | yes | 1.41 | 50 | 132k |
| ka59 | p1 | 4 | 67k | no |  |  | 146k |
| lf52 | p0 | 2 | 61k | no |  |  | 143k |
| lf52 | p1 | 2 | 61k | yes | 0.69 | 115 | 104k |
| lf52 | p1 | 3 | 62k | yes | 1.00 | 100 | 162k |
| lp85 | p0 | 6 | 60k | yes | 0.63 | 115 | 119k |
| m0r0 | p0 | 1 | 60k | yes | 1.33 | 56 | 88k |
| m0r0 | p0 | 2 | 62k | yes | 0.45 | 115 | 116k |
| m0r0 | p1 | 5 | 61k | yes | 0.16 | 115 | 128k |
| re86 | p0 | 6 | 71k | no |  |  | 202k |
| re86 | p1 | 6 | 71k | no |  |  | 142k |
| s5i5 | p0 | 2 | 66k | no |  |  | 138k |
| s5i5 | p1 | 2 | 64k | yes | 0.55 | 115 | 108k |
| s5i5 | p1 | 3 | 60k | yes | 0.70 | 115 | 113k |
| s5i5 | p1 | 4 | 64k | yes | 0.94 | 112 | 123k |
| s5i5 | p1 | 7 | 64k | no |  |  | 139k |
| sk48 | p0 | 1 | 67k | no |  |  | 142k |
| sk48 | p1 | 1 | 66k | yes | 0.85 | 115 | 122k |
| sk48 | p1 | 2 | 71k | no |  |  | 180k |
| sp80 | p0 | 2 | 60k | no |  |  | 190k |
| sp80 | p1 | 4 | 72k | yes | 0.29 | 115 | 152k |
| sp80 | p1 | 5 | 61k | no |  |  | 241k |
| su15 | p1 | 4 | 63k | no |  |  | 183k |
| tn36 | p0 | 2 | 62k | no |  |  | 121k |
| tn36 | p1 | 1 | 65k | yes | 2.53 | 16 | 94k |
| tn36 | p1 | 2 | 61k | no |  |  | 178k |
| tr87 | p1 | 5 | 61k | no |  |  | 129k |
| tu93 | p0 | 4 | 64k | yes | 1.14 | 77 | 76k |
| tu93 | p0 | 8 | 61k | yes | 2.22 | 20 | 156k |
| tu93 | p1 | 9 | 62k | no |  |  | 92k |
| vc33 | p0 | 4 | 62k | no |  |  | 172k |

