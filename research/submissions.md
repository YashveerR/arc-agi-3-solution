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

**Reference: Franzen's own scores** for the same notebook were 27.89 (his Milestone 2 entry) and 31.06 (his best).

**Franzen-level configurations so far:**
- Six scores: 26.52, 27.71, 27.89, 28.48, 29.29 and 31.06.
- Mean 28.5, standard deviation about 1.6.
- The 28.48 entry includes the RAM cache, which is neutral at 10 games.
- The 27.71 entry is 12 games. Its local gain (+6 points) did not show on the hidden set. If the true gain were +3 there, a score this low would be about a 1-in-100 draw. A gain of about 1 point is still plausible.

**The vLLM stack scored 23.35,** 3.3 standard deviations below the Franzen-setup mean. That's close to lordhansolo's own 23.84 on the same stack. Local runs over-predicted it, as they did for 12 games.

**12 games against 10 (2026-10-20):**
- **12 games:** 27.71 and 27.38, mean 27.55.
- **Our 10-game submissions:** 26.52, 29.29 and 28.48, mean 28.10.
- **Difference:** -0.55, with a standard error of about 1.5. There's no sign that 12 games help on the hidden set. 10 games use less memory, so they're the safer default.
