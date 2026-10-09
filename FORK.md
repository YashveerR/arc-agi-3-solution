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
| Run audit: per-level breakdown of where actions and generated tokens go, where score is lost, run-to-run noise, pass-to-pass swings and when levels get stuck | [`research/audit_run.py`](research/audit_run.py) | analysis only, no effect on submissions |

## Results

| Date | Configuration | Local games × passes | Mean | Hidden-set score | Report |
|---|---|---|---|---|---|
| 2026-10-08 | Franzen's published configuration, unchanged (baseline) | 25 × 2 | 47.2 | 26.52 (separate submission) | [baseline](research/results/2026-10-08-baseline/report.md) |

What the baseline shows:

- **Action efficiency is not the problem.** Completed levels use a median 0.67× the human number of actions; perfect efficiency would add only about 2 points.
- **Almost all lost score is levels never completed** (about 51 of the 53 missing points).
- **Outcomes swing between passes.** 12 of 25 games differ by two or more levels between the two passes (for example m0r0 scored 4.8 on one pass and 100 on the other). Taking each game's better pass would give 63.4 instead of 47.2.
- **Stuck levels absorb compute.** 92% of completed levels needed under 60k generated tokens; the level a run ended stuck on had absorbed a median 103k, and 17% of all tokens went into levels past 60k that were never completed.

## Method

Each pass of an agent is noisy (about ±17–29% for one 25-game pass, about ±8% for one hidden-set submission). A change is only kept if repeated local passes show an improvement larger than that noise. See [`research/README.md`](research/README.md).
