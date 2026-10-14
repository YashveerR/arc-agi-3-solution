# System-RAM cache at 10 games: second run (the submitted version)

**Run:** 2026-10-13. Kaggle's save run of the notebook version that was then submitted. Same configuration as the [first 10-game run with the cache](../2026-10-12-hicache-32g/README.md): 32 GB cache, 10 games.

**Local result:** 9.17M generated tokens; score 44.45.

**Server:** requests generating 8.89; mean decode 678 tokens/s; large re-processed prompts 8.7M tokens. This is the same as the first run.

**Competition submission of this version:** public score 28.48, which completed without problems. That confirms the 32 GB RAM cache is stable at 10 games through a full 9-hour, 110-game competition run.

**Two runs together:**
- tokens 9.26M and 9.17M, against 8.94–9.43M without the cache;
- scores 47.66 and 44.45, against 43.7–47.2 without it.

At 10 games the cache is neutral, as expected: it only pays off with more games at once.
