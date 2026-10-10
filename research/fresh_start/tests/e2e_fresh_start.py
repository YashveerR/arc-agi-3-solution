"""End-to-end check of the fresh-start mechanism, with no GPU and no real model.

The real harness (HarnessSolver + ToolAgent + Python sandbox + priority gate)
plays TAAF's ExampleGame (level 1: UP x3, level 2: DOWN x3) against a stand-in
OpenAI-compatible server that behaves like a stuck agent: it keeps pressing the
wrong key and reports 3,000 generated tokens per reply, until a request
contains the fresh-start note, after which it solves the game.

    python3 research/fresh_start/tests/e2e_fresh_start.py --fresh-start-tokens 10000 --out /tmp/on
    python3 research/fresh_start/tests/e2e_fresh_start.py --fresh-start-tokens 0     --out /tmp/off

Writes requests.jsonl (every request the server received) and the run's
benchmark.json to --out, and prints a JSON summary. Environment settings mirror
Daniel Franzen's competition notebook.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import socket
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

TOKENS_PER_REPLY = 3000
FRESH_MARK = "FRESH START ON LEVEL"
SOLVE_CODE = (
    'moves = ["UP", "UP", "UP"] if current_frame.level == 1 else ["DOWN", "DOWN", "DOWN"]\n'
    "action(moves)"
)
# Set in main(): before a fresh start the stand-in solves levels below
# --stuck-from-level and presses the wrong key (no progress) from there on.
STUCK_CODE = ""
STUCK_MARKER = "stuck: wrong key"


def _stuck_code(stuck_from_level: int) -> str:
    wrong = '"DOWN"' if stuck_from_level == 1 else '"UP"'
    return (
        f"if current_frame.level < {stuck_from_level}:\n"
        '    action(["UP", "UP", "UP"] if current_frame.level == 1 else ["DOWN", "DOWN", "DOWN"])\n'
        "else:\n"
        f'    print("{STUCK_MARKER}")\n'
        f"    action({wrong})"
    )

# Franzen's notebook settings that affect the agent loop (serving ones omitted).
NOTEBOOK_ENV = {
    "USE_TF": "0",
    "TRANSFORMERS_NO_TF": "1",
    "LOCAL_ANALYZER_PROVIDER": "vllm",
    "OPENAI_PROVIDER": "vllm",
    "LOCAL_ANALYZER_MODEL_ID": "flashnext",
    "INFERENCE_ANALYZER_MODEL": "flashnext",
    "LOCAL_ANALYZER_APP_NAME": "ARC3 Agent Harness",
    "ARC3_REASONING_HISTORY_KEY": "reasoning_content",
    "LOCAL_ANALYZER_ENABLE_THINKING": "true",
    "LOCAL_ANALYZER_TOOL_STEPS": "0",
    "LOCAL_ANALYZER_TOOL_TIMEOUT": "30",
    "LOCAL_ANALYZER_YIELD_SECONDS": "0",
    "LOCAL_ANALYZER_YIELD_TOKENS": "2048",
    "LOCAL_ANALYZER_TEMPERATURE": "0.7",
    "LOCAL_ANALYZER_TOP_P": "0.95",
    "LOCAL_ANALYZER_TOP_K": "20",
    "LOCAL_ANALYZER_CONTEXT_WINDOW": str((116 + 12) * 1024),
    "LOCAL_ANALYZER_MAX_OUTPUT": str(12 * 1024),
    "ARC3_CONTEXT_DRAIN_TOKENS": str(58 * 1024),
    "ARC3_HISTORY_ASSISTANT_TURNS": "150",
    "ARC3_HISTORY_TURN_DRAIN": "30",
    "ARC3_HISTORY_DRAIN_COALESCE": "1",
    "LOCAL_ANALYZER_TOOL_OUTPUT_TOKENS": "3072",
    "ARC3_MIDDLE_TRUNCATION": "1",
    "ARC3_ACTION_ECHO": "1",
    "ARC3_EXPLAIN_GAMEPLAY_CHANGED": "1",
    "ARC3_NEW_CHANGED_PROMPTS": "1",
    "ARC3_LEVEL_TRANSFER_GUIDANCE": "1",
    "ARC3_ACTION_INFO": "1",
    "ARC3_DEDUPE_MULTICALL_LINE": "1",
    "ARC3_FRAME_DIFF_HINT": "1",
    "MULTIMODAL_CONTEXT": "current_grid",
    "MULTIMODAL_UPSCALE": "10",
    "ARC3_DIFF_IMAGE": "1",
    "ARC3_GAMEOVER_DIFF_IMAGE": "1",
    "ARC3_ANIMATION": "1",
    "ARC3_GUARDS_FROM_LEVEL": "2",
    "ARC3_BATCH_NOOP_BLOCK": "1",
    "ARC3_STALE_STATE_BLOCK": "1",
    "ARC3_MEMORY_SECTIONS": "off",
    "ARC3_PERSISTENT_FUNCTIONS": "1",
    "ARC3_PERSISTENT_FUNCTIONS_SCOPE": "game",
    "ARC3_PERSISTENT_FUNCTIONS_IMPORTS": "1",
    "EXPOSE_UNDO": "on",
    "ARC3_MAX_ACTIVE_STREAMS": "10",
    "ARC3_PRIORITY_REFRESH_QUEUE": "1",
    "ARC3_PRIORITY_PACE": "0",
    "ARC3_PRIORITY_TAIL_FADE": "1",
    "ARC3_PRIORITY_TAIL_FADE_FRACTION": "0.2",
    "ARC3_PRIORITY_TAIL_LOOKUP": "remaining",
    "ARC3_PRIORITY_SCORE_NORMALIZATION": "1",
    "ONLY_RESET_LEVELS": "true",
    "TAAF_RUN_AS_SUBMISSION": "0",
    "MPLBACKEND": "Agg",
}


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _private_keys(value, path="") -> list[str]:
    """Every dict key starting with _arc3 anywhere in a request body."""
    found = []
    if isinstance(value, dict):
        for k, v in value.items():
            if str(k).startswith("_arc3"):
                found.append(f"{path}/{k}")
            found += _private_keys(v, f"{path}/{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            found += _private_keys(v, f"{path}[{i}]")
    return found


def _text_of(message: dict) -> str:
    content = message.get("content")
    if isinstance(content, list):
        return "\n".join(p.get("text", "") for p in content if isinstance(p, dict))
    return str(content or "")


class StubModel(BaseHTTPRequestHandler):
    requests_log: list[dict] = []
    lock = threading.Lock()

    def log_message(self, *args):  # keep test output readable
        pass

    def _send(self, body: dict, status: int = 200) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._send({"object": "list", "data": [{"id": "flashnext", "object": "model"}]})

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length) or b"{}")
        messages = body.get("messages") or []
        fresh = any(FRESH_MARK in _text_of(m) for m in messages if m.get("role") == "user")
        code = SOLVE_CODE if fresh else STUCK_CODE
        with self.lock:
            index = len(self.requests_log)
            self.requests_log.append(body)
        prompt_tokens = max(1, len(json.dumps(messages)) // 4)
        self._send({
            "id": f"stub-{index}",
            "object": "chat.completion",
            "created": 0,
            "model": "flashnext",
            "choices": [{
                "index": 0,
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant",
                    "content": "",
                    "reasoning_content": "stub reasoning: " + ("solve" if fresh else "stuck"),
                    "tool_calls": [{
                        "id": f"call_{index}",
                        "type": "function",
                        "function": {"name": "python", "arguments": json.dumps({"code": code})},
                    }],
                },
            }],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": TOKENS_PER_REPLY,
                "total_tokens": prompt_tokens + TOKENS_PER_REPLY,
            },
        })


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh-start-tokens", type=int, required=True, help="0 = feature off")
    ap.add_argument("--fresh-start-max", type=int, default=1)
    ap.add_argument("--max-runtime-s", type=float, default=25.0)
    ap.add_argument("--stuck-from-level", type=int, default=1, choices=(1, 2))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    global STUCK_CODE
    STUCK_CODE = _stuck_code(args.stuck_from_level)

    port = _free_port()
    os.environ.update(NOTEBOOK_ENV)
    os.environ["LOCAL_ANALYZER_BASE_URL"] = f"http://127.0.0.1:{port}/v1"
    os.environ["OPENAI_BASE_URL"] = os.environ["LOCAL_ANALYZER_BASE_URL"]
    if args.fresh_start_tokens > 0:
        os.environ["ARC3_FRESH_START_TOKENS"] = str(args.fresh_start_tokens)
        os.environ["ARC3_FRESH_START_MAX"] = str(args.fresh_start_max)
    else:
        os.environ.pop("ARC3_FRESH_START_TOKENS", None)
        os.environ.pop("ARC3_FRESH_START_MAX", None)

    server = ThreadingHTTPServer(("127.0.0.1", port), StubModel)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    # imported after the environment is set: some knobs are read at import
    import taaf.benchmark
    import taaf.game_examples
    from inference.framework.solver import HarnessSolver

    args.out.mkdir(parents=True, exist_ok=True)
    job_dir = Path(tempfile.mkdtemp(prefix="fresh_start_job_", dir=args.out))
    solver = HarnessSolver(
        model="local",
        analyzer_timeout=30.0,
        max_runtime_s_per_game=args.max_runtime_s,
        concurrency=1,
        save_request_logs=True,
    )
    bench = taaf.benchmark.Benchmark(
        label="fresh-start-e2e",
        games=[taaf.game_examples.ExampleGame()],
        solver=solver,
        n_passes=1,
        job_dir=job_dir,
    )
    asyncio.run(bench.run())
    server.shutdown()

    reqs = StubModel.requests_log
    with (args.out / "requests.jsonl").open("w") as f:
        for r in reqs:
            f.write(json.dumps(r) + "\n")
    bench_json = job_dir / "benchmark.json"
    if bench_json.exists():
        (args.out / "benchmark.json").write_text(bench_json.read_text())

    run = bench.game_runs[0]
    first_fresh = next(
        (i for i, r in enumerate(reqs)
         if any(FRESH_MARK in _text_of(m) for m in r.get("messages", []) if m.get("role") == "user")),
        None,
    )
    after = reqs[first_fresh] if first_fresh is not None else None
    before = reqs[first_fresh - 1] if first_fresh else None
    summary = {
        "fresh_start_tokens": args.fresh_start_tokens,
        "stuck_from_level": args.stuck_from_level,
        "requests": len(reqs),
        "private_keys_sent": sorted({k for r in reqs for k in _private_keys(r)}),
        "state": run.state,
        "levels_completed": run.levels_completed,
        "actions_per_level": run.actions_per_level,
        "solver_note": run.solver_note,
        "first_request_with_fresh_note": first_fresh,
        "messages_in_request_before_it": len(before["messages"]) if before else None,
        "roles_in_that_request": [m.get("role") for m in after["messages"]] if after else None,
        # the abandoned attempt's tool output must be gone from every later
        # request (the marker is printed only by the stuck branch)
        "stuck_output_in_any_later_request": (
            any(
                m.get("role") == "tool" and STUCK_MARKER in _text_of(m)
                for r in reqs[first_fresh:] for m in r.get("messages", [])
            )
            if first_fresh is not None else None
        ),
        # when stuck on level 2, the turn that solved level 1 must survive
        "earlier_level_solution_kept": (
            any(
                m.get("role") == "tool" and "stop_reason: level_completed" in _text_of(m)
                for m in after["messages"]
            )
            if after is not None and args.stuck_from_level > 1 else None
        ),
    }
    print(json.dumps(summary, indent=2))
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
