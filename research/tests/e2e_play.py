"""General end-to-end run of the real harness against the stand-in model.

Plays TAAF's ExampleGame with Franzen's notebook settings plus any extra
environment settings, and records every model request. Use it to check that a
harness patch still plays a game, and (with --stuck) that it changes nothing
the model is sent:

    python3 research/tests/e2e_play.py --env ARC3_SANDBOX_OOM_FIRST=1 --out /tmp/on
    python3 research/tests/e2e_play.py --stuck --max-runtime-s 6 --out /tmp/a
    python3 research/tests/compare_requests.py /tmp/a/requests.jsonl /tmp/b/requests.jsonl

By default the stand-in model solves the game straight away. With --stuck it
keeps pressing a wrong key until the time runs out. A watcher thread records the
oom_score_adj of every sandbox process it catches (sandbox_oom_scores_seen), so
the out-of-memory guard can be checked inside the real harness.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stub_model as stub  # noqa: E402

NEVER = "\x00never-present\x00"


def _watch_sandboxes(seen: set[int], done: threading.Event) -> None:
    """Poll for sandbox processes (children started with -I -S) and record
    their oom_score_adj. Each snippet is its own short-lived process."""
    me = os.getpid()
    while not done.is_set():
        for p in Path("/proc").iterdir():
            if not p.name.isdigit():
                continue
            try:
                ppid = int((p / "stat").read_text().rsplit(")", 1)[1].split()[1])
                if ppid != me:
                    continue
                cmd = (p / "cmdline").read_bytes().split(b"\0")
                if b"-I" in cmd and b"-S" in cmd:
                    seen.add(int((p / "oom_score_adj").read_text().strip()))
            except (OSError, ValueError, IndexError):
                continue
        time.sleep(0.002)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", action="append", default=[], help="extra KEY=VALUE settings")
    ap.add_argument("--stuck", action="store_true", help="never solve (for request comparisons)")
    ap.add_argument("--max-runtime-s", type=float, default=25.0)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--vllm-format", action="store_true",
                    help="the stand-in answers in vLLM's format (reasoning under `reasoning`)")
    ap.add_argument("--base-url", default="",
                    help="use an already running server instead of starting the stand-in")
    args = ap.parse_args()

    os.environ.update(stub.NOTEBOOK_ENV)
    for item in args.env:
        key, _, value = item.partition("=")
        os.environ[key] = value
    if args.base_url:
        server, reqs = None, []
        os.environ["LOCAL_ANALYZER_BASE_URL"] = args.base_url
    else:
        server, reqs, port = stub.serve(NEVER if args.stuck else "", 1, vllm_format=args.vllm_format)
        os.environ["LOCAL_ANALYZER_BASE_URL"] = f"http://127.0.0.1:{port}/v1"
    os.environ["OPENAI_BASE_URL"] = os.environ["LOCAL_ANALYZER_BASE_URL"]

    import taaf.benchmark
    import taaf.game_examples
    from inference.framework.solver import HarnessSolver

    args.out.mkdir(parents=True, exist_ok=True)
    job_dir = Path(tempfile.mkdtemp(prefix="e2e_play_job_", dir=args.out))
    solver = HarnessSolver(model="local", analyzer_timeout=30.0,
                           max_runtime_s_per_game=args.max_runtime_s, concurrency=1,
                           save_request_logs=True)
    bench = taaf.benchmark.Benchmark(label="e2e-play", games=[taaf.game_examples.ExampleGame()],
                                     solver=solver, n_passes=1, job_dir=job_dir)
    seen: set[int] = set()
    done = threading.Event()
    watcher = threading.Thread(target=_watch_sandboxes, args=(seen, done), daemon=True)
    watcher.start()
    try:
        asyncio.run(bench.run())
    finally:
        done.set()
        watcher.join(timeout=2)
    if server is not None:
        server.shutdown()
    with (args.out / "requests.jsonl").open("w") as f:
        for r in reqs:
            f.write(json.dumps(r) + "\n")
    run = bench.game_runs[0]
    summary = {"env": args.env, "stuck": args.stuck, "vllm_format": args.vllm_format, "base_url": args.base_url,
               "requests": len(reqs), "state": run.state,
               "levels_completed": run.levels_completed, "solver_note": run.solver_note,
               "sandbox_oom_scores_seen": sorted(seen)}
    print(json.dumps(summary, indent=2))
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
