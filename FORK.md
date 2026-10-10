# About this fork

This is Yashveer R's research fork of [Daniel Franzen's ARC-AGI-3 Milestone 2 solution](https://github.com/da-fr/arc-agi-3-solution), for the ARC Prize 2026 ARC-AGI-3 competition.

## Credit

- **Tufa Labs** (Jeroen Cottaar and team) wrote the original Duck harness and the Tufa ARC-AGI Framework (TAAF): [Tufalabs/duck-harness](https://github.com/Tufalabs/duck-harness).
- **Daniel Franzen** built the Milestone 2 solution this fork starts from, including the harness changes, compute scheduling and SGLang serving work. See his [write-up](WRITEUP.md).
- Third-party code and model weights remain under their own licences. Franzen's repository is published under the Apache License 2.0 ([LICENSE](LICENSE)).

This fork starts from upstream commit [`10882e3`](https://github.com/da-fr/arc-agi-3-solution/commit/10882e332d883af3e61616df8c8a17d03a328a75).

## What this fork changes

Changes are kept on the `research` branch and listed here as they land, each with the evidence behind it.

| Change | Where | Status |
|---|---|---|
| Run audit: per-level breakdown of where actions and generated tokens go, where score is lost, run-to-run noise, pass-to-pass swings, when levels get stuck, and fresh starts | [`research/audit_run.py`](research/audit_run.py) | analysis only, no effect on submissions |
| Fresh start when stuck: clear a level's conversation after a token threshold | [`research/fresh_start/`](research/fresh_start/README.md) | tried at 60k on 2026-10-09: no measurable gain ([result](research/results/2026-10-09-fresh-start-60k/README.md)); removed from the harness, kept as a record |
| Stuck review: at a token threshold per level, ask the model to re-test ideas it rejected with an unfair test; nothing is deleted | [`research/stuck_review/`](research/stuck_review/README.md) | built and tested offline; off by default; awaiting a Kaggle A/B run |

## Results

| Date | Configuration | Local games × passes | Mean | Hidden-set score | Report |
|---|---|---|---|---|---|
| 2026-10-08 | Franzen's published configuration, unchanged (baseline) | 25 × 2 | 47.2 | 26.52 (separate submission) | [baseline](research/results/2026-10-08-baseline/report.md) |
| 2026-10-09 | Baseline + fresh start at 60k tokens | 25 × 2 | 43.7 | not submitted | [result](research/results/2026-10-09-fresh-start-60k/README.md) |

What the baseline shows:

- **Action efficiency is not the problem.** Completed levels use a median 0.67× the human number of actions; perfect efficiency would add only about 2 points.
- **Almost all lost score is levels never completed** (about 51 of the 53 missing points).
- **Outcomes swing between passes.** 12 of 25 games differ by two or more levels between the two passes (for example m0r0 scored 4.8 on one pass and 100 on the other). Taking each game's better pass would give 63.4 instead of 47.2.
- **Stuck levels absorb compute.** 92% of completed levels needed under 60k generated tokens; the level a run ended stuck on had absorbed a median 103k, and 17% of all tokens went into levels past 60k that were never completed.

What the fresh-start run shows: no measurable gain.
- 42% of restarted levels were completed later, against 36% in the baseline (p = 0.66).
- The mean fell from 47.2 to 43.7, which is within the noise of one run.
- Restarting threw away nearly-solved attempts.
- Resetting the level's counters made the scheduler give stuck games more compute.

Details are in the [result](research/results/2026-10-09-fresh-start-60k/README.md).

What six transcripts of stuck runs show ([diagnoses](research/results/2026-10-09-fresh-start-60k/transcript-diagnoses/README.md)):
- In 5 of 6 the model reached the right idea for the level, then dropped it after a test that could not have shown it.
- The fresh start erased needed knowledge every time it fired.
- The stuck review is built on these findings.

## Method

Each pass of an agent is noisy (about ±17–29% for one 25-game pass, about ±8% for one hidden-set submission). A change is only kept if repeated local passes show an improvement larger than that noise. See [`research/README.md`](research/README.md).
