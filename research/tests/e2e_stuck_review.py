"""End-to-end check of the stuck review, with no GPU and no real model.

The real harness (HarnessSolver + ToolAgent + Python sandbox + priority gate)
plays TAAF's ExampleGame against the stand-in model in stub_model.py, which keeps
pressing the wrong key until a request contains the review note, then solves.

    python3 research/tests/e2e_stuck_review.py --review-tokens 10000 --out /tmp/on
    python3 research/tests/e2e_stuck_review.py --review-tokens 10000 --stuck-from-level 2 --out /tmp/on_l2
    python3 research/tests/e2e_stuck_review.py --review-tokens 10000 --ab --passes 2 --out /tmp/ab
    python3 research/tests/e2e_stuck_review.py --review-tokens 0 --max-runtime-s 6 --out /tmp/off

Writes requests.jsonl (every request the server received), the run's
benchmark.json and summary.json to --out, and prints the summary. For the
switched-off check, run with --review-tokens 0 once on this tree and once on the
unpatched harness, then compare the two requests.jsonl with compare_requests.py.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stub_model as stub  # noqa: E402

REVIEW_MARK = "REVIEW CHECKPOINT ON LEVEL"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--review-tokens", type=int, required=True, help="0 = feature off")
    ap.add_argument("--review-max", type=int, default=2)
    ap.add_argument("--ab", action="store_true", help="set ARC3_STUCK_REVIEW_AB=1")
    ap.add_argument("--passes", type=int, default=1)
    ap.add_argument("--max-runtime-s", type=float, default=25.0)
    ap.add_argument("--stuck-from-level", type=int, default=1, choices=(1, 2))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    os.environ.update(stub.NOTEBOOK_ENV)
    for key in ("ARC3_STUCK_REVIEW_TOKENS", "ARC3_STUCK_REVIEW_MAX", "ARC3_STUCK_REVIEW_AB"):
        os.environ.pop(key, None)
    if args.review_tokens > 0:
        os.environ["ARC3_STUCK_REVIEW_TOKENS"] = str(args.review_tokens)
        os.environ["ARC3_STUCK_REVIEW_MAX"] = str(args.review_max)
        if args.ab:
            os.environ["ARC3_STUCK_REVIEW_AB"] = "1"
    server, reqs, port = stub.serve(REVIEW_MARK, args.stuck_from_level)
    os.environ["LOCAL_ANALYZER_BASE_URL"] = f"http://127.0.0.1:{port}/v1"
    os.environ["OPENAI_BASE_URL"] = os.environ["LOCAL_ANALYZER_BASE_URL"]

    # imported after the environment is set: some knobs are read at import
    import taaf.benchmark
    import taaf.game_examples
    from inference.framework.solver import HarnessSolver

    args.out.mkdir(parents=True, exist_ok=True)
    job_dir = Path(tempfile.mkdtemp(prefix="stuck_review_job_", dir=args.out))
    solver = HarnessSolver(
        model="local",
        analyzer_timeout=30.0,
        max_runtime_s_per_game=args.max_runtime_s,
        concurrency=max(1, args.passes),
        save_request_logs=True,
    )
    bench = taaf.benchmark.Benchmark(
        label="stuck-review-e2e",
        games=[taaf.game_examples.ExampleGame()],
        solver=solver,
        n_passes=args.passes,
        job_dir=job_dir,
    )
    asyncio.run(bench.run())
    server.shutdown()

    with (args.out / "requests.jsonl").open("w") as f:
        for r in reqs:
            f.write(json.dumps(r) + "\n")
    bench_json = job_dir / "benchmark.json"
    if bench_json.exists():
        (args.out / "benchmark.json").write_text(bench_json.read_text())

    first = next((i for i, r in enumerate(reqs) if stub.has_trigger(r, REVIEW_MARK)), None)
    with_note = reqs[first] if first is not None else None
    note_message = next(
        (m for m in with_note["messages"] if m.get("role") == "user" and REVIEW_MARK in stub.text_of(m)),
        None,
    ) if with_note else None
    summary = {
        "review_tokens": args.review_tokens,
        "ab": args.ab,
        "passes": args.passes,
        "stuck_from_level": args.stuck_from_level,
        "requests": len(reqs),
        "requests_with_note": sum(1 for r in reqs if stub.has_trigger(r, REVIEW_MARK)),
        "private_keys_sent": sorted({k for r in reqs for k in stub.private_keys(r)}),
        "runs": [
            {"state": run.state, "levels_completed": run.levels_completed, "solver_note": run.solver_note}
            for run in bench.game_runs
        ],
        # nothing is dropped: the stuck attempt's tool output is still in the
        # request that carries the note, and the history only grows
        "stuck_output_kept_in_note_request": (
            any(m.get("role") == "tool" and stub.STUCK_MARKER in stub.text_of(m) for m in with_note["messages"])
            if with_note else None
        ),
        "messages_before_and_with_note": (
            [len(reqs[first - 1]["messages"]), len(with_note["messages"])] if first else None
        ),
        "note_message_has_board_image": (
            isinstance(note_message.get("content"), list)
            and any(p.get("type") == "image_url" for p in note_message["content"] if isinstance(p, dict))
            if note_message else None
        ),
        "note_opening": stub.text_of(note_message)[:160] if note_message else None,
    }
    print(json.dumps(summary, indent=2))
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
