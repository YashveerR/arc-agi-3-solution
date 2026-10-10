# Stuck review

When one level has used `ARC3_STUCK_REVIEW_TOKENS` generated tokens without being completed, the harness adds a review checkpoint to the start of the next turn. The model is asked to:

1. list the ideas it has rejected on this level;
2. check whether the test that ruled out each one was fair;
3. properly re-test the most coherent idea that was ruled out unfairly.

Nothing is removed from the model's context, and the game is not touched. Off by default.

## Why

[Six transcripts of stuck runs](../results/2026-10-09-fresh-start-60k/transcript-diagnoses/README.md) show the same pattern in five of them. The model reaches the right idea about a level, then drops it after a test that could not have shown it:
- **g50t:** it checked one spot too early.
- **sc25:** it tested while a precondition was false.
- **tn36:** it tried a fragment instead of the whole configuration.

It never comes back to the idea. Other passes of the same games solved those levels.

The [fresh start](../fresh_start/README.md) went after the same problem by deleting the stuck attempt. That made things worse, because it also deleted the right idea. The review works in the other direction: it keeps everything and points the model back at what it already considered.

## What it does

At the start of each analyzer turn, the checkpoint fires if both of these hold:
- the current level has used at least n × `ARC3_STUCK_REVIEW_TOKENS` generated tokens, where n is the number of the next review;
- the level has had fewer than `ARC3_STUCK_REVIEW_MAX` reviews.

When it fires:
1. **The turn opens with the note**, a full prompt and the current board. A short "resume" prompt would drop the note, so the full prompt is used for that one turn.
2. **Nothing else changes.** The history is kept, and so are the scheduler's per-level counters, so a reviewed game is not moved up the queue. The fresh start did both.
3. **It is recorded.** The solver note in `benchmark.json` gets `review_arm=on reviews=<level>@<tokens>,…`, and the game transcript gets a `stuck_review:` status line. `research/audit_run.py` reports this in section 10.

Code: `ARC3-Inference/inference/agent/tool_agent.py` (`_maybe_stuck_review`, `_STUCK_REVIEW_NOTE`) and `ARC3-Inference/inference/framework/solver.py` (A/B assignment and the note). As a patch against the competition tree: [`stuck-review.patch`](stuck-review.patch).

| Setting | Default | Meaning |
|---|---|---|
| `ARC3_STUCK_REVIEW_TOKENS` | `0` (off) | Generated tokens on one level per review: review n fires at n × this |
| `ARC3_STUCK_REVIEW_MAX` | `2` | Reviews allowed per level |
| `ARC3_STUCK_REVIEW_AB` | `0` | Measurement only: each game gets reviews on one pass and not on the other |

**A/B mode.** Each game's two passes go to opposite arms. Which pass gets reviews varies by game, so neither arm is always pass 0, which the scheduler orders first. The pass without reviews still records where its checkpoints would have fired, so both arms are compared at the same trigger point in the same run: same GPU, scheduler and clock.

## Using it on Kaggle

1. If the old fresh-start cell is still in your copy of Franzen's notebook, delete it. The new cell refuses to run while the fresh-start patch is applied.
2. Paste [`notebook_cell.py`](notebook_cell.py) as a **new cell directly after section "1. Environment and submission mode"** and **before "2. Precaching"**.

The cell carries the patch base64-encoded and checks its SHA-256, so a damaged copy fails with a clear message. Running it twice is safe.

**Settings in the cell:**
- `REVIEW_TOKENS = 40000`. A review at 40k tokens comes while the stuck level's conversation is still in context; about 80% of completed levels needed less than that (77% and 83% in the two runs so far).
- `REVIEW_MAX = 2`, so the second review fires at 80k.
- `AB_TEST = True`, for measurement runs.

**For a submission, set `AB_TEST = False`.** Otherwise only about half the games get reviews. To switch the feature off, set `REVIEW_TOKENS = 0`.

Regenerate the cell after changing the patch: `python3 research/stuck_review/make_cell.py`.

## Evaluating it

1. Run the notebook interactively with the cell, `AB_TEST = True`, `bm.n_passes = 2` and all 25 games. This is the same setup as the earlier runs.
2. Audit: `python3 research/audit_run.py <run dir> --out <dir>`. Section 10 compares the two arms:
   - the share of levels completed after reaching a checkpoint (with a Fisher test);
   - the score difference paired by game.
3. Expect about 30 levels per arm to reach a checkpoint in one run, so only a large effect shows up in a single run.

**Decision rule, set before seeing results.** Recommend a submission with reviews on only if both of these hold:
- the reviewed arm completes clearly more checkpoint levels (at least 15 points more, pooled over runs);
- the paired score difference is not negative.

If one run is unclear, run another and pool. If the reviewed arm is worse, drop it.

## Testing done (no GPU needed)

All on the exact tree Kaggle runs: the competition bundle plus Franzen's patch, with this patch applied. The two patched files come out byte-identical to this branch.

**Unit tests** ([`../tests/test_stuck_review_unit.py`](../tests/test_stuck_review_unit.py)), 11/11 pass:
- off by default;
- fires at the threshold, not below it;
- history and scheduler counters untouched;
- second review at twice the threshold;
- the maximum is respected;
- one review per check;
- a new level gets its own reviews;
- never fires after a win;
- the A/B arm without reviews records but sends nothing;
- A/B assignment alternates passes and varies by game.

**End to end** ([`../tests/e2e_stuck_review.py`](../tests/e2e_stuck_review.py)). The real harness plays TAAF's `ExampleGame` with Franzen's notebook settings against a stand-in model that presses a wrong key until it sees the note.
- **Stuck on level 1 and stuck on level 2:** the review fires at 12k tokens and arrives with the board image. The history grows from 11 to 14 messages, with nothing removed, and the stuck attempt's output is still in context. The game is won.
- **A/B with 2 passes:** the reviewed pass wins (`review_arm=on reviews=1@12000`). The other pass stays stuck, records checkpoints at 12k and 21k, and sends no note.
- **Switched off:** all 11 requests are identical to the unpatched harness's.
- **No request** contains a private key.

**The notebook cell**, run as the notebook would:
- applies cleanly, and a second run skips;
- a damaged copy is rejected;
- a notebook still carrying the fresh-start patch is stopped with "delete it" advice;
- the tree it produces passes the A/B end-to-end test.

**Not testable here:** whether Qwen3.8-Flash-Next actually uses the review well. That is what the Kaggle run measures.
