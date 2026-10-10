# Fresh start when stuck

When one level has used `ARC3_FRESH_START_TOKENS` generated tokens without being completed, the harness clears that level's conversation from the model's context. The model then starts the level again with fresh eyes. Off by default.

**Result (2026-10-09, 60k threshold): no measurable gain.**
- 42% of restarted levels were completed later, against the baseline's 36% (p = 0.66).
- The mean fell from 47.2 to 43.7, within noise.
- The run exposed two design problems: restarts discard nearly-solved attempts, and they lift a stuck game's scheduler priority.

See the [result](../results/2026-10-09-fresh-start-60k/README.md) before using this.

**Removed from the harness on 2026-10-10.** It was replaced by the [stuck review](../stuck_review/README.md), which keeps the conversation. This folder is the record: the patch and cell still apply to the competition tree. The tests are in [`tests/`](tests/) and need a tree with `fresh-start.patch` applied.

## Why

The baseline run (25 public games × 2 passes, [report](../results/2026-10-08-baseline/report.md)) showed:

- 12 of 25 games differ by two or more levels between the two passes. Taking each game's better pass would score 63.4 instead of 47.2. The agent can solve these games; on some passes it locks onto a wrong idea and never recovers.
- 92% of completed levels needed under 60k generated tokens. The level a run ended stuck on had absorbed a median 103k.
- Of levels that passed 60k tokens without being completed, only 36% were ever completed. **That is the rate a fresh start has to beat.**

Other attempts were different. lordhansolo's Milestone 2 entry adds a "you may be stuck, audit your assumptions" prompt, but inside the same conversation. Franzen tried periodic summaries that weren't tied to being stuck. This change removes the stuck attempt itself.

## What it does

At the start of each analyzer turn, if the current level has used at least `ARC3_FRESH_START_TOKENS` generated tokens and has had fewer than `ARC3_FRESH_START_MAX` fresh starts:

1. **Clears this level's conversation.** History is kept up to the first turn opened on this level. Every turn's opening message carries a private level tag; it is stripped before any request leaves the process.
2. **Keeps what's still valid.** Earlier levels' conversation, retained helper functions, and the game state are untouched. The level is **not** reset.
3. **Opens a fresh turn.** The turn starts with a full prompt (current board image included) and a short note. The note says the previous attempt was abandoned after N tokens and M actions, and asks for a fresh look at the goal and the controls.
4. **Restarts the level's counters.** The priority scheduler prices the new attempt as new, and a further fresh start (if allowed) needs another full threshold.
5. **Records it.** The solver note in `benchmark.json` gets `fresh_starts=<level>@<tokens>,…`, which `research/audit_run.py` reports in section 9.

Code: `ARC3-Inference/inference/agent/tool_agent.py` (`_maybe_fresh_start`, `_history_before_level`) and `ARC3-Inference/inference/framework/solver.py` (the note). As a patch: [`fresh-start.patch`](fresh-start.patch).

| Setting | Default | Meaning |
|---|---|---|
| `ARC3_FRESH_START_TOKENS` | `0` (off) | Generated tokens on one level before a fresh start |
| `ARC3_FRESH_START_MAX` | `1` | Fresh starts allowed per level |

## Using it on Kaggle

Paste [`notebook_cell.py`](notebook_cell.py) into your copy of Franzen's notebook as a **new cell directly after section "1. Environment and submission mode"** (the cell that applies his harness patch) and **before "2. Precaching"**.

The cell carries the patch base64-encoded and checks its SHA-256, so a damaged copy fails with a clear message instead of a broken harness. Running the cell twice is safe. Set `FRESH_START_TOKENS = 0` in the cell to switch the feature off.

The cell applies to competition reruns too. Don't submit a version with it switched on until a local run has shown it helps.

Regenerate the cell after changing the patch: `python3 research/fresh_start/make_cell.py`.

## Evaluating it

1. Run the notebook interactively with the cell (`bm.n_passes = 2`, all 25 games), the same as the baseline run.
2. Audit against the baseline:
   ```bash
   python3 research/audit_run.py <new run dir> --baseline research/results/2026-10-08-baseline/benchmark.json
   ```
3. Section 9 shows the share of restarted levels that were later completed. Compare it with the baseline's 36% for levels past 60k. With roughly 40 restarts expected per 2-pass run, a rate of about 55% or more would be a clear signal. Section 1's mean score is the secondary check, and it is noisier.

## Testing done (no GPU needed)

All against the exact tree Kaggle runs: the competition bundle plus Franzen's patch, rebuilt from the mirrored dataset copy. Applying his patch there reproduces the notebook log exactly (`Hunk #1 succeeded at 467 (offset 48 lines)`), and this patch then applies cleanly.

- **Unit tests** ([`../tests/test_fresh_start_unit.py`](tests/test_fresh_start_unit.py)), 10/10 pass:
  - off by default changes nothing;
  - fires at the threshold, not below it;
  - cuts at the level's first turn, keeping earlier levels;
  - one per level by default; with a higher limit, each needs a full threshold;
  - a new level gets its own budget;
  - front-trimmed history and dangling openers are handled;
  - never fires after the game is won;
  - the private tag is stripped before sending.
- **End to end** ([`../tests/e2e_fresh_start.py`](tests/e2e_fresh_start.py)): the real harness plays TAAF's `ExampleGame` with Franzen's notebook settings, against a stand-in model server that keeps pressing a wrong key until it sees a fresh-start note.
  - **Stuck on level 1:** fires after 12k tokens. The next request is just the system prompt and the fresh opener; no output from the stuck attempt reappears; the game is won; the note reads `fresh_starts=1@12000`.
  - **Stuck on level 2:** the turn that solved level 1 is kept and only level 2's attempt is dropped. The game is won; the note reads `fresh_starts=2@12000`.
  - **Switched off:** all 25 requests are identical to the unpatched harness's, apart from two clock fields the harness prints.
  - **No request** contains a private tag.
- **The notebook cell**, executed exactly as the notebook would:
  - applies cleanly, and the resulting files are identical to this branch;
  - a second run skips safely;
  - a deliberately damaged copy is rejected;
  - the tree it produces passes the end-to-end test.

Not testable here: real model behaviour. Whether a fresh look actually unsticks Qwen3.8-Flash-Next is exactly what the Kaggle run measures.
