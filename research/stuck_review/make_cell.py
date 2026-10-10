"""Build the paste-in Kaggle notebook cell for the stuck-review patch.

    python3 research/stuck_review/make_cell.py

Reads research/stuck_review/stuck-review.patch and writes
research/stuck_review/notebook_cell.py: one self-contained cell that carries the
patch base64-encoded (so copying it cannot mangle whitespace), checks its
SHA-256, applies it on top of Daniel Franzen's harness patch, and sets the
switches. Re-running the cell is safe: an already-applied patch is skipped.
"""
from __future__ import annotations

import base64
import hashlib
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent

CELL_TEMPLATE = '''\
# === Stuck review =============================================================
# From the research branch of https://github.com/YashveerR/arc-agi-3-solution
# (research/stuck_review/). When one level has used REVIEW_TOKENS generated
# tokens without being completed, the model is asked to review the ideas it
# rejected on that level and re-test any that were ruled out by an unfair test.
# Nothing is removed from its context; review n on a level fires at n x REVIEW_TOKENS.
#
# Paste as a NEW cell directly AFTER section "1. Environment and submission mode"
# (the cell that applies Franzen's harness patch) and BEFORE "2. Precaching".
# Delete the old fresh-start cell first, if it is still there.
#
# AB_TEST = True is for local measurement runs (bm.n_passes = 2): every game gets
# reviews on one pass and not on the other, and both are logged. Set it to False
# before submitting, so that every game gets reviews.
REVIEW_TOKENS = 40000   # generated tokens on one level per review; 0 switches it off
REVIEW_MAX = 2          # reviews allowed per level
AB_TEST = True

import base64, hashlib, os, subprocess
from pathlib import Path

_PATCH_SHA256 = "{sha}"
_PATCH_B64 = (
{b64}
)
_patch = base64.b64decode("".join(_PATCH_B64.split()))
assert hashlib.sha256(_patch).hexdigest() == _PATCH_SHA256, (
    "stuck-review patch was damaged while copying: re-copy this whole cell"
)
_src = f"{{BUNDLE_DIR}}/src"
_agent_py = Path(_src) / "ARC3-Inference/inference/agent/tool_agent.py"
if "ARC3_FRESH_START_TOKENS" in _agent_py.read_text():
    raise RuntimeError(
        "The old fresh-start cell is still in this notebook: delete it, then run all cells again."
    )
_patch_path = Path("/kaggle/stuck-review.patch")
_patch_path.write_bytes(_patch)
_git = ["git", "apply", "--include=ARC3-Inference/*"]
if subprocess.run(_git + ["-R", "--check", str(_patch_path)], cwd=_src, capture_output=True).returncode == 0:
    print("stuck review: patch already applied")
else:
    subprocess.run(_git + ["-v", str(_patch_path)], cwd=_src, check=True)
os.environ["ARC3_STUCK_REVIEW_TOKENS"] = str(int(REVIEW_TOKENS))
os.environ["ARC3_STUCK_REVIEW_MAX"] = str(int(REVIEW_MAX))
os.environ["ARC3_STUCK_REVIEW_AB"] = "1" if AB_TEST else "0"
print(
    f"stuck review: ARC3_STUCK_REVIEW_TOKENS={{REVIEW_TOKENS}}, ARC3_STUCK_REVIEW_MAX={{REVIEW_MAX}}, "
    f"A/B test {{'ON (local measurement only)' if AB_TEST else 'off'}}"
)
'''


def build() -> str:
    patch = (HERE / "stuck-review.patch").read_bytes()
    encoded = base64.b64encode(patch).decode()
    lines = textwrap.wrap(encoded, 76)
    b64 = "\n".join(f'    "{line}"' for line in lines)
    return CELL_TEMPLATE.format(sha=hashlib.sha256(patch).hexdigest(), b64=b64)


def main() -> None:
    cell = build()
    out = HERE / "notebook_cell.py"
    out.write_text(cell)
    print(f"wrote {out} ({len(cell.splitlines())} lines)")


if __name__ == "__main__":
    main()
