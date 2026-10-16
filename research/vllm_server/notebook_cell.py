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

_SETUP_SHA256 = "fd8da590911e852230c940752404ad661756d83f7c239c71ce677059264fd3ec"
_SETUP_B64 = (
    "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"
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

assert sys.version_info[:2] == (3, 12), f"lordhansolo's runtime is built for Python 3.12, this kernel has {sys.version}"
assert shutil.disk_usage("/tmp").free > 40 * 1024**3, "need about 40 GB free under /tmp for the unpacked runtime"
with socket.socket() as _probe:
    if _probe.connect_ex(("127.0.0.1", int(SERVED_MODEL_PORT))) == 0:
        raise RuntimeError(f"Port {SERVED_MODEL_PORT} is occupied; restart the session before running again")

_setup_path = Path("/tmp/arc3v/vllm_setup.py")
_setup_path.parent.mkdir(parents=True, exist_ok=True)
_setup_path.write_bytes(_setup)
_env = dict(os.environ)
_env.update({
    "TAAF_KAGGLE_WORKING_DIR": str(WORKING_DIR),
    "ARC3V_RUNTIME_DIR": str(VLLM_RUNTIME_DIR),
    "ARC3V_MODEL_DIR": str(VLLM_MODEL_DIR),
    "ARC3V_DRAFT_VOCAB": str(VLLM_DRAFT_VOCAB or ""),
    "ARC3V_SERVED_NAME": SERVED_MODEL_NAME,
    "ARC3V_PORT": str(SERVED_MODEL_PORT),
    "ARC3V_MAX_MODEL_LEN": "147072",          # lordhansolo's; the harness keeps its own 128K budget
    "ARC3V_MAX_NUM_SEQS": str(int(VLLM_MAX_SEQS)),
    "ARC3V_MAX_PIXELS": str(640 * 640),       # Franzen's grid image: 64 x 64 cells, upscaled 10x
    "ARC3V_TEMPLATE_KWARGS": json.dumps({"preserve_thinking": True}),  # as Franzen's SGLang server
    "ARC3V_CHAT_TEMPLATE": VLLM_CHAT_TEMPLATE,
    "ARC3V_GENERATION_CONFIG": VLLM_GENERATION_CONFIG,
})
VLLM_SETUP_LOG = Path(WORKING_DIR) / "vllm-setup.log"
VLLM_SERVER_LOG = Path(WORKING_DIR) / "vllm-openai-server.log"
with open(VLLM_SETUP_LOG, "w") as _log:
    vllm_setup = subprocess.Popen([sys.executable, str(_setup_path)], env=_env, stdout=_log,
                                  stderr=subprocess.STDOUT, start_new_session=True)
print(f"vLLM setup started (pid {vllm_setup.pid}) -> {VLLM_SETUP_LOG}")

# The harness: one game per server slot, and a first-request grace long enough
# for a slow cold start (the runtime unpack plus the weight load took about
# 10 minutes in lordhansolo's run, up to about 30 on a cold disk).
os.environ["ARC3_MAX_ACTIVE_STREAMS"] = str(int(ACTIVE_STREAMS))
os.environ["ARC3_HTTP_RETRY_INITIAL_SECONDS"] = "2400"


def _tail(path, lines=40):
    try:
        return "\n".join(Path(path).read_text(errors="replace").splitlines()[-lines:])
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
        with urllib.request.urlopen(f"http://127.0.0.1:{SERVED_MODEL_PORT}/v1/models", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False


def _setup_failed():
    code = vllm_setup.poll()
    return code is not None and code != 0


def _report_failure():
    print(f"\nvLLM SETUP FAILED (exit code {vllm_setup.returncode}). Last setup log lines:\n{_tail(VLLM_SETUP_LOG, 60)}")
    print(f"\nLast server log lines:\n{_tail(VLLM_SERVER_LOG, 60)}")


# Same release rule as Franzen's cell: wait until SERVER_STARTUP_TIMEOUT after
# the notebook started, then let the benchmark start anyway, because Kaggle
# needs a game action within 15 minutes and the harness's warmup RESET gives it one.
_t0, _last = time.time(), -30
while time.time() - NOTEBOOK_START_TIME < SERVER_STARTUP_TIMEOUT:
    if _setup_failed():
        _report_failure()
        raise RuntimeError("vLLM setup failed; see the log lines above")
    if _ready():
        print(f"\nREADY after {int(time.time() - _t0)}s -> http://127.0.0.1:{SERVED_MODEL_PORT}/v1")
        break
    _elapsed = int(time.time() - _t0)
    if _elapsed - _last >= 30:
        print(f"  {_elapsed}s ...", flush=True)
        _last = _elapsed
    time.sleep(3)
else:
    print(f"\nDEADLINE at {int(time.time() - NOTEBOOK_START_TIME)}s from notebook start; "
          f"releasing the benchmark with the server still loading")


def _watch_setup():
    code = vllm_setup.wait()
    if code != 0:
        _report_failure()
    else:
        print(f"[vllm] setup finished {int(time.time() - _t0)}s after launch; server summary:", flush=True)
        _server_summary()


threading.Thread(target=_watch_setup, name="vllm-setup-watch", daemon=True).start()
