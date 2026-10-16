"""Run the vLLM section-5 cell against a fake Kaggle machine, with no GPU.

    python3.12 research/vllm_server/tests/simulate_kaggle.py

Linux, run as root in a throwaway container: it creates /kaggle and
/tmp/vllm-image-runtime and removes them afterwards. Refuses if /kaggle
already exists.

The fake machine has what the cell needs, in the same places as on Kaggle:
- lordhansolo's runtime dataset, with a manifest carrying the pinned identity
  the setup script checks, one image layer and a runtime-patch applier;
- his model folder (index, shards, tokenizer, chat template) and his bundle's
  draft vocabulary;
- Franzen's model folder (tokenizer, chat template, generation config);
- an nvidia-smi that names the RTX PRO 6000.

The image layer's vLLM is a stand-in: `vllm.entrypoints.cli.main` records the
arguments and environment it was started with, prints a loader progress bar and
the KV-cache line, then serves the test stand-in model in vLLM's response format
on the requested port. Everything else is the real cell and the real setup
script: the unpack, the identity checks, the environment, the server command,
the watchdog, the shard prefetcher, the readiness wait and the smoke test.

Cases:
1. normal start: READY, the exact server command, the server environment and
   the harness settings, then Franzen's harness plays a game against the server
   (run with python3.11, which has the harness's packages);
2. slow start past the notebook's deadline: the benchmark is released and the
   background watcher reports the server once it is up;
3. a failing runtime patch: the cell stops with the setup log;
4. a missing input: the cell names the input to add;
5. a damaged copy of the cell: the checksum stops it.
"""
from __future__ import annotations

import ast
import gzip
import io
import json
import os
import shutil
import signal
import subprocess
import sys
import tarfile
import textwrap
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CELL = REPO / "research/vllm_server/notebook_cell.py"
SETUP = REPO / "research/vllm_server/vllm_setup.py"
SIM = Path("/tmp/arc3v-sim")
KAGGLE = Path("/kaggle")
RUNTIME = KAGGLE / "input/datasets/lordhansolo/arc3-vllm-e975732-gdn-recoverssm"
MODEL = KAGGLE / "input/models/lordhansolo/qwen3-8-flash-next-mixed-nvfp4-fp8/pytorch/hf-mixed-mtp-nvfp4/1"
BUNDLE = KAGGLE / "input/datasets/lordhansolo/taaf-kaggle-source"
FRANZEN_MODEL = KAGGLE / "input/models/dfranzen/intel-qwen3.8-flash-next-w4a16-autoround/transformers/default/1"
WORKING = KAGGLE / "working"
DIST = "usr/local/lib/python3.12/dist-packages"

FAKE_VLLM_MAIN = '''
import json, os, sys, time
from pathlib import Path
record = Path(os.environ["ARC3V_SIM_RECORD"])
record.mkdir(parents=True, exist_ok=True)
argv = sys.argv[1:]
(record / "server_argv.json").write_text(json.dumps(argv))
keep = ("VLLM_", "ARC3_CACHE", "PYTHONPATH", "CUDA_HOME", "HF_HUB_OFFLINE", "TORCH_CUDA_ARCH_LIST")
(record / "server_env.json").write_text(json.dumps({k: v for k, v in os.environ.items() if k.startswith(keep)}))
print("fake vLLM starting", flush=True)
for i in range(4):
    print(f"Loading safetensors checkpoint shards: | {i}/3 [00:01<00:01]", flush=True)
    time.sleep(0.3)
time.sleep(float(os.environ.get("ARC3V_SIM_SERVER_DELAY", "0")))
print("(EngineCore pid=1) INFO [kv_cache_utils.py:2485] GPU KV cache size: 1,410,972 tokens, "
      "Maximum concurrency for 147,072 tokens per request: 9.59x", flush=True)
sys.path.insert(0, os.environ["ARC3V_SIM_STUB_DIR"])
import stub_model
port = int(argv[argv.index("--port") + 1])
name = argv[argv.index("--served-model-name") + 1]
server, log, _ = stub_model.serve("", 1, port=port, vllm_format=True, model_name=name)
print(f"fake vLLM serving {name} on {port}", flush=True)
while True:
    time.sleep(0.5)
    (record / "requests.jsonl").write_text("".join(json.dumps(r) + "\\n" for r in list(log)))
'''

APPLIER_OK = '''
import sys
from pathlib import Path
assert Path(sys.argv[1]).is_dir(), sys.argv
print("ARC3 main-e975732 GDN RecoverSSM overlay installed=25, already-patched=0")
'''
APPLIER_FAIL = '''
import sys
print("overlay target missing: vllm/v1/worker/gpu_model_runner.py", file=sys.stderr)
sys.exit(1)
'''


def _pinned_constants() -> dict:
    """The identity constants the setup script checks, read from the script itself."""
    tree = ast.parse(SETUP.read_text())
    wanted = {"FINE_PREFIX_CACHE_RUNTIME_IDENTITY", "FINE_PREFIX_CACHE_PATCH_IDENTITY",
              "FINE_PREFIX_CACHE_REQUIRED_OVERLAYS", "RUNTIME_MANIFEST_FILE_NAME"}
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in wanted:
            out[node.targets[0].id] = ast.literal_eval(node.value)
    return out


def _tar_layer(files: dict[str, str]) -> bytes:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for name, text in files.items():
            data = text.encode()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o755
            tar.addfile(info, io.BytesIO(data))
    return gzip.compress(raw.getvalue())


def build_machine(applier: str = APPLIER_OK) -> None:
    pinned = _pinned_constants()
    for path in (RUNTIME, MODEL, BUNDLE, FRANZEN_MODEL, WORKING, SIM / "bin"):
        path.mkdir(parents=True, exist_ok=True)
    layer = _tar_layer({
        f"{DIST}/vllm/__init__.py": "",
        f"{DIST}/vllm/entrypoints/__init__.py": "",
        f"{DIST}/vllm/entrypoints/cli/__init__.py": "",
        f"{DIST}/vllm/entrypoints/cli/main.py": FAKE_VLLM_MAIN,
        "usr/local/cuda/bin/nvcc": "#!/bin/sh\necho fake nvcc\n",
    })
    blob = RUNTIME / "layer-8-fake.tar.gz.blob"
    blob.write_bytes(layer)
    (RUNTIME / "apply_vllm_main_e975732_arc3_gdn_recoverssm.py").write_text(applier)
    overlays = [{"target": t, **h} for t, h in pinned["FINE_PREFIX_CACHE_REQUIRED_OVERLAYS"].items()]
    manifest = {
        **pinned["FINE_PREFIX_CACHE_RUNTIME_IDENTITY"],
        "torch_version": "2.13.0+cu130",
        "dist_packages": DIST,
        "nvcc": "usr/local/cuda/bin/nvcc",
        "selected_layers": [{"index": 8, "file": blob.name, "size": blob.stat().st_size, "whiteouts": []}],
        "patch": {**pinned["FINE_PREFIX_CACHE_PATCH_IDENTITY"], "overlay_files": overlays},
    }
    (RUNTIME / pinned["RUNTIME_MANIFEST_FILE_NAME"]).write_text(json.dumps(manifest))
    shards = ["model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors", "ple-00001-of-00001.safetensors"]
    for name in shards:
        (MODEL / name).write_bytes(os.urandom(64 * 1024))
    (MODEL / "model.safetensors.index.json").write_text(json.dumps({"weight_map": {f"w{i}": n for i, n in enumerate(shards)}}))
    (MODEL / "config.json").write_text("{}")
    (MODEL / "chat_template.jinja").write_text("{# lordhansolo's copy of the template #}")
    tokenizer = json.dumps({"model": {"type": "BPE"}, "note": "same tokenizer in both checkpoints"})
    (MODEL / "tokenizer.json").write_text(tokenizer)
    (FRANZEN_MODEL / "tokenizer.json").write_text(tokenizer)
    (FRANZEN_MODEL / "chat_template.jinja").write_text("{# Franzen's template #}")
    (FRANZEN_MODEL / "generation_config.json").write_text(json.dumps({"temperature": 0.6, "top_k": 20}))
    (FRANZEN_MODEL / "config.json").write_text("{}")
    vocab = BUNDLE / "src/ARC3-Inference/configs/draft_vocab_32k.json"
    vocab.parent.mkdir(parents=True, exist_ok=True)
    vocab.write_text(json.dumps(list(range(32))))
    smi = SIM / "bin/nvidia-smi"
    smi.write_text("#!/bin/sh\necho 'NVIDIA RTX PRO 6000 Blackwell Server Edition'\n")
    smi.chmod(0o755)


RUNNER = '''
import os, shutil, sys, time, json
from pathlib import Path
from collections import namedtuple
# Section 1 of Franzen's notebook defines these.
MODEL_DIR = {franzen_model!r}
WORKING_DIR = Path("/kaggle/working")
SERVED_MODEL_NAME = "flashnext"
SERVED_MODEL_PORT = 8001
NOTEBOOK_START_TIME = time.time()
SERVER_STARTUP_TIMEOUT = {deadline}
# This container has less free disk than Kaggle's /tmp; the size check is not what is under test.
_Usage = namedtuple("_Usage", "total used free")
shutil.disk_usage = lambda path: _Usage(10**13, 0, 10**13)
cell = open({cell!r}).read()
if {damage}:
    i = cell.index("_SETUP_B64 = (") + 30
    cell = cell[:i] + ("A" if cell[i] != "A" else "B") + cell[i + 1:]
try:
    exec(compile(cell, "cell-5", "exec"))
except BaseException as exc:
    print(f"CELL RAISED {{type(exc).__name__}}: {{exc}}", flush=True)
    sys.exit(3)
print("HARNESS ENV", json.dumps({{k: os.environ.get(k) for k in ("ARC3_MAX_ACTIVE_STREAMS", "ARC3_HTTP_RETRY_INITIAL_SECONDS")}}), flush=True)
# Like the notebook kernel, stay alive while the background watcher reports.
deadline = time.time() + {linger}
while time.time() < deadline and vllm_setup.poll() is None:
    time.sleep(0.5)
time.sleep(1.5)
print("SETUP EXIT", vllm_setup.returncode, flush=True)
'''


def run_cell(*, deadline: int = 600, server_delay: float = 0.0, damage: bool = False, linger: int = 120) -> str:
    runner = SIM / "runner.py"
    runner.write_text(RUNNER.format(franzen_model=str(FRANZEN_MODEL), deadline=deadline, cell=str(CELL),
                                    damage=damage, linger=linger))
    env = dict(os.environ)
    env.update({
        "PATH": f"{SIM / 'bin'}:{env.get('PATH', '')}",
        "TAAF_RUN_AS_SUBMISSION": "0",
        "ARC3V_SIM_RECORD": str(SIM / "record"),
        "ARC3V_SIM_STUB_DIR": str(REPO / "research/tests"),
        "ARC3V_SIM_SERVER_DELAY": str(server_delay),
    })
    result = subprocess.run([sys.executable, str(runner)], env=env, capture_output=True, text=True, timeout=900)
    return result.stdout + result.stderr


def stop_servers() -> None:
    for name in ("vllm-watchdog.pid", "vllm-openai-server.pid"):
        pid_file = WORKING / name
        if pid_file.exists():
            try:
                os.kill(int(pid_file.read_text()), signal.SIGTERM)
            except (OSError, ValueError):
                pass
    time.sleep(1.5)
    subprocess.run(["pkill", "-f", "vllm.entrypoints.cli.main"], check=False)
    subprocess.run(["pkill", "-f", "vllm-watchdog.py"], check=False)
    time.sleep(1.0)


def reset() -> None:
    stop_servers()
    shutil.rmtree(KAGGLE, ignore_errors=True)
    shutil.rmtree(SIM, ignore_errors=True)
    shutil.rmtree("/tmp/vllm-image-runtime", ignore_errors=True)
    shutil.rmtree("/tmp/vllm-image-runtime-cache", ignore_errors=True)
    shutil.rmtree("/tmp/arc3v", ignore_errors=True)


def check(name: str, ok: bool, detail: str = "") -> bool:
    """One result line; the detail is shown only for a failure."""
    print(f"{'PASS' if ok else 'FAIL'} {name}{': ' + detail if detail and not ok else ''}", flush=True)
    return ok


def _arg(argv: list[str], flag: str) -> str | None:
    return argv[argv.index(flag) + 1] if flag in argv else None


def case_normal() -> list[bool]:
    reset()
    build_machine()
    out = run_cell()
    results = [check("normal start: READY before the deadline", "READY after" in out, out[-600:] if "READY after" not in out else "")]
    argv = json.loads((SIM / "record/server_argv.json").read_text())
    senv = json.loads((SIM / "record/server_env.json").read_text())
    spec = json.loads(_arg(argv, "--speculative-config") or "{}")
    expected = {
        "--served-model-name": "flashnext", "--port": "8001", "--max-model-len": "147072",
        "--max-num-seqs": "14", "--mm-processor-kwargs": json.dumps({"max_pixels": 409600}),
        "--default-chat-template-kwargs": json.dumps({"preserve_thinking": True}),
        "--chat-template": str(FRANZEN_MODEL / "chat_template.jinja"),
        "--generation-config": str(FRANZEN_MODEL), "--quantization": "compressed-tensors",
        "--tool-call-parser": "qwen3_coder", "--reasoning-parser": "qwen3",
        "--kv-cache-dtype": "fp8_e4m3", "--gpu-memory-utilization": "0.98",
        "--max-cudagraph-capture-size": "56",
    }
    wrong = {k: (_arg(argv, k), v) for k, v in expected.items() if _arg(argv, k) != v}
    results.append(check("server command has the expected settings", not wrong, json.dumps(wrong)))
    results.append(check("server serves the mixed model folder", argv[:2] == ["serve", str(MODEL)], str(argv[:2])))
    results.append(check("MTP draft with the draft vocabulary",
                         spec == {"method": "mtp", "num_speculative_tokens": 3, "use_local_argmax_reduction": True}
                         and senv.get("VLLM_QWEN4_EXP_DRAFT_VOCAB", "").endswith("configs/draft_vocab_32k.json"),
                         json.dumps(spec)))
    results.append(check("no reasoning_effort, no cache diagnostics, prompt-token details on",
                         "reasoning_effort" not in " ".join(argv) and "--kv-cache-metrics" not in argv
                         and senv.get("ARC3_CACHE_DIAGNOSTICS") == "0" and "--enable-prompt-tokens-details" in argv,
                         json.dumps({"ARC3_CACHE_DIAGNOSTICS": senv.get("ARC3_CACHE_DIAGNOSTICS")})))
    results.append(check("runtime's packages first on the server's path",
                         senv.get("PYTHONPATH", "").split(":")[1].endswith(DIST)
                         and senv.get("VLLM_ARC3_GDN_RECOVERSSM") == "1", senv.get("PYTHONPATH", "")[:200]))
    results.append(check("harness settings: 14 streams, 40-minute first-request grace",
                         'HARNESS ENV {"ARC3_MAX_ACTIVE_STREAMS": "14", "ARC3_HTTP_RETRY_INITIAL_SECONDS": "2400"}' in out))
    results.append(check("setup finished, smoke test ran, watchdog still up",
                         "SETUP EXIT 0" in out and "[vllm] setup finished" in out
                         and "smoke test" in (WORKING / "vllm-setup.log").read_text().lower()
                         and (WORKING / "vllm-watchdog.pid").exists()
                         and _alive(int((WORKING / "vllm-watchdog.pid").read_text())), out[-800:]))
    results.append(check("cell prints the server summary (KV cache size)", "GPU KV cache size: 1,410,972" in out))
    # Franzen's harness, unchanged, against the running server
    play = subprocess.run(
        ["python3.11", str(REPO / "research/tests/e2e_play.py"), "--base-url", "http://127.0.0.1:8001/v1",
         "--out", str(SIM / "play")],
        env={**os.environ, "PYTHONPATH": os.environ.get("ARC3V_HARNESS_PYTHONPATH", "")},
        capture_output=True, text=True, timeout=300)
    summary = json.loads((SIM / "play/summary.json").read_text()) if (SIM / "play/summary.json").exists() else {}
    reqs = [json.loads(l) for l in (SIM / "record/requests.jsonl").read_text().splitlines() if l.strip()]
    harness_reqs = [r for r in reqs if (r.get("tools") or [])]
    history_has_reasoning = any(
        m.get("role") == "assistant" and "stub reasoning" in str(m.get("reasoning_content", ""))
        for r in harness_reqs for m in r.get("messages") or [])
    results.append(check("Franzen's harness wins the example game through the vLLM-format server",
                         summary.get("state") == "won", play.stderr[-800:] if summary.get("state") != "won" else ""))
    results.append(check("harness sends flashnext, thinking on, preserve_thinking, and earlier reasoning back",
                         bool(harness_reqs) and all(r.get("model") == "flashnext" for r in harness_reqs)
                         and all((r.get("chat_template_kwargs") or {}).get("enable_thinking") is True for r in harness_reqs)
                         and all((r.get("chat_template_kwargs") or {}).get("preserve_thinking") is True for r in harness_reqs)
                         and (history_has_reasoning or len(harness_reqs) < 2),
                         f"{len(harness_reqs)} harness requests, reasoning in history: {history_has_reasoning}"))
    return results


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def case_slow_start() -> list[bool]:
    reset()
    build_machine()
    out = run_cell(deadline=4, server_delay=12, linger=120)
    return [check("slow start: benchmark released at the deadline, watcher reports the server later",
                  "DEADLINE at" in out and "releasing the benchmark" in out and "[vllm] setup finished" in out
                  and "SETUP EXIT 0" in out, out[-800:])]


def case_patch_fails() -> list[bool]:
    reset()
    build_machine(applier=APPLIER_FAIL)
    out = run_cell()
    return [check("failing runtime patch: the cell stops and shows why",
                  "CELL RAISED RuntimeError: vLLM setup failed" in out and "overlay target missing" in out, out[-800:])]


def case_missing_input() -> list[bool]:
    reset()
    build_machine()
    shutil.rmtree(KAGGLE / "input/models/lordhansolo")
    out = run_cell()
    return [check("missing model: the cell names the input to add",
                  "CELL RAISED RuntimeError: Add these inputs" in out and "qwen3-8-flash-next-mixed-nvfp4-fp8" in out,
                  out[-500:])]


def case_damaged() -> list[bool]:
    reset()
    build_machine()
    out = run_cell(damage=True)
    return [check("damaged copy: the checksum stops it",
                  "CELL RAISED AssertionError" in out and "damaged while copying" in out, out[-300:])]


def main() -> int:
    if os.geteuid() != 0:
        print("run as root in a throwaway container")
        return 2
    if KAGGLE.exists() and not (KAGGLE / ".arc3v-sim").exists():
        print("/kaggle exists and was not made by this test; refusing")
        return 2
    results = []
    try:
        for case in (case_normal, case_slow_start, case_patch_fails, case_missing_input, case_damaged):
            results += case()
            if KAGGLE.exists():
                (KAGGLE / ".arc3v-sim").touch()
    finally:
        reset()
    print(f"\n{sum(results)}/{len(results)} passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
