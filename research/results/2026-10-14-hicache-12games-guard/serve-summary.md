## 10 games + RAM cache (10-13, submitted version)

KV cache: 1,011,264 tokens; server limit 10 running requests; 4.09 h of decoding statistics.

| from | requests generating (mean) | share of time at the limit | KV used (mean / max) | decode tokens/s (median) |
|---|---|---|---|---|
| 0.0 h | 9.5 | 64% | 0.54 / 0.94 | 769 |
| 0.5 h | 9.5 | 60% | 0.56 / 0.95 | 746 |
| 1.0 h | 9.2 | 48% | 0.66 / 0.90 | 742 |
| 1.5 h | 8.8 | 33% | 0.74 / 0.96 | 740 |
| 2.0 h | 8.5 | 30% | 0.69 / 0.91 | 712 |
| 2.5 h | 8.6 | 32% | 0.72 / 0.95 | 730 |
| 3.0 h | 8.6 | 29% | 0.72 / 0.94 | 709 |
| 3.5 h | 8.7 | 32% | 0.71 / 0.96 | 733 |
| 4.0 h | 7.3 | 5% | 0.50 / 0.91 | 662 |

Decode tokens/s by requests generating: 3: 362, 4: 489, 5: 482, 6: 573, 7: 671, 8: 722, 9: 760, 10: 784
Mean decode throughput 678 tokens/s; with every slot busy 784 (+16%).
Prompt tokens: 316.0M from cache, 20.7M processed (93.9% cached); 1068 large prompts mostly not cached (8.7M tokens).

## 12 games + RAM cache + guard (10-14)

KV cache: 977,984 tokens; server limit 12 running requests; 4.06 h of decoding statistics.

| from | requests generating (mean) | share of time at the limit | KV used (mean / max) | decode tokens/s (median) |
|---|---|---|---|---|
| 0.0 h | 11.1 | 49% | 0.60 / 1.00 | 785 |
| 0.5 h | 11.2 | 49% | 0.75 / 1.00 | 789 |
| 1.0 h | 10.9 | 34% | 0.81 / 1.00 | 783 |
| 1.5 h | 10.5 | 9% | 0.89 / 1.00 | 772 |
| 2.0 h | 10.3 | 9% | 0.87 / 1.00 | 769 |
| 2.5 h | 10.2 | 11% | 0.86 / 1.00 | 772 |
| 3.0 h | 10.2 | 9% | 0.86 / 0.99 | 777 |
| 3.5 h | 9.9 | 7% | 0.84 / 0.99 | 760 |
| 4.0 h | 8.1 | 6% | 0.61 / 0.99 | 656 |

Decode tokens/s by requests generating: 5: 491, 6: 579, 7: 668, 8: 722, 9: 773, 10: 795, 11: 782, 12: 837
Mean decode throughput 723 tokens/s; with every slot busy 837 (+16%).
Prompt tokens: 320.8M from cache, 25.2M processed (92.7% cached); 1378 large prompts mostly not cached (11.3M tokens).

## Comparison

| log | requests generating | mean decode tokens/s | KV mean / max | prompt tokens processed | large uncached prompts |
|---|---|---|---|---|---|
| 10 games + RAM cache (10-13, submitted version) | 8.89 | 678 | 0.66 / 0.96 | 20.7M | 1068 (8.7M) |
| 12 games + RAM cache + guard (10-14) | 10.50 | 723 | 0.81 / 1.00 | 25.2M | 1378 (11.3M) |
