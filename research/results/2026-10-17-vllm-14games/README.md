# lordhansolo's vLLM server, 14 games, Franzen's harness

**Run:** 2026-10-17 on Kaggle, 25 games × 2 passes.

**Configuration:** Franzen's notebook with:
- section 5 replaced by the [vLLM cell](../../vllm_server/README.md);
- 14 games at once;
- the sandbox guard on.

**Files:**
- `benchmark.json`;
- `report.md` and `levels.csv`, from `audit_run.py`;
- `vllm-openai-server.log.gz`, `vllm-setup.log` and `vllm-watchdog.log`;
- `notebook-sys-lines.txt`: the RAM monitor and section-5 lines from the notebook log.

## Start-up

- **The setup ran 1,546 s**, about 26 minutes. lordhansolo's logged run took about 8 minutes. Both slow parts are reads from Kaggle's input storage:
  - **runtime unpack:** 382 s, against 135 s in his run;
  - **weight load:** about 17 minutes from the first kernel line to the KV-cache line (14:01:51 to 14:18:50), against about 5.4 minutes in his run.
- **The notebook's 12-minute deadline released the games** while the server was still loading, and they waited on the 40-minute first-request grace as designed.
- **Play began 14.1 minutes into the benchmark,** against about 0 for the SGLang runs, whose server was ready before the benchmark started.
- **KV cache: 1,414,036 tokens,** against Franzen's 1,011,264. The smoke test passed.

## Result

**Judged against the criteria set before the run:**

| criterion | bar | result |
|---|---|---|
| KV cache | at least 1.3M tokens | **1,414,036**: pass |
| stable | no server restart, no failed model calls | pass. The watchdog log has only the first start (`restart 0`). The longest pause between any two actions after play began was 47 s. No game note reports failed model calls. |
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

## Server

From `vllm-openai-server.log` ([`serve_stats.py`](../../serve_stats.py)):

| | vLLM, 14 games | SGLang, 10 games (10-13) | SGLang, 12 games (10-14) |
|---|---|---|---|
| requests generating (mean) | 12.19 of 14 | 8.89 of 10 | 10.50 of 12 |
| mean generation tokens/s | **777** | 678 | 723 |
| at every slot busy | 884 | 783 | 837 |
| KV used, mean / max | 0.71 / 1.00 | 0.66 / 0.96 | 0.81 / 1.00 |
| prompt tokens processed (not cached) | **38.1M** | 20.7M | 25.2M |
| preemptions / retractions | 0 | 1 | 2 |

- **Gaps in decode statistics.** The vLLM numbers start once the server is up. Requests generating fall from 13.7 in the first half hour to 8.9 in the last, as games finish.
- **Prompt re-processing.** vLLM processes about 1.5 to 1.8 times as many prompt tokens from scratch as SGLang did, despite a prefix-cache hit rate of about 91%. That is prefill time not spent decoding, and a possible lever: the 2,048-token prefill chunk, the 128-token cache unit, and 14 games on one cache.
- **MTP draft acceptance:** 2.70 tokens per step on average (the first and last 3 draft tokens included).

## Memory (from the `[sys]` lines)

| hours of serving | RAM in use (of 176.9 GiB) | harness | server and rest |
|---|---|---|---|
| 0.0 | 141.6 | 0.3 | 141.3 |
| 0.5 | 147.1 | 1.1 | 146.0 |
| 1.1 | 148.3 | 2.0 | 146.3 |
| 2.1 | 150.2 | 3.3 | 146.9 |
| 3.2 | 151.2 | 4.3 | 146.9 |
| 3.8 | 152.9 | 5.0 | 147.9 |

- **The same pattern as SGLang:** the server settles at about 147 within the first hour, and the harness grows about 1 GB an hour.
- **One spike:** 156.2 at 4,209 s, about 9 GB above its neighbours for one sample. That is most likely a Python snippet; the guard would take it first if RAM ran out.
- **The pre-submission check passes:** halfway 150.2, last 152.9 (under 155, and less than 5 higher).
- **A 9-hour competition run** projects to about 157 GB, plus spikes.

## Next

**Submit this exact version:** the memory check passes.

**Then, in order:**
1. **Start-up** costs about 26 of the competition's ~540 minutes, about 5%. Both slow parts are storage reads, and lordhansolo measured parallel reads of the same storage at 4 to 6 times the speed of a single stream. Reading the runtime blobs and weight shards in parallel threads from the start of the notebook could cut that.
2. **Prompt re-processing** (38M tokens against SGLang's 21 to 25M): test a larger prefill chunk.
