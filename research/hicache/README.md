# System-RAM tier for the prompt cache

**Run 1 (2026-10-12, 10 games):** attached and stable, tokens +1%, score 47.66. Re-processed prompts barely fell: at 10 games they are mostly trims, not evictions. See the [result](../results/2026-10-12-hicache-32g/README.md). [Run 2](run2.md), at 12 games, is the real test.

## Why

The GPU's prompt cache, the KV pool, limits throughput. Our evidence:
- It holds 1.01M tokens and peaks at 90–99% full.
- A run re-processes 9.3M prompt tokens from scratch, about 6% of GPU time.
- Admitting an 11th game more than doubled that, to 21.1M, and cost 5% of tokens ([result](../results/2026-10-11-streams-11/README.md)).

Other teams report the same limit ([field notes](../field-notes.md)).

**What the tier does.** Lohit Siriki's Milestone 2 notebook runs the same server family (SGLang Pennyroyal) with a 48 GB tier in system RAM for evicted cache pages. When a game comes back, its prompt is copied from RAM instead of being re-processed. That should:
1. cut the 9.3M re-processed tokens at 10 games, and
2. make 12 or more games at once workable, because overflow lands in RAM instead of being thrown away.

## The change

[`section5_snippet.py`](section5_snippet.py) adds four server flags:

```
--enable-hierarchical-cache --hicache-size 32 --hicache-write-policy write_through --hicache-io-backend kernel
```

**Where it goes:** section 5 of Franzen's notebook, directly above `# ---- launch detached and wait for health ----`.

**RAM budget.** The machine has 176.9 GiB of system RAM (from Siriki's boot log). Franzen's BF16 PLE table takes about 96 GB, and Siriki used an FP8 PLE (about 48 GB) to make room for 48 GB. With the BF16 PLE kept, 32 GB leaves about 50 GB for everything else.

**If a flag isn't recognised** by Franzen's Pennyroyal version (v2.5.3 against Siriki's v2.5.0), the server exits within a minute and the notebook shows the log tail. The test then costs minutes, not hours.

## Judging it (set before the run)

**Run 1: tier on, 10 games** (Franzen's stream setting unchanged). All four must hold:
1. **It attached.** The server boots and `serve.log` mentions the hierarchical cache.
2. **Fewer re-processed prompts.** Large uncached prompts process at most 5M tokens, down from 9.3M, measured with `research/serve_stats.py`.
3. **No loss of tokens.** Generated tokens are at least 8.9M, the lowest of the three earlier 10-game runs.
4. **Stable.** No out-of-memory errors or server restarts in the logs.

Throughput at 10 games may rise only a few percent. The real payoff is run 2.

**Run 2, only if run 1 passes: tier on, 12 games** ([exact changes](run2.md)) (`ARC3_MAX_ACTIVE_STREAMS=12`, server `MAXREQ=12`, CUDA graphs up to 12).
- Success needs at least 9.9M generated tokens (+8% over the earlier mean of 9.18M).
- Large uncached prompts must stay at most 9.3M tokens.

**Whatever happens,** upload `benchmark.json` and `serve.log`.
