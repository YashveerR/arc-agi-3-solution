"""Check the sandbox out-of-memory guard (ARC3_SANDBOX_OOM_FIRST).

    PYTHONPATH=<tree>/src/ARC3-Inference python3 research/sandbox_guard/tests/test_sandbox_guard.py

While a sandboxed snippet is busy, reads the sandbox process's
/proc/<pid>/oom_score_adj from outside: 1000 with the switch on, unchanged
(normally 0) with it off. Also checks an ordinary snippet still works with the
switch on (numpy is not allowed in the sandbox at all), and that when the
out-of-memory killer takes a sandbox (simulated with SIGKILL) the harness gets
an ordinary tool error back, promptly, instead of an exception, and a
"[sandbox guard]" line goes to stderr. Linux only.
"""
from __future__ import annotations

import contextlib
import io
import os
import signal
import sys
import threading
import time
from pathlib import Path

from inference.agent.python_tool_sandbox import run_sandboxed_python

BUSY = "x = 0\nfor i in range(30_000_000):\n    x += i\nprint('done', x > 0)\n"


def _sandbox_children() -> list[int]:
    me = os.getpid()
    out = []
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            stat = (p / "stat").read_text()
            ppid = int(stat.rsplit(")", 1)[1].split()[1])
            cmd = (p / "cmdline").read_bytes()
        except OSError:
            continue
        if ppid == me and b"-I" in cmd and b"-S" in cmd:
            out.append(int(p.name))
    return out


def _score_during(code: str) -> tuple[str | None, dict]:
    """Highest oom_score_adj seen on the sandbox process while it runs (the
    child sets it only after receiving its first message, so keep polling)."""
    seen: list[int] = []
    done = threading.Event()

    def watch():
        while not done.is_set():
            for pid in _sandbox_children():
                try:
                    seen.append(int(Path(f"/proc/{pid}/oom_score_adj").read_text().strip()))
                except (OSError, ValueError):
                    pass
            time.sleep(0.02)

    t = threading.Thread(target=watch)
    t.start()
    try:
        result = run_sandboxed_python(
            code=code, timeout_seconds=30, initial_state={"color_chars": ""},
            action_handler=lambda *a, **k: {"error": "no actions in this test"},
        )
    finally:
        done.set()
        t.join()
    return (str(max(seen)) if seen else None), result


def _killed_midway() -> tuple[float, dict, bool, str]:
    """Kill the sandbox with SIGKILL once it has raised its score, as the
    out-of-memory killer would. Returns (seconds taken, result, killed, stderr)."""
    killed = threading.Event()

    def assassin():
        deadline = time.time() + 20
        while time.time() < deadline and not killed.is_set():
            for pid in _sandbox_children():
                try:
                    if Path(f"/proc/{pid}/oom_score_adj").read_text().strip() == "1000":
                        os.kill(pid, signal.SIGKILL)
                        killed.set()
                        return
                except (OSError, ValueError):
                    pass
            time.sleep(0.02)

    t = threading.Thread(target=assassin)
    t.start()
    start = time.time()
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        result = run_sandboxed_python(
            code=BUSY, timeout_seconds=30, initial_state={"color_chars": ""},
            action_handler=lambda *a, **k: {"error": "no actions in this test"},
        )
    took = time.time() - start
    t.join()
    return took, result, killed.is_set(), err.getvalue()


def main() -> int:
    failures = 0
    baseline = Path("/proc/self/oom_score_adj").read_text().strip()

    os.environ.pop("ARC3_SANDBOX_OOM_FIRST", None)
    score, result = _score_during(BUSY)
    ok = score == baseline and "done True" in (result.get("stdout") or "")
    print(f"{'PASS' if ok else 'FAIL'} switch off: sandbox score {score} (parent {baseline}), stdout {result.get('stdout')!r}")
    failures += not ok

    os.environ["ARC3_SANDBOX_OOM_FIRST"] = "1"
    score, result = _score_during(BUSY)
    ok = score == "1000" and "done True" in (result.get("stdout") or "")
    print(f"{'PASS' if ok else 'FAIL'} switch on: sandbox score {score}, stdout {result.get('stdout')!r}")
    failures += not ok

    score, result = _score_during("import collections\nd = collections.Counter('abcab')\nprint('ordinary ok', d['a'])\n")
    ok = "ordinary ok 2" in (result.get("stdout") or "") and not result.get("error")
    print(f"{'PASS' if ok else 'FAIL'} switch on, ordinary snippet: stdout {result.get('stdout')!r} error {result.get('error')!r}")
    failures += not ok

    try:
        took, result, killed, err = _killed_midway()
        ok = (killed and isinstance(result, dict) and bool(result.get("error")) and took < 10
              and "[sandbox guard]" in err)
        print(f"{'PASS' if ok else 'FAIL'} sandbox killed mid-snippet: returned in {took:.1f}s with error "
              f"{result.get('error')!r}; logged {err.strip()!r}")
    except Exception as exc:  # the harness must not see an exception
        ok = False
        print(f"FAIL sandbox killed mid-snippet: raised {exc!r}")
    failures += not ok
    os.environ.pop("ARC3_SANDBOX_OOM_FIRST", None)
    print(f"\n{4 - failures}/4 passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
