# 12 games at once with the system-RAM cache: crashed after 2.1 hours

**Run:** 2026-10-13 on Kaggle. Franzen's configuration plus:
- a 32 GB [system-RAM cache](../../hicache/README.md);
- 12 games admitted at once;
- server settings `MAXREQ=12`, `CUDAGRAPH_MAXBS=12`, `MAMBA_CACHE=68` ([run 2](../../hicache/run2.md)).

The server log confirms all of these (`max_running_requests: 12`, `hicache_size: 32`, `max_mamba_cache_size: 68`).

**Files:** `benchmark.json` (truncated run) and `serve.log.gz`.

## What happened

**The crash.** At 22:53, 2.1 hours in, the server's scheduler process was killed: `Subprocess scheduler_0 (pid=541) crashed with exit code -9`.
- Exit code -9 is SIGKILL from outside the process. There is no CUDA error and no Python traceback, and the decode lines up to 11 seconds before look normal.
- That points to the system running out of RAM and the kernel killing the largest process. This is not confirmed yet: the notebook's `[sys]` monitor lines would show it.
- After the crash every model call failed (`analyzer failed 11 times consecutively`), so the run's score (31.46) means nothing.

**What it measured while running** (first 2 hours, against every 10-game run):

| | 12 games + RAM cache | 10-game runs (6 runs) |
|---|---|---|
| generated tokens in the first 2 h | **4.71M** | 4.31–4.49M (mean 4.43M) |
| levels completed in the first 2 h | 146 | 133–145 |
| mean decode tokens/s (server) | **733** | 678–687 |
| requests generating (mean) | 10.98 of 12 | 8.85–8.94 of 10 |
| large re-processed prompts | 3.1M tokens in 2.1 h | 8.6–9.3M in 4.1 h |

**Reading.**
- With the RAM cache, 12 games fill the GPU better: +6% generated tokens and +7% decode throughput.
- There was no re-processing blow-up like the 11-game run without the cache.
- Decode speed per batch tops out at about 780 tokens/s above 10 running requests, so the gain comes from fewer idle slots, not faster decoding.

## To make it usable

System RAM has to have room. On this machine:
- total: 176.9 GiB;
- Franzen's BF16 PLE table: about 96 GB;
- RAM cache: 32 GB;
- the harness for every game, plus the Python sandboxes, takes the rest.

**Options:**
- a smaller RAM cache (16 GB);
- the FP8 PLE table, as Siriki did: it frees about 48 GB, but needs a mixed model folder built from a second checkpoint.

The `[sys]` lines from this run and the 10-game run decide which. Note that a competition rerun keeps all 110 games live, not 50, so it needs more margin than local runs.
