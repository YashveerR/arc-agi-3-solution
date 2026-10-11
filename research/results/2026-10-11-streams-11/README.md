# Admitting 11 games at once: result

**Run:** 2026-10-11 on Kaggle. Franzen's published configuration with [`ARC3_MAX_ACTIVE_STREAMS=11`](../../throughput/README.md); the server limit stays at 10 running requests. 25 public games × 2 passes.

**Files:** [audit report](report.md), [levels.csv](levels.csv), `benchmark.json`, the server log (`serve.log.gz`), and a [summary comparing it with the 10-game run](serve-summary.md).

## Verdict

**Failed. Keep 10.** The extra game crowded the cache.

| criterion (set before the run) | needed | result | |
|---|---|---|---|
| generated tokens | ≥ 9.9M | 8.69M, against an earlier 8.94–9.43M | fail |
| mean requests generating | ≥ 9.3 | 9.42, up from 8.85 | pass |
| large uncached prompts | ≤ 14M tokens | 21.1M, up from 9.3M | fail |
| errors | none | none | pass |
| score | 43.7–47.2 | 46.1 | pass |

## What happened

- **The slots filled up.** Requests generating rose from 8.85 to 9.42 on average, and the server had a request waiting half the time.
- **The cache overflowed.** It holds 1.01M tokens and was already peaking at 99% with 10 games, so the 11th game's prompts pushed others out. Prompt tokens re-processed from scratch rose from 21.6M to 33.4M, and the cache hit rate fell from 93.5% to 89.6%.
- **Decoding slowed.** With 10 requests running, decode dropped from 783 to 750 tokens/s, because more prompt processing was interleaved.
- **Net result.** The extra prompt processing, roughly 19 minutes of GPU time, outweighed the filled slots. Generated tokens fell 5% against the mean of the three earlier runs.

**Conclusion.** KV-cache capacity, not idle slots, is what limits throughput in this setup. Franzen's choice of 10 is right for this cache size. The remaining serving levers are small (a few percent each): shortening the time a game holds its slot without generating, and fewer re-processed prompts.
