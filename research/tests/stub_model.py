"""Shared pieces for end-to-end tests that run the real harness without a GPU.

- NOTEBOOK_ENV: Daniel Franzen's competition-notebook settings that affect the
  agent loop (serving settings omitted).
- serve(trigger): a stand-in OpenAI-compatible model server. It behaves like a
  stuck agent - presses the wrong key and reports 3,000 generated tokens per
  reply - until a user message in the request contains `trigger`, after which
  it solves TAAF's ExampleGame (level 1: UP x3, level 2: DOWN x3).
"""
from __future__ import annotations

import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKENS_PER_REPLY = 3000
STUCK_MARKER = "stuck: wrong key"
SOLVE_CODE = (
    'moves = ["UP", "UP", "UP"] if current_frame.level == 1 else ["DOWN", "DOWN", "DOWN"]\n'
    "action(moves)"
)

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


def stuck_code(stuck_from_level: int) -> str:
    """Solves levels below `stuck_from_level`, presses the wrong key from there on."""
    wrong = '"DOWN"' if stuck_from_level == 1 else '"UP"'
    return (
        f"if current_frame.level < {stuck_from_level}:\n"
        '    action(["UP", "UP", "UP"] if current_frame.level == 1 else ["DOWN", "DOWN", "DOWN"])\n'
        "else:\n"
        f'    print("{STUCK_MARKER}")\n'
        f"    action({wrong})"
    )


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def text_of(message: dict) -> str:
    content = message.get("content")
    if isinstance(content, list):
        return "\n".join(p.get("text", "") for p in content if isinstance(p, dict))
    return str(content or "")


def private_keys(value, path: str = "") -> list[str]:
    """Every dict key starting with _arc3 anywhere in a request body."""
    found = []
    if isinstance(value, dict):
        for k, v in value.items():
            if str(k).startswith("_arc3"):
                found.append(f"{path}/{k}")
            found += private_keys(v, f"{path}/{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            found += private_keys(v, f"{path}[{i}]")
    return found


def has_trigger(body: dict, trigger: str) -> bool:
    return any(trigger in text_of(m) for m in body.get("messages") or [] if m.get("role") == "user")


def serve(trigger: str, stuck_from_level: int) -> tuple[ThreadingHTTPServer, list[dict], int]:
    """Start the stand-in server on a free port. Returns (server, request log, port)."""
    log: list[dict] = []
    lock = threading.Lock()
    stuck = stuck_code(stuck_from_level)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep test output readable
            pass

        def _send(self, body: dict) -> None:
            data = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self._send({"object": "list", "data": [{"id": "flashnext", "object": "model"}]})

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}")
            solve = has_trigger(body, trigger)
            with lock:
                index = len(log)
                log.append(body)
            prompt_tokens = max(1, len(json.dumps(body.get("messages") or [])) // 4)
            code = SOLVE_CODE if solve else stuck
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
                        "reasoning_content": "stub reasoning: " + ("solve" if solve else "stuck"),
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

    port = free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, log, port
