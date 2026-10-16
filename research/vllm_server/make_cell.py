"""Build the paste-in Kaggle notebook cell that replaces Franzen's section 5.

    python3 research/vllm_server/make_cell.py

Reads research/vllm_server/vllm_setup.py (made by port_setup.py) and writes
research/vllm_server/notebook_cell.py: one self-contained cell that carries the
setup script compressed and base64-encoded (so copying it cannot mangle
whitespace, and the cell stays short), checks its
SHA-256, finds lordhansolo's runtime, model and draft vocabulary among the
notebook's inputs, starts the setup in the background and waits for the server
the way Franzen's cell does.
"""
from __future__ import annotations

import base64
import hashlib
import textwrap
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent

CELL_TEMPLATE = '''\
# === 5. Start serving: lordhansolo's vLLM runtime ==============================
# From the research branch of https://github.com/YashveerR/arc-agi-3-solution
# (research/vllm_server/). REPLACES the whole of Franzen's section-5 cell
# (SGLang). The setup step is lordhansolo's, from his public Milestone 2
# notebook: his packed vLLM runtime, his mixed NVFP4/FP8 checkpoint with its
# built-in MTP head, and his watchdog. Changed only where Franzen's harness
# needs it: the model name and port it already uses, its 640x640 images, the
# chat template and sampling defaults of Franzen's model folder, and no
# reasoning_effort, so the server is the only thing that differs.
#
# Needs three inputs added to the notebook (Add Input):
#   - dataset  lordhansolo/arc3-vllm-e975732-gdn-recoverssm   (the vLLM runtime)
#   - model    lordhansolo/qwen3-8-flash-next-mixed-nvfp4-fp8 (PyTorch, hf-mixed-mtp-nvfp4)
#   - dataset  lordhansolo/taaf-kaggle-source                (only for its draft vocabulary)
VLLM_MAX_SEQS = 14     # requests the server runs at once (lordhansolo used 14)
ACTIVE_STREAMS = 14    # games the harness admits at once; keep equal to VLLM_MAX_SEQS

import base64, hashlib, json, os, shutil, socket, subprocess, sys, threading, time, urllib.request, zlib
from pathlib import Path

_SETUP_SHA256 = "{sha}"
_SETUP_B64 = (
{b64}
)
try:
    _setup = zlib.decompress(base64.b64decode("".join(_SETUP_B64.split())))
except Exception:
    _setup = b""
assert hashlib.sha256(_setup).hexdigest() == _SETUP_SHA256, (
    "vLLM setup script was damaged while copying: re-copy this whole cell"
)


def _first_dir(candidates, must_contain):
    for path in candidates:
        if path.is_dir() and all((path / name).exists() for name in must_contain):
            return path
    return None


_INPUT = Path("/kaggle/input")
VLLM_RUNTIME_DIR = _first_dir(
    [_INPUT / "datasets/lordhansolo/arc3-vllm-e975732-gdn-recoverssm", _INPUT / "arc3-vllm-e975732-gdn-recoverssm"],
    ["runtime-manifest.json"],
)
VLLM_MODEL_DIR = _first_dir(
    sorted((_INPUT / "models/lordhansolo/qwen3-8-flash-next-mixed-nvfp4-fp8").glob("*/hf-mixed-mtp-nvfp4/*"))
    + sorted((_INPUT / "qwen3-8-flash-next-mixed-nvfp4-fp8").glob("*/hf-mixed-mtp-nvfp4/*")),
    ["config.json", "model.safetensors.index.json"],
)
_missing = [name for name, path in [
    ("dataset lordhansolo/arc3-vllm-e975732-gdn-recoverssm", VLLM_RUNTIME_DIR),
    ("model lordhansolo/qwen3-8-flash-next-mixed-nvfp4-fp8 (hf-mixed-mtp-nvfp4)", VLLM_MODEL_DIR),
] if path is None]
if _missing:
    raise RuntimeError("Add these inputs to the notebook (Add Input), then run all cells again: " + "; ".join(_missing))
_vocab = []
for _root in (_INPUT / "datasets/lordhansolo/taaf-kaggle-source", _INPUT / "taaf-kaggle-source"):
    if _root.is_dir():
        _vocab += sorted(_root.glob("**/ARC3-Inference/configs/draft_vocab_32k.json"))
VLLM_DRAFT_VOCAB = _vocab[0] if _vocab else None
print("vLLM runtime:", VLLM_RUNTIME_DIR)
print("vLLM model:  ", VLLM_MODEL_DIR)
print("draft vocabulary:", VLLM_DRAFT_VOCAB or "not found (dataset lordhansolo/taaf-kaggle-source not added); using the full-vocabulary draft head")

# Prompts and default sampling come from Franzen's model folder, as with SGLang,
# if both checkpoints share one tokenizer.
def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).is_file() else None
_tok_franzen, _tok_vllm = _sha(Path(MODEL_DIR) / "tokenizer.json"), _sha(VLLM_MODEL_DIR / "tokenizer.json")
_same_tokenizer = _tok_franzen is not None and _tok_franzen == _tok_vllm
_template = Path(MODEL_DIR) / "chat_template.jinja"
if _same_tokenizer and _template.is_file():
    VLLM_CHAT_TEMPLATE, VLLM_GENERATION_CONFIG = str(_template), str(MODEL_DIR)
    print("tokenizers match; using Franzen's chat template and sampling defaults")
else:
    VLLM_CHAT_TEMPLATE, VLLM_GENERATION_CONFIG = "", ""
    print("WARNING: tokenizers differ (or Franzen's template is missing); using the vLLM model's own chat template")
print("same chat template file in both models:", _sha(_template) == _sha(VLLM_MODEL_DIR / "chat_template.jinja"))

assert sys.version_info[:2] == (3, 12), f"lordhansolo's runtime is built for Python 3.12, this kernel has {{sys.version}}"
assert shutil.disk_usage("/tmp").free > 40 * 1024**3, "need about 40 GB free under /tmp for the unpacked runtime"
with socket.socket() as _probe:
    if _probe.connect_ex(("127.0.0.1", int(SERVED_MODEL_PORT))) == 0:
        raise RuntimeError(f"Port {{SERVED_MODEL_PORT}} is occupied; restart the session before running again")

_setup_path = Path("/tmp/arc3v/vllm_setup.py")
_setup_path.parent.mkdir(parents=True, exist_ok=True)
_setup_path.write_bytes(_setup)
_env = dict(os.environ)
_env.update({{
    "TAAF_KAGGLE_WORKING_DIR": str(WORKING_DIR),
    "ARC3V_RUNTIME_DIR": str(VLLM_RUNTIME_DIR),
    "ARC3V_MODEL_DIR": str(VLLM_MODEL_DIR),
    "ARC3V_DRAFT_VOCAB": str(VLLM_DRAFT_VOCAB or ""),
    "ARC3V_SERVED_NAME": SERVED_MODEL_NAME,
    "ARC3V_PORT": str(SERVED_MODEL_PORT),
    "ARC3V_MAX_MODEL_LEN": "147072",          # lordhansolo's; the harness keeps its own 128K budget
    "ARC3V_MAX_NUM_SEQS": str(int(VLLM_MAX_SEQS)),
    "ARC3V_MAX_PIXELS": str(640 * 640),       # Franzen's grid image: 64 x 64 cells, upscaled 10x
    "ARC3V_TEMPLATE_KWARGS": json.dumps({{"preserve_thinking": True}}),  # as Franzen's SGLang server
    "ARC3V_CHAT_TEMPLATE": VLLM_CHAT_TEMPLATE,
    "ARC3V_GENERATION_CONFIG": VLLM_GENERATION_CONFIG,
}})
VLLM_SETUP_LOG = Path(WORKING_DIR) / "vllm-setup.log"
VLLM_SERVER_LOG = Path(WORKING_DIR) / "vllm-openai-server.log"
with open(VLLM_SETUP_LOG, "w") as _log:
    vllm_setup = subprocess.Popen([sys.executable, str(_setup_path)], env=_env, stdout=_log,
                                  stderr=subprocess.STDOUT, start_new_session=True)
print(f"vLLM setup started (pid {{vllm_setup.pid}}) -> {{VLLM_SETUP_LOG}}")

# The harness: one game per server slot, and a first-request grace long enough
# for a slow cold start (the runtime unpack plus the weight load took about
# 10 minutes in lordhansolo's run, up to about 30 on a cold disk).
os.environ["ARC3_MAX_ACTIVE_STREAMS"] = str(int(ACTIVE_STREAMS))
os.environ["ARC3_HTTP_RETRY_INITIAL_SECONDS"] = "2400"


def _tail(path, lines=40):
    try:
        return "\\n".join(Path(path).read_text(errors="replace").splitlines()[-lines:])
    except OSError:
        return ""


def _server_summary():
    keys = ("gpu kv cache size", "maximum concurrency", "smoke test", "generated:", "runtime ready", "draft vocab")
    try:
        text = VLLM_SETUP_LOG.read_text(errors="replace").splitlines()
    except OSError:
        return
    for line in text:
        if any(k in line.lower() for k in keys):
            print("  " + line[:300])


def _ready():
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{{SERVED_MODEL_PORT}}/v1/models", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False


def _setup_failed():
    code = vllm_setup.poll()
    return code is not None and code != 0


def _report_failure():
    print(f"\\nvLLM SETUP FAILED (exit code {{vllm_setup.returncode}}). Last setup log lines:\\n{{_tail(VLLM_SETUP_LOG, 60)}}")
    print(f"\\nLast server log lines:\\n{{_tail(VLLM_SERVER_LOG, 60)}}")


# Same release rule as Franzen's cell: wait until SERVER_STARTUP_TIMEOUT after
# the notebook started, then let the benchmark start anyway, because Kaggle
# needs a game action within 15 minutes and the harness's warmup RESET gives it one.
_t0, _last = time.time(), -30
while time.time() - NOTEBOOK_START_TIME < SERVER_STARTUP_TIMEOUT:
    if _setup_failed():
        _report_failure()
        raise RuntimeError("vLLM setup failed; see the log lines above")
    if _ready():
        print(f"\\nREADY after {{int(time.time() - _t0)}}s -> http://127.0.0.1:{{SERVED_MODEL_PORT}}/v1")
        break
    _elapsed = int(time.time() - _t0)
    if _elapsed - _last >= 30:
        print(f"  {{_elapsed}}s ...", flush=True)
        _last = _elapsed
    time.sleep(3)
else:
    print(f"\\nDEADLINE at {{int(time.time() - NOTEBOOK_START_TIME)}}s from notebook start; "
          f"releasing the benchmark with the server still loading")


def _watch_setup():
    code = vllm_setup.wait()
    if code != 0:
        _report_failure()
    else:
        print(f"[vllm] setup finished {{int(time.time() - _t0)}}s after launch; server summary:", flush=True)
        _server_summary()


threading.Thread(target=_watch_setup, name="vllm-setup-watch", daemon=True).start()
'''


def build() -> str:
    script = (HERE / "vllm_setup.py").read_bytes()
    encoded = base64.b64encode(zlib.compress(script, 9)).decode()
    lines = textwrap.wrap(encoded, 76)
    b64 = "\n".join(f'    "{line}"' for line in lines)
    return CELL_TEMPLATE.format(sha=hashlib.sha256(script).hexdigest(), b64=b64)


def main() -> None:
    cell = build()
    out = HERE / "notebook_cell.py"
    out.write_text(cell)
    print(f"wrote {out} ({len(cell.splitlines())} lines)")


if __name__ == "__main__":
    main()
