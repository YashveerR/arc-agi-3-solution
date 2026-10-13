# System-RAM prompt cache at 10 games: result

**Run:** 2026-10-12 on Kaggle. Franzen's configuration with a 32 GB [hierarchical cache](../../hicache/README.md) in system RAM; streams unchanged at 10. 25 public games × 2 passes.

**Files:** [audit report](report.md), [levels.csv](levels.csv), `benchmark.json`, `serve.log.gz`, and a [server summary compared with the 10- and 11-game runs](serve-summary.md).

## Against the criteria set before the run

| criterion | needed | result | |
|---|---|---|---|
| cache tier attached | yes | yes: a host pool of 1.8M KV tokens (23.9 GB) + 6.6 GB Mamba state + 1.5 GB index | pass |
| large uncached prompts | ≤ 5M tokens | 8.6M, down from 9.3M | **fail** |
| generated tokens | ≥ 8.9M | 9.26M (earlier 10-game runs: 8.94–9.43M) | pass |
| stability | no OOM or restarts | none; one routine "KV pool full, retract 1 request" event | pass |

**Score:** 47.66, the highest of the five local runs (43.7–47.7), but within the noise.

## Why criterion 2 failed, and what it means

**The breakdown.** Prompt processing done in large chunks (8K-token chunked-prefill lines), the big re-processing events:

| run | tokens in large prefill chunks |
|---|---|
| 10 games, no RAM cache | 10.6M |
| 11 games, no RAM cache | 22.6M |
| 10 games, 32 GB RAM cache | 9.9M |

**What the breakdown shows.**
- **At 10 games, almost none of the large re-processing is cache evictions.** The tier removed only 7%. The rest is most likely history trims, which change a game's prompt so no cache can match it, plus genuinely new prompts.
- **The criterion assumed otherwise.** It took most of the 9.3M to be evictions, and it was wrong.
- **The 11-game run was different:** its extra 12M tokens were evictions caused by the 11th game. That is what the system-RAM tier is built to absorb, and this 10-game run could not test it.

**The tier itself.** It is harmless at 10 games: tokens +1%, stable, best local score. It does not raise throughput by itself.

**Next.** [Run 2](../../hicache/run2.md), 12 games with the tier, is the real test. Its bar is restated on the cleaner measure:
- generated tokens ≥ 9.9M;
- tokens in large prefill chunks ≤ 13M, about half of the 11-game run's 22.6M.
