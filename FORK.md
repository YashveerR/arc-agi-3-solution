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
| Run audit: per-level breakdown of where actions and generated tokens go, where score is lost, and run-to-run noise | [`research/audit_run.py`](research/audit_run.py) | analysis only, no effect on submissions |

## Method

Each pass of an agent is noisy (about ±17–29% for one 25-game pass, about ±8% for one hidden-set submission). A change is only kept if repeated local passes show an improvement larger than that noise. See [`research/README.md`](research/README.md).
