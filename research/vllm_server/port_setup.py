"""Adapt lordhansolo's vLLM setup script to Daniel Franzen's notebook and harness.

    python3 research/vllm_server/port_setup.py

Reads lordhansolo_setup_original.py (his Milestone 2 setup step, copied verbatim
from his public notebook's output) and writes vllm_setup.py. Every change is an
exact text replacement that must match once, so a different original fails here
instead of producing a half-ported script.

What changes, and why:
- Settings that must match Franzen's notebook come from ARC3V_* environment
  variables that the notebook cell sets: the served model name and port the
  harness already uses (flashnext, 8001), the image size Franzen's harness sends
  (640x640, against his 256x256), the number of sequences, the chat template
  and sampling defaults (Franzen's model folder, so prompts and default sampling
  match the SGLang run), the draft vocabulary path, and the input folders.
- The chat-template defaults drop his `reasoning_effort: xhigh`, which
  Franzen's setup never used, so the server is the only thing that changes.
- His test-only cache diagnostics are off: they write one record per request,
  which over a 4-hour run could fill the 20 GB working volume.
- The tail that writes his harness settings is removed; Franzen's notebook sets
  its own in section 1.

Everything else (unpacking his runtime image, the runtime patch and its identity
checks, the environment, the server command, the watchdog that restarts a
crashed server, the shard prefetcher, the readiness wait and the smoke test) is
his code, unchanged.
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINAL_SHA256 = "64d172cd0422acb370e1e2472d32d5a9def11a06ded8cba910a2362a3ac93894"

REPLACEMENTS: list[tuple[str, str]] = [
    (
        "SERVED_MODEL_NAME = 'primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8'\n",
        "SERVED_MODEL_NAME = os.environ['ARC3V_SERVED_NAME']\n",
    ),
    ("VLLM_PORT = 1234\n", "VLLM_PORT = int(os.environ['ARC3V_PORT'])\n"),
    ("VLLM_MAX_MODEL_LEN = 147072\n", "VLLM_MAX_MODEL_LEN = int(os.environ['ARC3V_MAX_MODEL_LEN'])\n"),
    (
        "VLLM_DRAFT_VOCAB = 'configs/draft_vocab_32k.json'\n"
        "VLLM_DRAFT_VOCAB_FILE = (\n"
        "    Path(os.environ['TAAF_KAGGLE_BUNDLE_DIR']) / 'src' / 'ARC3-Inference' / VLLM_DRAFT_VOCAB\n"
        "    if VLLM_DRAFT_VOCAB\n"
        "    else None\n"
        ")\n",
        "# ARC3V: an absolute path found by the notebook cell; empty runs the full-vocabulary draft head.\n"
        "VLLM_DRAFT_VOCAB = os.environ.get('ARC3V_DRAFT_VOCAB', '')\n"
        "VLLM_DRAFT_VOCAB_FILE = Path(VLLM_DRAFT_VOCAB) if VLLM_DRAFT_VOCAB else None\n",
    ),
    ("VLLM_IMAGE_MAX_PIXELS = 65536\n", "VLLM_IMAGE_MAX_PIXELS = int(os.environ['ARC3V_MAX_PIXELS'])\n"),
    ("VLLM_MAX_NUM_SEQS = 14\n", "VLLM_MAX_NUM_SEQS = int(os.environ['ARC3V_MAX_NUM_SEQS'])\n"),
    (
        "RUNTIME_DATASET = resolve_kaggle_dataset_path(RUNTIME_OWNER, RUNTIME_SLUG)\n"
        "MODEL_PATH = resolve_kaggle_model_path(MODEL_SOURCE_PARTS)\n",
        "RUNTIME_DATASET = Path(os.environ['ARC3V_RUNTIME_DIR'])\n"
        "MODEL_PATH = Path(os.environ['ARC3V_MODEL_DIR'])\n",
    ),
    (
        "        '--generation-config',\n        'vllm',\n",
        "        '--generation-config',\n        os.environ.get('ARC3V_GENERATION_CONFIG') or 'vllm',\n",
    ),
    (
        "        '{\"preserve_thinking\": true, \"reasoning_effort\": \"xhigh\"}',\n",
        "        os.environ['ARC3V_TEMPLATE_KWARGS'],\n",
    ),
    (
        "    chat_template = MODEL_PATH / 'chat_template.jinja'\n",
        "    chat_template = Path(os.environ.get('ARC3V_CHAT_TEMPLATE') or (MODEL_PATH / 'chat_template.jinja'))\n",
    ),
    (
        "    enabled = namespace['is_test_run']()\n",
        "    enabled = False  # ARC3V: off; it writes one record per request\n",
    ),
]

# Everything from here to the end of the original writes lordhansolo's harness
# settings into his TAAF setup-env file, which Franzen's notebook does not have.
TAIL_MARKER = "setup_env = {\n    'ARC3_CACHE_DIAGNOSTICS'"
NEW_TAIL = "print('ARC3V: vLLM setup finished; the server stays up under its watchdog', flush=True)\n"


def port(original: str) -> str:
    sha = hashlib.sha256(original.encode()).hexdigest()
    if sha != ORIGINAL_SHA256:
        raise SystemExit(f"original script changed: sha256 {sha}")
    text = original
    for old, new in REPLACEMENTS:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"expected one match, found {count}: {old[:80]!r}")
        text = text.replace(old, new)
    if text.count(TAIL_MARKER) != 1:
        raise SystemExit("tail marker not found exactly once")
    text = text[: text.index(TAIL_MARKER)] + NEW_TAIL
    header = (
        "# Adapted from lordhansolo's ARC Prize 2026 Milestone 2 vLLM setup step by\n"
        "# research/vllm_server/port_setup.py. Every change reads an ARC3V_ setting or is marked ARC3V.\n"
    )
    text = header + text
    ast.parse(text)
    return text


def main() -> None:
    original = (HERE / "lordhansolo_setup_original.py").read_text()
    ported = port(original)
    out = HERE / "vllm_setup.py"
    out.write_text(ported)
    print(f"wrote {out} ({ported.count(chr(10))} lines, sha256 {hashlib.sha256(ported.encode()).hexdigest()[:16]})")


if __name__ == "__main__":
    main()
