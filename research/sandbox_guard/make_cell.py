"""Build the paste-in Kaggle notebook cell for the sandbox out-of-memory guard.

    python3 research/sandbox_guard/make_cell.py

Reads research/sandbox_guard/sandbox-guard.patch and writes
research/sandbox_guard/notebook_cell.py: one self-contained cell that carries
the patch base64-encoded (so copying it cannot mangle whitespace), checks its
SHA-256, applies it on top of Daniel Franzen's harness patch, switches the
guard on, and checks that this machine's kernel accepts the setting.
Re-running the cell is safe: an already-applied patch is skipped.
"""
from __future__ import annotations

import base64
import hashlib
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent

CELL_TEMPLATE = '''\
# === Sandbox out-of-memory guard ==============================================
# From the research branch of https://github.com/YashveerR/arc-agi-3-solution
# (research/sandbox_guard/). Each Python snippet the model runs is volunteered
# as the first process Linux kills if the machine runs out of RAM, so a runaway
# snippet dies (its game gets an ordinary tool error and carries on) instead of
# the model server. Nothing changes unless RAM actually runs out.
#
# Paste as a NEW cell directly AFTER section "1. Environment and submission mode"
# (the cell that applies Franzen's harness patch) and BEFORE "2. Precaching".
# It can sit before or after the 12-games cell; the order doesn't matter.
import base64, hashlib, os, subprocess, sys
from pathlib import Path

_PATCH_SHA256 = "{sha}"
_PATCH_B64 = (
{b64}
)
_patch = base64.b64decode("".join(_PATCH_B64.split()))
assert hashlib.sha256(_patch).hexdigest() == _PATCH_SHA256, (
    "sandbox-guard patch was damaged while copying: re-copy this whole cell"
)
_src = f"{{BUNDLE_DIR}}/src"
_patch_path = Path("/kaggle/sandbox-guard.patch")
_patch_path.write_bytes(_patch)
_git = ["git", "apply", "--include=ARC3-Inference/*"]
if subprocess.run(_git + ["-R", "--check", str(_patch_path)], cwd=_src, capture_output=True).returncode == 0:
    print("sandbox guard: patch already applied")
else:
    subprocess.run(_git + ["-v", str(_patch_path)], cwd=_src, check=True)
_sandbox_py = Path(_src) / "ARC3-Inference/inference/agent/python_tool_sandbox.py"
assert "ARC3_SANDBOX_OOM_FIRST" in _sandbox_py.read_text(), "sandbox guard: patch did not land"
os.environ["ARC3_SANDBOX_OOM_FIRST"] = "1"

# Check this machine lets a process volunteer itself (it should: raising your
# own score needs no special rights).
_probe = subprocess.run(
    [sys.executable, "-I", "-S", "-c",
     "open('/proc/self/oom_score_adj','w').write('1000');"
     "print(open('/proc/self/oom_score_adj').read().strip())"],
    capture_output=True, text=True,
)
if _probe.stdout.strip() == "1000":
    print("sandbox guard: ON (ARC3_SANDBOX_OOM_FIRST=1), kernel accepted oom_score_adj=1000")
else:
    print("sandbox guard: WARNING, this machine refused the setting, so the guard does nothing here:",
          (_probe.stderr or _probe.stdout).strip()[-300:])
'''


def build() -> str:
    patch = (HERE / "sandbox-guard.patch").read_bytes()
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
