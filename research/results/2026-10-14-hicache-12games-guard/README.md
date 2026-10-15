# 12 games with the RAM cache and the sandbox guard (run 3)

**Run:** 2026-10-14 on Kaggle, 4.07 hours, 25 games × 2 passes.

**Configuration:** Franzen's notebook plus:
- the 32 GB [RAM cache](../../hicache/README.md);
- 12 games at once (server `MAXREQ=12`, `CUDAGRAPH_MAXBS=12`, `MAMBA_CACHE=68`);
- the [sandbox out-of-memory guard](../../sandbox_guard/README.md).

The server log confirms the settings: `max_running_requests: 12`, `hicache_size: 32`, `max_mamba_cache_size: 68`.

**Files:**
- `benchmark.json`, `serve.log.gz`;
- `report.md` and `levels.csv`, from `audit_run.py`;
- `serve-summary.md`, from `serve_stats.py`.

## Result: the best local run so far

**Score 52.38.** The four comparable 10-game runs of Franzen's harness scored 44.45–47.66 (mean 46.35, sd 1.43).

| | 12 games + cache + guard | 10-game runs |
|---|---|---|
| score | **52.38** | 47.19, 46.09, 47.66, 44.45 |
| levels completed | **219** | 204–211 |
| games won (all levels) | **19** of 50 | 11–16 |
| generated tokens | 9.56M | 8.94–9.43M (mean 9.19M) |
| requests generating (mean) | 10.50 of 12 | 8.85–8.94 of 10 |
| mean decode tokens/s | 723 | 678–682 |
| large re-processed prompts | 11.3M tokens | 8.6–9.3M |
| retractions (server pausing a request because the cache is full) | 2 | 0–1 |

## Judged against the criteria set before the run ([run 3](../../hicache/run3.md))

1. **Survives: pass.** The server was still decoding in the run's last second. There is no `exit code -9` and no failed model calls.
2. **Tokens at least 9.7M: missed.**
   - 9.56M is +4.0% over the 10-game mean, against the +6% the bar asked for.
   - The server's own decode figure is up 6.5%. The two measures don't match exactly.
3. **Score in the usual range or above: pass, far above.**
   - 52.38 is 6.0 points over the 10-game mean.
   - Treating the four 10-game runs as the spread of one run, the chance of a score this high by luck is about 3% (t = 3.8, 3 degrees of freedom).
   - The paired per-game comparison is noisier. Against the 10-12 run it gives +4.7 with a standard error of 3.9, because single games swing a lot between passes. Most of the gain is four games (m0r0, cd82, vc33, r11l) that had one bad pass before and two good ones here. Three games went the other way (sp80, s5i5, ls20).
4. **Guard lines:** the guard was on (`kernel accepted oom_score_adj=1000` at start-up) and **never fired**. No snippet ran away in this run, so it neither confirms nor rules out runaway snippets as run 2's cause.

## Over time

Mean score / levels completed / generated tokens so far, at each checkpoint ([`time_curve.py`](../../time_curve.py)):

| hours | 10 g baseline (10-08) | 10 g stuck review (10-10) | 10 g cache (10-12) | 10 g cache (10-13) | 12 g crashed (10-13) | **12 g guard (10-14)** |
|---|---|---|---|---|---|---|
| 1.0 | 9.9 / 72 / 2.15M | 11.5 / 82 / 2.30M | 9.6 / 75 / 2.25M | 8.7 / 65 / 2.25M | 9.5 / 76 / 2.42M | 10.6 / 80 / 2.36M |
| 2.0 | 25.6 / 141 / 4.31M | 27.5 / 145 / 4.49M | 25.6 / 140 / 4.46M | 24.7 / 133 / 4.40M | **30.3** / 146 / 4.71M | **29.6** / 149 / 4.63M |
| 3.0 | 38.2 / 182 / 6.42M | 38.9 / 184 / 6.62M | 37.6 / 179 / 6.51M | 35.8 / 171 / 6.57M | crashed | **44.1** / 192 / 6.95M |
| 4.0 | 47.2 / 208 / 8.62M | 46.1 / 210 / 8.71M | 47.1 / 209 / 8.84M | 44.4 / 204 / 8.73M | crashed | **52.1** / 218 / 9.23M |

Both 12-game runs were about 4 points ahead at two hours (30.3 and 29.6, against 24.7–27.5). They are independent runs, so the lead is unlikely to be one lucky draw.

**The gain is larger than tokens alone predict.** Earlier runs suggested about 2–3 points per +10% tokens, so +4% should give about 1 point. The rest is either luck or a second effect of more games running at once: two more games make progress at any moment, and a game stuck on a hard level blocks a smaller share of the GPU. This run can't tell those apart.

**Best estimate:** a real gain of a few points locally, size uncertain (roughly +1 to +7). A hidden-set submission is the next test.

## Memory (from the notebook's `[sys]` lines)

The lines are in [`notebook-sys-lines.txt`](notebook-sys-lines.txt). "Harness" is the notebook process; "server" is everything else, nearly all of it the model server.

| hours into the run | RAM in use (of 176.9 GiB) | harness | server and rest |
|---|---|---|---|
| 0.0 | 136.5 | 0.3 | 136.2 |
| 0.5 | 146.9 | 1.0 | 145.9 |
| 1.0 | 145.9 | 1.6 | 144.3 |
| 2.0 | 147.0 | 2.6 | 144.4 |
| 3.0 | 148.4 | 3.4 | 145.0 |
| 4.0 | 149.6 | 4.2 | 145.4 |

**Peak:** 151.9 at 3.9 hours, leaving 25 GB free.

**Reading.**
- **The server ramps up by about 10 GB in its first half hour, then stays flat** at about 145.
- **The harness grows steadily,** about 0.8 GB an hour.
- **Total growth after the first hour:** about 1.1 GB an hour.
- **The crashed run fits this pattern.** Its rise from 136.5 to 148.4 was the same first-hour ramp, not a steady 5.7 GB an hour. It then lost its server with about 28 GB free, so something sudden took the memory.

**For a 9-hour competition run:**
- Total use should reach about 155 GB. The harness could take a few GB more, since all 110 games are live.
- Spikes like this run's 2–3 GB peak would take that to around 160. That leaves about 15 GB of margin.
- This passes the check set before submitting:
  - at halfway, 148.2;
  - at the end, 148.7;
  - under 155, and less than 5 higher than halfway.
