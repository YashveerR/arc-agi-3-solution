# Offline tests

These run on a CPU with no model and no Kaggle access.

## What you need

- **Python 3.11 or newer** with `numpy`, `requests`, `pillow`, `pydantic`, `scipy`, `matplotlib`, `imageio` and `python-dotenv`.
- **The game engine source**, pinned to the harness's version:
  ```bash
  git clone --branch v0.9.3 https://github.com/arcprize/arcengine third_party/arcengine
  ```
- **`stubs/arc_agi`**, a test-only stand-in for the `arc_agi` toolkit. The TAAF framework imports the toolkit at load time, but these tests only play `taaf.game_examples.ExampleGame`, which never uses it; any use of the stand-in raises. Never put it on the path of a real run.

## Files

| File | What it is |
|---|---|
| `stub_model.py` | the stand-in model server and Franzen's notebook settings, shared by end-to-end tests |
| `compare_requests.py` | checks that two recordings of model requests are identical, with clock values masked. `--prefix` accepts different counts from time-limited runs as long as the shared requests match |
| `e2e_play.py` | plays the example game through the real harness with extra settings (`--env KEY=VALUE`), records model requests, and records the out-of-memory score of every sandbox process it catches |

Feature tests live next to their patches, in [`../fresh_start/tests/`](../fresh_start/tests/), [`../stuck_review/tests/`](../stuck_review/tests/) and [`../sandbox_guard/tests/`](../sandbox_guard/tests/). Run them on a tree with that patch applied (see below).

## Running

From the repository root:

```bash
# with a tree that has research/stuck_review/stuck-review.patch applied (see below)
export PYTHONPATH=research/tests/stubs:third_party/arcengine:<tree>/src/tufa-arc-agi-framework/src:<tree>/src/ARC3-Inference

python3 research/stuck_review/tests/test_stuck_review_unit.py
python3 research/stuck_review/tests/e2e_stuck_review.py --review-tokens 10000 --out /tmp/sr_l1
python3 research/stuck_review/tests/e2e_stuck_review.py --review-tokens 10000 --stuck-from-level 2 --out /tmp/sr_l2
python3 research/stuck_review/tests/e2e_stuck_review.py --review-tokens 10000 --ab --passes 2 --out /tmp/sr_ab
python3 research/stuck_review/tests/e2e_stuck_review.py --review-tokens 0 --max-runtime-s 6 --out /tmp/sr_off
```

Build the tree from the competition bundle, which is what Kaggle actually runs:
1. Apply Franzen's `harness-changes.patch` with `git apply --include='ARC3-Inference/*'`.
2. Apply `research/stuck_review/stuck-review.patch` the same way.
3. Point `PYTHONPATH` at that tree's `src/`, as above.

**Switched-off check.** Run the `--review-tokens 0` case once on the patched tree and once on the tree without the patch, then compare:

```bash
python3 research/tests/compare_requests.py /tmp/sr_off_original/requests.jsonl /tmp/sr_off/requests.jsonl
```

`research/stuck_review/README.md` lists the expected results.

**Sandbox guard.** With `research/sandbox_guard/sandbox-guard.patch` applied on top of Franzen's patch:

```bash
python3 research/sandbox_guard/tests/test_sandbox_guard.py
python3 research/tests/e2e_play.py --env ARC3_SANDBOX_OOM_FIRST=1 --out /tmp/sg_on
python3 research/tests/e2e_play.py --stuck --max-runtime-s 6 --out /tmp/sg_off        # also once on the unpatched tree
python3 research/tests/compare_requests.py /tmp/sg_off_original/requests.jsonl /tmp/sg_off/requests.jsonl --prefix
```
