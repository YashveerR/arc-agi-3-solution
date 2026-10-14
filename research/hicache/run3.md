# Run 3: 12 games with the RAM cache and the sandbox guard

[Run 2](run2.md) (12 games, 32 GB RAM cache) gave +6% generated tokens for two hours, then lost its model server ([result](../results/2026-10-13-hicache-12games-crashed/README.md)). Run 3 is the same notebook plus the [sandbox out-of-memory guard](../sandbox_guard/README.md), which makes a runaway Python snippet the process Linux kills instead of the server.

## Exact steps

1. **Open the notebook version you used for run 2** (the one that crashed). Check it has all three run-2 changes:
   - **a.** A cell directly after section 1 with `ACTIVE_STREAMS = 12` in it.
   - **b.** In section 5, inside `CFG = dict(...)`: `MAXREQ=12`, `CUDAGRAPH_MAXBS=12`, `MAMBA_CACHE=68`.
   - **c.** In section 5, directly above `# ---- launch detached and wait for health ----`: the RAM-cache snippet with `HICACHE_GB = 32`.
2. **Add the guard cell.**
   - Click the `ACTIVE_STREAMS = 12` cell, then add a new code cell directly below it.
   - Paste the whole of [`../sandbox_guard/notebook_cell.py`](../sandbox_guard/notebook_cell.py) into it, all ~100 lines. Change nothing.
3. **Run it** the same way as run 2: **Save Version → Save & Run All**. This is a local run, not a submission.
4. **Check after about 15 minutes.** In the log, find the guard cell's output. It must say:
   ```
   sandbox guard: ON (ARC3_SANDBOX_OOM_FIRST=1), kernel accepted oom_score_adj=1000
   ```
   If it says `WARNING` instead, the guard does nothing on that machine. Stop the run and send me that line.
5. **When it finishes** (about 4.2 hours), send me:
   - `benchmark.json` and `serve.log` from the version's **Output** tab;
   - from the log, every `[sys]` line, and every line that starts with `[sandbox guard]` (search the log for `sandbox guard`). If there are none, say so; that is a result too.

## Judging it (set before the run)

1. **Survives.** No `crashed with exit code -9` in `serve.log`, and no `analyzer failed ... consecutively` in the log.
2. **Tokens: at least 9.7M generated**, which is +6% over the 10-game mean of 9.18M.
   - Run 2's bar was 9.9M (+8%). It was set before any 12-game data existed.
   - Run 2 then measured +6% over its first two hours, so 9.7M asks whether that gain lasts the whole run.
3. **Score** within the usual range (43.7–47.7) or above. One run is too noisy for score to decide this.
4. **Guard lines** are counted, not judged. They tell us whether runaway snippets were the cause.

## What each outcome means

| Survives? | Guard lines? | Reading | Next |
|---|---|---|---|
| yes | yes | runaway snippets were the cause, and the guard handled them | submit 12 games + guard if tokens pass |
| yes | none | no runaway this time. One clean run is weaker evidence, since run 2 failed only after 2.1 h | submit 12 games + guard if tokens pass. The submission is the second test |
| no | yes, before the crash | snippets were part of it but not all | `HICACHE_GB = 16` |
| no | none | not a snippet: a container memory limit, or the server itself | `HICACHE_GB = 16`, or the FP8 PLE table (frees about 48 GB) |

**A crash during a submission** would cost that day's score, not cause an error. The run carries on with failing model calls and scores what it reached by then.
