# Submission log

One submission per day. Each score is one run on the public half of the hidden games. Configurations alternate so that the averages can be compared. Pick the final submissions by average, not by the best single score.

| date | configuration | public score | rank after |
|---|---|---|---|
| 2026-10-0? | Franzen's notebook, unchanged | 26.52 | |
| 2026-10-11 | Franzen's notebook, unchanged | 29.29 | 561 |
| 2026-10-13 | Franzen + 32 GB system-RAM cache, 10 games (neutral; a stability check) | 28.48 | |
| 2026-10-15 | 12 games + 32 GB RAM cache + sandbox guard (best local run, 52.38) | 27.71 | |
| 2026-10-17 | lordhansolo's vLLM server and NVFP4/FP8 checkpoint, 14 games, Franzen's harness (local 48.71) | **23.35** | |
| 2026-10-19 | 12 games + 32 GB RAM cache + sandbox guard (resubmission of the 27.71 version) | 27.38 | |
| 2026-10-21 | 10 games + 32 GB RAM cache + sandbox guard: the 12-game version set back to `MAXREQ=10`, `ACTIVE_STREAMS=10` | **29.47** | |

**The 2026-10-21 entry** is the 12-game notebook with only `MAXREQ` and `ACTIVE_STREAMS` changed back to 10. So `CUDAGRAPH_MAXBS=12` and `MAMBA_CACHE=68` are presumably still set. CUDA graphs up to 12 still cover 10 requests, and the larger Mamba cache only reserves a little more memory. The guard changes no request. So this counts as the 10-game RAM-cache configuration, the same as the 28.48 entry.

**Reference: Franzen's own scores** for the same notebook were 27.89 (his Milestone 2 entry) and 31.06 (his best).

**Franzen-level configurations so far (2026-10-21):**
- Eight scores: 26.52, 27.38, 27.71, 27.89, 28.48, 29.29, 29.47 and 31.06.
- Mean 28.5, standard deviation 1.4.
- 29.47 is our best score. It is 1.1 above the mean of the seven before it, under one standard deviation (z = 0.8). It shows stability, not a gain.
- The 12-game local gain (+6 points) did not show on the hidden set (27.71, 27.38).

**The vLLM stack scored 23.35,** 3.6 standard deviations below the Franzen-setup mean. That's close to lordhansolo's own 23.84 on the same stack. Local runs over-predicted it, as they did for 12 games.

**12 games against 10 (updated 2026-10-21):**
- **12 games:** 27.71 and 27.38, mean 27.55.
- **10 games, ours:** 26.52, 29.29, 28.48 and 29.47, mean 28.44. That's −0.9 for 12 games (standard error 1.0).
- **10 games, with Franzen's two:** six scores, mean 28.79. That's −1.2 for 12 games (standard error 1.2).
- **Reading:** still no proof, but every comparison now leans toward 10 games. 10 games also use less memory. Keep 10 as the default.

**Final picks (as of 2026-10-21): 29.47 and 29.29.** Both are 10-game submissions of the stable setup, and they are our two highest public scores. The public and private halves come from the same run, so a crash or a slow start would hurt both. Which games go well is independent between the halves, so the higher public score is only a slightly better bet.
