# Research tools

Analysis scripts for this fork. None of them change what a submission does.

## `audit_run.py`: where actions and tokens go

Reads the `benchmark.json` that every TAAF / Duck-harness run writes to its job directory and prints a Markdown report:

1. **Score and noise.** The mean score (recomputed from per-level actions as a check), how much one full pass varies, and how many passes are needed to detect a +10/20/30% improvement.
2. **Where the points go.** Each game's 100 points split into earned, lost to inefficiency on completed levels, lost on the level the run was stuck on, and lost on levels never reached.
3. **Action efficiency** on completed levels, compared with the human baseline.
4. **Completion by level number.**
5. **Where generated tokens go**, including tokens spent on a stuck level after most successful runs would already have finished it.
6. **A per-game table.**

Standard library only.

```bash
python3 research/audit_run.py /path/to/run_dir              # report to stdout
python3 research/audit_run.py /path/to/run_dir --out audit/  # also writes report.md and levels.csv
```

### On Kaggle

After an interactive run of the notebook (Save & Run All, not a competition rerun), `benchmark.json` is in `/kaggle/working`. Either download it from the version's **Output** tab and run the script locally, or add a cell at the end of the notebook:

```python
!python3 /path/to/audit_run.py /kaggle/working --out /kaggle/working/audit
```

### Checked against

Tufa Labs' public example run (25 games × 20 passes, in [Tufalabs/duck-harness](https://github.com/Tufalabs/duck-harness/tree/main/example-run)):

- Per-game scores match `evaluation.json` exactly, and the recomputed score matches the reported one on all 500 runs.
- Every action and generated token is attributed to exactly one level.
- The point breakdown adds to 100 for every run.

That run uses the June configuration (Qwen 3.6, mean 1.60), so its numbers describe the old harness, not the current one.
