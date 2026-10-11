## 10 games (2026-10-10)

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

## 11 games (2026-10-11)

KV cache: 1,011,264 tokens; server limit 10 running requests; 4.08 h of decoding statistics.

| from | requests generating (mean) | share of time at the limit | KV used (mean / max) | decode tokens/s (median) |
|---|---|---|---|---|
| 0.0 h | 9.9 | 91% | 0.51 / 0.99 | 731 |
| 0.5 h | 9.9 | 91% | 0.63 / 0.93 | 746 |
| 1.0 h | 9.7 | 81% | 0.62 / 0.93 | 721 |
| 1.5 h | 9.5 | 69% | 0.78 / 0.97 | 746 |
| 2.0 h | 9.5 | 71% | 0.78 / 0.98 | 728 |
| 2.5 h | 9.3 | 65% | 0.77 / 0.97 | 736 |
| 3.0 h | 9.0 | 52% | 0.75 / 0.98 | 731 |
| 3.5 h | 8.8 | 50% | 0.72 / 0.97 | 734 |
| 4.0 h | 7.0 | 35% | 0.49 / 0.85 | 677 |

Decode tokens/s by requests generating: 1: 175, 2: 294, 3: 350, 4: 482, 5: 483, 6: 567, 7: 675, 8: 723, 9: 744, 10: 750
Mean decode throughput 687 tokens/s; with every slot busy 750 (+9%).
Prompt tokens: 287.7M from cache, 33.4M processed (89.6% cached); 2576 large prompts mostly not cached (21.1M tokens).

## Comparison

| log | requests generating | mean decode tokens/s | KV mean / max | prompt tokens processed | large uncached prompts |
|---|---|---|---|---|---|
| 10 games (2026-10-10) | 8.85 | 678 | 0.65 / 0.99 | 21.6M | 1130 (9.3M) |
| 11 games (2026-10-11) | 9.42 | 687 | 0.69 / 0.99 | 33.4M | 2576 (21.1M) |
