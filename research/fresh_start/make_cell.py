"""Build the paste-in Kaggle notebook cell for the fresh-start patch.

    python3 research/fresh_start/make_cell.py

Reads research/fresh_start/fresh-start.patch and writes
research/fresh_start/notebook_cell.py: one self-contained cell that carries the
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
# === Fresh start when stuck =================================================
# From the research branch of https://github.com/YashveerR/arc-agi-3-solution
# (research/fresh_start/). When one level has used FRESH_START_TOKENS generated
# tokens without being completed, that level's conversation is cleared and the
# model starts the level again with fresh eyes.
#
# Paste as a NEW cell directly AFTER section "1. Environment and submission mode"
# (the cell that applies Franzen's harness patch) and BEFORE "2. Precaching".
# Set FRESH_START_TOKENS = 0 to switch the feature off.
FRESH_START_TOKENS = 60000   # generated tokens on one level before a fresh start
FRESH_START_MAX = 1          # fresh starts allowed per level

import base64, hashlib, os, subprocess
from pathlib import Path

_PATCH_SHA256 = "{sha}"
_PATCH_B64 = (
{b64}
)
_patch = base64.b64decode("".join(_PATCH_B64.split()))
assert hashlib.sha256(_patch).hexdigest() == _PATCH_SHA256, (
    "fresh-start patch was damaged while copying: re-copy this whole cell"
)
_patch_path = Path("/kaggle/fresh-start.patch")
_patch_path.write_bytes(_patch)
_src = f"{{BUNDLE_DIR}}/src"
_git = ["git", "apply", "--include=ARC3-Inference/*"]
if subprocess.run(_git + ["-R", "--check", str(_patch_path)], cwd=_src, capture_output=True).returncode == 0:
    print("fresh start: patch already applied")
else:
    subprocess.run(_git + ["-v", str(_patch_path)], cwd=_src, check=True)
os.environ["ARC3_FRESH_START_TOKENS"] = str(int(FRESH_START_TOKENS))
os.environ["ARC3_FRESH_START_MAX"] = str(int(FRESH_START_MAX))
print(f"fresh start: ARC3_FRESH_START_TOKENS={{FRESH_START_TOKENS}}, ARC3_FRESH_START_MAX={{FRESH_START_MAX}}")
'''


def build() -> str:
    patch = (HERE / "fresh-start.patch").read_bytes()
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
