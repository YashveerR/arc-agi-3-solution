# lordhansolo's vLLM server under Franzen's harness

**Status: dropped.** Locally the first Kaggle run passed all four criteria: 10.7M tokens (+27% at equal play time) and a score of 48.71. On the hidden set it scored **23.35**, against 26.5–31.1 for Franzen's setup. lordhansolo's own Milestone 2 entry on this stack scored 23.84. The checkpoint most likely plays worse on unseen games ([result](../results/2026-10-17-vllm-14games/README.md)). Kept as a record.

## Why

- **Speed tweaks on Franzen's SGLang server are near their limit.**
  - 12 games instead of 10 gave +4% tokens.
  - On the hidden set it scored 27.71, inside the usual band ([result](../results/2026-10-14-hicache-12games-guard/README.md)).
  - Top 20 needs about 8 more points.
- **lordhansolo's Milestone 2 server is the biggest speed lever on the table** ([field notes](../field-notes.md)). It runs vLLM with:
  - a mixed NVFP4/FP8 checkpoint whose MTP draft head is built in;
  - a 32K-token draft vocabulary;
  - 98% of GPU memory in use.

  His log shows a 1,410,972-token KV cache against Franzen's 1,011,264 (+40%). Peak decode is 1,135 tokens/s against 946 (+20%).
- **The harness is unchanged.** Franzen's harness was written for an OpenAI-compatible vLLM server in the first place. Its provider setting is already `vllm`.

## What the cell does

[`notebook_cell.py`](notebook_cell.py) replaces the whole of Franzen's section-5 cell. Step by step, it:
1. checks its embedded setup script survived copying (SHA-256);
2. finds lordhansolo's runtime, model and draft vocabulary among the notebook's inputs, and says which input to add if one is missing;
3. compares the two checkpoints' tokenizers. If they match, it uses Franzen's chat template and his model's sampling defaults, so prompts and default sampling are what SGLang produced;
4. starts the setup in the background;
5. sets the harness to 14 games at once, with a 40-minute grace on each game's first request so a slow start can't fail a game;
6. waits for the server the way Franzen's cell does. It releases the benchmark at the notebook's 12-minute deadline, because Kaggle needs a game action within 15 minutes and Franzen's warmup RESET provides one. A background thread then reports the server once it is up, or prints the logs if the setup fails.

### The setup script

[`vllm_setup.py`](vllm_setup.py) is lordhansolo's setup step, copied verbatim from his public notebook's output into [`lordhansolo_setup_original.py`](lordhansolo_setup_original.py). [`port_setup.py`](port_setup.py) then makes the changes below. Each change is an exact text replacement that must match once.

| setting | lordhansolo | here | why |
|---|---|---|---|
| served model name, port | `primitive-ai/...`, 1234 | `flashnext`, 8001 | what Franzen's harness calls |
| image size cap | 65,536 pixels (256×256) | 409,600 (640×640) | Franzen sends 640×640 grid images, which he found was his biggest image gain |
| chat-template defaults | `preserve_thinking`, `reasoning_effort: xhigh` | `preserve_thinking` only | as on Franzen's SGLang server, so only the server changes |
| chat template, sampling defaults | his model's, and vLLM's built-in defaults | Franzen's model folder (if the tokenizers match) | same prompts and defaults as with SGLang |
| test-only cache diagnostics | on in test runs | off | one record per request could fill the 20 GB working volume |
| harness settings he writes at the end | written | removed | Franzen's section 1 sets its own |

**Unchanged:**
- the runtime image unpack, the runtime patch and its identity checks;
- the server environment and command: NVFP4/FP8 weights, fp8 KV cache, MTP with 3 draft tokens, 98% GPU memory, a 2,048-token prefill chunk, and his prefix-cache settings;
- the watchdog that restarts a crashed server, up to 5 times;
- the shard prefetcher, the readiness wait and the smoke test.

**Server logs:** `vllm-openai-server.log`, `vllm-watchdog.log` and `vllm-setup.log` in `/kaggle/working`. [`../serve_stats.py`](../serve_stats.py) now reads vLLM logs as well as SGLang ones.

## Offline checks (2026-10-16, all passing)

**[`tests/simulate_kaggle.py`](tests/simulate_kaggle.py)** runs the real cell and the real setup script on a fake Kaggle machine (15/15 pass).
- **The fake machine** has:
  - lordhansolo's runtime dataset, with the pinned identity the script checks;
  - his model folder and draft vocabulary;
  - Franzen's model folder;
  - an `nvidia-smi` that names the RTX PRO 6000.
- **Its vLLM is a stand-in.** It records how it was started, then serves in vLLM's response format.
- **It checks** the exact server command and environment, the harness settings, the watchdog staying up, and the KV-cache line being reported. Franzen's harness then wins the example game through that server.
- **The four ways it can go wrong:** a slow start past the deadline, a failing runtime patch, a missing input, a damaged copy of the cell.

**Harness against vLLM-format replies** (reasoning under `reasoning` rather than SGLang's `reasoning_content`). It sends exactly the same requests (28 of 28 identical) and sends earlier reasoning back the same way. vLLM at this commit accepts `reasoning_content` in requests and hands it to the chat template ([`chat_utils.py`](https://github.com/vllm-project/vllm/blob/e9757321527ca1ecd514c07c1418dd2c53da3d19/vllm/entrypoints/chat_utils.py)).

**What can't be checked without the GPU:**
- that his runtime loads in Franzen's notebook;
- the real KV size with 640×640 images;
- the throughput;
- **the model's quality.** The mixed NVFP4/FP8 checkpoint is quantized differently from Franzen's W4A16 AutoRound, so it may play better or worse. The run measures that.

## Exact steps

### A. In the notebook editor, add three inputs

Right-hand panel, **Input → + Add Input**:
1. **Datasets:** search `arc3-vllm-e975732-gdn-recoverssm` (by lordhansolo) → Add.
2. **Models:** search `qwen3-8-flash-next-mixed-nvfp4-fp8` (by lordhansolo) → framework **PyTorch**, variation **hf-mixed-mtp-nvfp4**, version **1** → Add.
3. **Datasets:** search `taaf-kaggle-source` (by lordhansolo) → Add. It is only needed for the draft vocabulary file.

Keep all of Franzen's inputs.

### B. Change the notebook

Start from the version that scored 27.71 (12 games, RAM cache, sandbox guard).
1. **Delete** the cell after section 1 that contains `ACTIVE_STREAMS = 12`. The new cell sets the number of games itself.
2. **Keep** the sandbox guard cell.
3. **Section 5 ("Start serving"):**
   - click into the code cell (it starts `# Paste this entire file into the launcher cell.`);
   - select all of its text and delete it;
   - paste the whole of `notebook_cell.py` (about 570 lines).

   This also removes the RAM-cache snippet and the `MAXREQ`/`MAMBA_CACHE` edits, which belong to SGLang.
4. Change nothing else.

### C. Run it

Click **Save Version → Save & Run All**. This is a local run, not a submission.

### D. Check after about 15 minutes

In the log, find section 5's output. It should show these lines, in order:
1. `vLLM runtime: ...`, `vLLM model: ...` and `draft vocabulary: .../draft_vocab_32k.json`;
2. `tokenizers match; using Franzen's chat template and sampling defaults`;
3. either `READY after ...s`, or `DEADLINE ... releasing the benchmark` followed a few minutes later by `[vllm] setup finished ...`;
4. a `GPU KV cache size: ... tokens` line.

**If it says `vLLM SETUP FAILED`** or `Add these inputs`, stop the run and send me the output.

### E. When it finishes (about 4.3 hours), send me

- `benchmark.json`, `vllm-openai-server.log`, `vllm-watchdog.log` and `vllm-setup.log` from the Output tab;
- the `[sys]` lines from the log.

## Judging it (set before the run)

1. **Starts:** the KV cache is at least 1.3M tokens (lordhansolo's was 1.41M with smaller images).
2. **Stable:**
   - `vllm-watchdog.log` shows no server restart;
   - the log shows no `analyzer failed ... consecutively`.
3. **Throughput:** at least 10.5M generated tokens, +14% over the 10-game SGLang mean of 9.19M.
   - Between 9.6M and 10.5M is a small gain, no better than 12 games on SGLang (9.56M).
4. **Quality:** a score of at least 44, the bottom of the usual 10-game range (43.7–47.7).
   - A lower score with more tokens would mean the NVFP4/FP8 checkpoint plays worse.
   - Score alone can't show a gain: local runs have overstated gains before (52.38 locally, 27.71 hidden).

**If 1, 2 and 4 pass and tokens are at least 9.6M,** the next step is a submission of the same version.
