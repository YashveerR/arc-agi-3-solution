# Run 2: 12 games at once with the system-RAM cache

[Run 1](../results/2026-10-12-hicache-32g/README.md) passed three of four criteria. The cache attached, tokens held and it was stable. The miss criterion failed for a reason that doesn't bear on this run: at 10 games the re-processing is mostly trims, not evictions. Run 2 tests the eviction case directly.

## Changes on top of run 1

1. **Section 1:** paste the [throughput cell](../throughput/notebook_cell.py) after section 1 with `ACTIVE_STREAMS = 12`, so the harness admits 12 games.
2. **Section 5, in `CFG = dict(...)`,** change three numbers so the server runs 12 requests at once:
   - `MAXREQ=12` (was 10)
   - `CUDAGRAPH_MAXBS=12` (was 10; the notebook asserts it covers `MAXREQ`)
   - `MAMBA_CACHE=68` (was 60)

   Each running request holds 4 slots of the model's recurrent-state cache. 10 requests used 40 of the 60, leaving 20 for cached prompts. 12 requests need 48, and 68 keeps 20 spare. The extra 8 slots cost about 0.45 GB of GPU memory, roughly 4% of the KV pool.
3. **Keep the section-5 snippet from run 1** (`HICACHE_GB = 32`).

## Judging it (set before the run)

- **Tokens:** at least 9.9M generated (+8% over the 10-game mean of 9.18M).
- **Re-processing:** at most 13M tokens in large prefill chunks (≥ 8K new tokens per log line). The 11-game run without the tier had 22.6M, and 10 games have 9.9–10.6M.
- **Stability:** no out-of-memory errors, retractions or server restarts.
- **Score:** within the usual range (43.7–47.2).

Upload `benchmark.json` and `serve.log` as before.
