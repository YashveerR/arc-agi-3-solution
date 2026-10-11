## research/results/2026-10-10-stuck-review-ab/serve.log

KV cache: 1,011,264 tokens; server limit 10 running requests; 4.10 h of decoding statistics.

| from | requests generating (mean) | share of time at the limit | KV used (mean / max) | decode tokens/s (median) |
|---|---|---|---|---|
| 0.0 h | 9.5 | 60% | 0.53 / 0.95 | 763 |
| 0.5 h | 9.5 | 61% | 0.56 / 0.84 | 759 |
| 1.0 h | 9.2 | 50% | 0.64 / 0.90 | 754 |
| 1.5 h | 8.9 | 34% | 0.74 / 0.94 | 739 |
| 2.0 h | 8.6 | 30% | 0.71 / 0.91 | 723 |
| 2.5 h | 8.4 | 26% | 0.69 / 0.96 | 702 |
| 3.0 h | 8.5 | 26% | 0.70 / 0.91 | 718 |
| 3.5 h | 8.5 | 28% | 0.71 / 0.99 | 719 |
| 4.0 h | 7.2 | 17% | 0.42 / 0.72 | 675 |

Decode tokens/s by requests generating: 2: 303, 3: 346, 4: 470, 5: 482, 6: 571, 7: 670, 8: 720, 9: 760, 10: 783
Mean decode throughput 678 tokens/s; with every slot busy 783 (+15%).
Prompt tokens: 312.7M from cache, 21.6M processed (93.5% cached); 1130 large prompts mostly not cached (9.3M tokens).

