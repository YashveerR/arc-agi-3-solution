# Offline tests

These run on a CPU with no model and no Kaggle access.

## What you need

- **Python 3.11 or newer** with `numpy`, `requests`, `pillow`, `pydantic`, `scipy`, `matplotlib`, `imageio` and `python-dotenv`.
- **The game engine source**, pinned to the harness's version:
  ```bash
  git clone --branch v0.9.3 https://github.com/arcprize/arcengine third_party/arcengine
  ```
- **`stubs/arc_agi`**, a test-only stand-in for the `arc_agi` toolkit. The TAAF framework imports the toolkit at load time, but these tests only play `taaf.game_examples.ExampleGame`, which never uses it; any use of the stand-in raises. Never put it on the path of a real run.

## Running

From the repository root:

```bash
export PYTHONPATH=research/tests/stubs:third_party/arcengine:tufa-arc-agi-framework/src:ARC3-Inference

python3 research/tests/test_fresh_start_unit.py
python3 research/tests/e2e_fresh_start.py --fresh-start-tokens 10000 --stuck-from-level 1 --out /tmp/fs_l1
python3 research/tests/e2e_fresh_start.py --fresh-start-tokens 10000 --stuck-from-level 2 --out /tmp/fs_l2
python3 research/tests/e2e_fresh_start.py --fresh-start-tokens 0 --max-runtime-s 6 --out /tmp/fs_off
```

To test what Kaggle actually runs rather than this repository's copy, build the tree from the competition bundle:
1. Apply Franzen's `harness-changes.patch` with `git apply --include='ARC3-Inference/*'`.
2. Apply `research/fresh_start/fresh-start.patch` the same way.
3. Point `PYTHONPATH` at that tree's `src/` instead.

`research/fresh_start/README.md` lists the expected results.
