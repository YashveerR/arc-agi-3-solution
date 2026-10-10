# Run comparison

## 1. Score

Baseline mean **47.19** (50 runs), candidate mean **43.73** (50 runs).
Paired over 25 games: difference **-3.46** (standard error 4.96, so roughly -13.4 to +6.5).

| game | baseline | candidate | difference | levels (baseline) | levels (candidate) | intervention fired |
|---|---|---|---|---|---|---|
| sc25 | 67.2 | 10.4 | -56.8 | 5, 5 | 0, 3 |  |
| tr87 | 99.1 | 47.6 | -51.5 | 6, 6 | 4, 4 | fresh start |
| tn36 | 45.9 | 2.1 | -43.8 | 7, 1 | 1, 1 | fresh start |
| ls20 | 34.9 | 7.1 | -27.8 | 0, 6 | 1, 2 |  |
| g50t | 26.8 | 0.0 | -26.8 | 0, 5 | 0, 0 | fresh start |
| cn04 | 73.8 | 52.4 | -21.4 | 4, 6 | 6, 1 | fresh start |
| su15 | 17.8 | 7.8 | -10.0 | 4, 3 | 1, 3 | fresh start |
| tu93 | 77.8 | 69.0 | -8.8 | 9, 8 | 8, 8 | fresh start |
| ka59 | 23.6 | 17.9 | -5.7 | 3, 5 | 3, 3 | fresh start |
| sk48 | 2.1 | 1.4 | -0.7 | 1, 1 | 0, 1 | fresh start |
| ar25 | 100.0 | 100.0 | +0.0 | 8, 8 | 8, 8 |  |
| bp35 | 1.8 | 1.8 | +0.0 | 1, 1 | 1, 1 | fresh start |
| lp85 | 100.0 | 100.0 | +0.0 | 8, 8 | 8, 8 | fresh start |
| re86 | 41.7 | 41.7 | +0.0 | 5, 5 | 5, 5 | fresh start |
| sp80 | 26.2 | 26.2 | +0.0 | 1, 4 | 1, 4 | fresh start |
| vc33 | 60.6 | 60.6 | +0.0 | 3, 7 | 3, 7 | fresh start |
| wa30 | 2.2 | 2.2 | +0.0 | 1, 1 | 1, 1 |  |
| sb26 | 94.7 | 98.6 | +4.0 | 8, 8 | 8, 8 |  |
| lf52 | 1.8 | 6.4 | +4.5 | 1, 1 | 1, 3 | fresh start |
| dc22 | 29.3 | 34.3 | +5.0 | 2, 4 | 3, 4 | fresh start |
| s5i5 | 12.5 | 30.3 | +17.8 | 2, 3 | 1, 6 | fresh start |
| ft09 | 73.8 | 100.0 | +26.2 | 4, 6 | 6, 6 |  |
| m0r0 | 52.4 | 83.5 | +31.1 | 1, 6 | 6, 5 | fresh start |
| cd82 | 56.7 | 91.9 | +35.2 | 6, 2 | 6, 6 |  |
| r11l | 57.1 | 100.0 | +42.9 | 6, 2 | 6, 6 |  |

## 2. Levels stuck past 60k tokens

Baseline: 17 of 47 completed later (36%). Candidate: 16 of 38 (42%).
Difference +6% (95% interval about -15% to +27%); Fisher exact two-sided p = 0.66.

## 3. What happened after 60k

| run | completed later: median tokens after the threshold | completed within 30k after it | never completed: median tokens spent after it |
|---|---|---|---|
| baseline | 21k | 11 | 50k |
| candidate | 60k | 2 | 84k |

## 4. The same game-levels, stuck past 60k in both runs

18 game-levels. Baseline completed 5 of 23 attempts (22%); candidate 7 of 24 (29%).

## 5. Generated tokens

| run | total | on the level each run ended stuck on | everything else |
|---|---|---|---|
| baseline | 8.94M | 3.41M (38%) | 5.53M |
| candidate | 9.43M | 3.93M (42%) | 5.49M |

