# Throughput: admit 11 games at once

## Why

Recomputing three runs' scores at earlier cut-off times shows the score still rising by about 7 points per hour at the end of a 4-hour run. Generated tokens stay flat at about 2.2M per hour the whole time. Each 10% more throughput should therefore be worth roughly 2–3 points ([analysis](../results/2026-10-10-stuck-review-ab/README.md)).

The server log of the 2026-10-10 run ([summary](../results/2026-10-10-stuck-review-ab/serve-summary.md)) shows where throughput is lost:
- **Empty slots.** On average only 8.7 of the server's 10 request slots are generating, falling from 9.5 early in the run to 8.5 later. Each game keeps its slot ([`solver.py`](../../ARC3-Inference/inference/framework/solver.py), `gate.acquire` / `release`) until it finishes or its context is trimmed. That includes the time it spends running Python between model requests.
- **What full slots would give.** Decode throughput is 783 tokens/s with all 10 slots busy against a run average of 678, so +15% if the slots never sat empty.
- **More streams is not the answer.** The KV cache holds about 1.01M tokens and peaks at 90–99% full. Raising the server's own limit above 10 would overflow it.

## The change

**Setting.** `ARC3_MAX_ACTIVE_STREAMS=11`: the harness admits 11 games while the server keeps its limit of 10 running requests. The 11th game fills the gaps while other games run Python. When all 11 want the GPU at once, one waits briefly in the server's queue.

**What doesn't change.** The server batch never exceeds 10, so memory per batch is as before.

**Risk.** An 11th game's prompt cache competes for KV memory, which could push more cached prompts out and cost re-processing. Franzen limited admission to 10 for exactly this reason ([write-up](../../WRITEUP.md), "Limiting concurrent admission to protect the cache").

There's no harness patch: [`notebook_cell.py`](notebook_cell.py) only overrides the environment variable that section 1 sets.

## Judging it (set before the run)

**Primary measure: generated tokens in `benchmark.json`.** The three earlier runs produced 8.94M, 9.43M and 9.17M in the same 4 hours, so ±3%.

**Success needs all of these:**
1. **Tokens.** At least 9.9M generated tokens (+8% over the earlier mean).
2. **Server.** In `research/serve_stats.py` on the new `serve.log`:
   - mean requests generating is at least 9.3, up from 8.7;
   - large uncached prompts process at most 14M tokens, against 9.3M before.
3. **Stability.** No out-of-memory errors, retractions or request timeouts in the logs.
4. **Score.** The score is reported, but a 2–3 point gain cannot be confirmed in one run. It only has to stay within the earlier range (43.7–47.2), allowing for noise.

**If it succeeds,** try 12 the same way, then submit with the best setting.

**If tokens rise but uncached prompts balloon,** the cache cost is eating the gain. Go back to 10 and look at handing the slot over during Python runs instead.

Compare the logs with:

```bash
python3 research/serve_stats.py research/results/2026-10-10-stuck-review-ab/serve.log <new serve.log>
```

(`serve.log.gz` in that folder: `gunzip -k` first.)
