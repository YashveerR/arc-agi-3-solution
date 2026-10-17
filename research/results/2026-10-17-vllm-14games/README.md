# lordhansolo's vLLM server, 14 games, Franzen's harness

**Run:** 2026-10-17 on Kaggle, 25 games × 2 passes.

**Configuration:** Franzen's notebook with:
- section 5 replaced by the [vLLM cell](../../vllm_server/README.md);
- 14 games at once;
- the sandbox guard on.

**Files:**
- `benchmark.json`;
- `report.md` and `levels.csv`, from `audit_run.py`.

The vLLM logs (`vllm-openai-server.log`, `vllm-watchdog.log`, `vllm-setup.log`) are still to be added.

## Start-up

- **The setup ran 1,546 s**, about 26 minutes. That's a cold read of the 168 GiB checkpoint; lordhansolo's logged run took about 8 minutes.
- **The notebook's 12-minute deadline released the games** while the server was still loading, and they waited on the 40-minute first-request grace as designed.
- **Play began 14.1 minutes into the benchmark,** against about 0 for the SGLang runs, whose server was ready before the benchmark started.
- **KV cache: 1,414,036 tokens,** against Franzen's 1,011,264. The smoke test passed.

## Result

**Judged against the criteria set before the run:**

| criterion | bar | result |
|---|---|---|
| KV cache | at least 1.3M tokens | **1,414,036**: pass |
| stable | no server restart, no failed model calls | pass. The longest pause between any two actions after play began was 47 s; a restart means a reload of many minutes. No game note reports failed model calls. |
| throughput | at least 10.5M generated tokens | **10.7M**: pass, despite 14 minutes less play |
| quality | score at least 44 | **48.71**: pass |

**The two passes** scored 45.38 and 52.03.

**Totals:** 221 levels completed, the most of any run. 14 of 50 games won.

## At equal hours of play

The vLLM run is shifted by its 14.1-minute late start. Each cell is mean score / generated tokens so far ([`time_curve.py`](../../time_curve.py)).

| hours of play | 10 g baseline | 10 g stuck review | 10 g cache | 10 g cache | 12 g cache + guard | **vLLM, 14 g** |
|---|---|---|---|---|---|---|
| 1 | 9.9 / 2.15M | 11.5 / 2.30M | 9.6 / 2.25M | 8.7 / 2.25M | 10.6 / 2.36M | **15.3 / 3.07M** |
| 2 | 25.6 / 4.31M | 27.5 / 4.49M | 25.6 / 4.46M | 24.7 / 4.40M | 29.6 / 4.63M | **31.8 / 5.98M** |
| 3 | 38.2 / 6.42M | 38.9 / 6.62M | 37.6 / 6.51M | 35.8 / 6.57M | 44.1 / 6.95M | **43.7 / 8.65M** |
| 3.83 | 45.6 / 8.28M | 44.6 / 8.33M | 46.5 / 8.42M | 42.9 / 8.38M | 50.7 / 8.85M | **48.7 / 10.57M** |

**Reading.**
- **Tokens: +27%** over the 10-game SGLang runs at equal play time, and +19% over 12 games on SGLang. This is the largest throughput gain of any change so far, and close to what lordhansolo's log suggested (+40% KV cache, +20% peak decode).
- **Score:** +3.8 over the mean of the four 10-game runs at equal play time (44.9). It is 2.0 below the 12-game SGLang run, whose 52.38 did not carry over to the hidden set (27.71).
- **No sign that the NVFP4/FP8 checkpoint plays worse.** It completed the most levels of any run. Median actions per completed level were 0.72× the human baseline, against 0.61–0.71 in the seven earlier runs; that is the top of the usual range, not outside it.
- **The score gain is smaller than the token gain suggests.** By the earlier rule of 2–3 points per 10% more tokens, +27% would be about +6. One run can't tell whether the checkpoint or the noise accounts for the difference.

## Next

**Submit this exact version,** once the memory check passes. A competition run lasts 9 hours, so RAM growth over the full 4-hour local run has to be checked first; the `[sys]` lines from the notebook log show it.

**The start-up costs about 26 of the competition's ~540 minutes,** about 5%. Warming the checkpoint before the server starts could cut that; it is the next change to test.
