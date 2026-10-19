# Field notes: what other teams report

Gathered 2026-10-12 from Kaggle discussion threads (pasted in by hand, since the forum is not reachable from the research environment), GitHub and news. Most claims are unverified.

## Leaderboard (2026-10-12, public, top 20)

| | score |
|---|---|
| 1. Yi-Chia Chen | 62.96 |
| 2. Tufa Labs | 56.52 |
| 3. mtg | 45.00 |
| 5th place (prize line) | 42.55 |
| 20th | 36.49 |

**Places 8–20:** 15 teams sit between 36.5 and 39.1.

**Repeat submissions inflate public scores.**
- Many teams have 70–100+ entries.
- One public score varies by roughly ±2.3 points (from three scores of Franzen's notebook: 27.89, 31.06, 26.52).
- So the best of about 80 entries sits about 5–6 points above a team's true level.
- The final ranking uses the other half of the hidden games.

**Some teams score high with few entries**, which points to real gains:
- Majkel1337: 42.66 in 14
- fshindo: 38.20 in 11
- _hans: 37.07 in 8
- Nhan Duc Nguyen: 38.84 in 16

## Where the gains are coming from: inference engineering

**"Comparing the Milestone 2 winning solutions"** (Tong Hui Kang, Kaggle discussion). All three winners run the Duck harness and Qwen3.8-Flash-Next.

| | dfranzen (27.89) | lordhansolo (23.84) | sirikilohit (22.53) |
|---|---|---|---|
| quantization | Intel W4A16 AutoRound + BF16 PLE, separate INT4 MTP draft | primitive-ai NVFP4 + FP8 mixed, built-in MTP head | Intel W4A16 + RadixArk FP8 PLE, NVFP4 MTP draft |
| server | SGLang Pennyroyal v2.5.3 | vLLM 0.29.1rc1 nightly | SGLang Pennyroyal v2.5.0 |
| KV pool (tokens) | 1,011,264 | **1,417,100** | 1,004,288 + **48 GB host-RAM tier for KV and Mamba state** |
| GPU memory left free | 4.25 GB | 1.90 GB | 3.17 GB |
| context (server / harness) | 139K / 131K | 147K / 127K | 70K / 70K |
| games streaming | 10 | 14 | 16 |
| peak decode tokens/s | 946 | **1,135** | **1,159** |
| scheduling | priority gate; a game keeps its slot until its next history trim | 3,918 s cap per game | 2,400 s slice per game, then UCB on levels cleared per token |
| carried across levels | history, Python functions | history, saved Python modules | history; the rule and last 30 winning actions of each solved level pinned in the system prompt |

**What the thread's comments add:**
- **rellik13:** "the kv pool sat somewhere between 91-97% full and requests queued for cache space, so the memory was the actual limit." Switching to fp8 KV and spending the freed memory on history took him from 14.5 to 22.5. This matches our [11-stream result](results/2026-10-11-streams-11/README.md).
- **rellik13, on prompts:** harness changes that helped were "simply to not mislead the agent". Examples: UNDO instead of ACTION7, "level restarted" instead of "game over", and removing lines that tell the agent to ignore the budget bar.
- **xz:** NVFP4 KV showed "very little NLL penalty" in his tests. That would roughly double KV capacity over fp8, but it is untested at 60–100K contexts.
- **Son Pham (7th):** pruning and changing the serving setup is "an entire untapped area to explore".
- **Yi-Chia Chen (1st):** "excited to see how high a score people can achieve by combining these three winning notebooks!"
- **Nhan Duc Nguyen (10th):** the public notebooks share the same inference improvements, so the next phase is likely harness work or a new open model.

## Our own finding: the Milestone 2 gap is mostly the serving stack (2026-10-18)

- Franzen's harness on lordhansolo's vLLM server and mixed NVFP4/FP8 checkpoint scored **23.35** on the hidden set. lordhansolo's own harness on that stack scored 23.84.
- Franzen's harness on his own SGLang server and W4A16 AutoRound checkpoint averages 28.5.
- So the quantization or server, not the harness, accounts for most of the 27.89 against 23.84 gap in Milestone 2.
- Locally the same stack looked better: +27% tokens, and 48.71 against 44.9 at equal play time. See the [result](results/2026-10-17-vllm-14games/README.md).

## Forum threads pasted 2026-10-19

**"What are your agents scoring on the 25 public games?"** (Reki)
- **Everyone sees local gains fail to carry over.** Examples:
  - Fususu: 22.26 locally, 5.37 on the leaderboard.
  - Scott Le Grand: 11.04 locally, 2.71.
  - Nick Pellegrin: "doing better on the public set ... correlates to weaker private scores".
  - Giang Rita: "I do not believe in scores anymore".
- **CPMP (10th):** "We achieved 100% months ago on 25 public games ... any number not from the competition leaderboard is irrelevant."
- **Son Pham (3rd):** submit early. Local games miss "resource constraints, harder games, new mechanics".
- **Scott Le Grand:** the stock Duck client on NVFP4 with 16 sequences "will get you to the brink of the top 10%, but all of my harness engineering beyond that has been utterly useless". He calls the final ranking a lottery ticket: the two selected submissions are scored on the other 55 hidden games.
- **Mark Barney (3rd):** about seven of the public games ("the Slippery Seven") are extremely hard for every current solution.

**"Which is a better choice for training, Qwen3.8-27B or Qwen3.8-Flash-Next?"** (Slow∞Loop, 3rd)
- **The top teams train.**
  - Slow∞Loop trains Qwen3.8-27B with SFT and RL, because Flash-Next's mixture-of-experts makes training unstable. Scores grow slowly.
  - For Flash-Next he uses QLoRA 4-bit, FSDP2 and PLE CPU offload on 2 × 96 GB GPUs.
- **Scott Le Grand:** +2 points on the public games from SFT on 27B; nothing from Flash-Next. He is running RL on a borrowed B300, with a dense reward: the maximum score still attainable from the current state.

**"Things Claude Code has said"** (Scott Le Grand): speculation only.
- Yi-Chia Chen, 1st, is said to distil into a smaller model, and may have much more compute.
- Her earlier AIMO write-up is recommended reading.

**What this means for this fork:**
- **Training is out of reach on Kaggle's weekly GPU quota.** The top teams train on outside hardware.
- **Our finding matches the forum:** only submissions measure score.
- **Within one submission, the public and private scores come from the same 9-hour run on 110 games.** Run-wide problems (a slow start, a crash) hit both halves alike. So among submissions of one configuration, the higher public score is a slightly better pick, even though game-level luck is independent between the halves.

## What did not work for others

**Fine-tuning, in any form, on this hardware and timeline.**
- Training Flash-Next does not fit on the RTX PRO 6000; one person used a full H200 node.
- SFT with frontier teachers (Qwen Max, Astra), synthetic game variants, and STaR on the model's own winning trajectories all gave no meaningful hidden-set gain.
- One report: +2 on the public games that did not carry over to the hidden set.
- An early STaR LoRA on Qwen3.6-27B (1.25 → 1.94) predates the current models.
- Chollet has cautioned that the 25 public games are not meant as training data.
- Distilling from OpenAI outputs may conflict with their terms and with open-source release.
- LamDang's fork is building QLoRA at 120K context: about 43 minutes per sample on this GPU, with no results yet.

**Other models.** Gemma 4 31B was worse at logic and coding. Qwen 27B variants fall clearly short of Flash-Next.

**Multi-role LLM setups** (observer, theorist, actor, advisor): better reasoning, but about 5× the tokens.

**Symbolic game decoders and strategy libraries:** they introduce game-specific bias.

**Concurrency above about 16:** throughput saturates. Prefill and decode start interfering, and the KV cache fills.

**Expert pruning to 256 of 512 experts (REAP):** the score fell from 68.97 to 45.95 in LamDang's runs. Milder pruning or merging is untested. One example is WaveCut/Qwen3.8-Flash-Next-REAM-288 on Hugging Face.

## Consequences for this fork

**The binding constraint is GPU memory for the KV cache.** That is our measurement and the field's. Candidates, in order:
1. **Host-RAM KV tier** (sirikilohit): evicted prefixes come back from host RAM instead of being re-processed. That attacks the 9.3M re-processed tokens per run, and may make 11–14 streams viable. FP8 PLE frees the host RAM it needs.
2. **lordhansolo's serving:** NVFP4/FP8 mixed weights, a built-in MTP head and higher memory utilisation give a 40% larger KV pool and 20% higher peak decode.
3. **NVFP4 KV,** if the server supports it on this GPU.
4. **A pruned or merged model,** for much more memory, but with a quality risk.
5. **Prompt wording that does not mislead** (rellik13): cheap, small.

**How to judge serving changes:** tokens per hour and re-processed prompt tokens (`research/serve_stats.py`) decide first. Score is checked afterwards with daily submissions alternating against Franzen's configuration.

## Exact server settings from the two other Milestone 2 notebooks (received 2026-10-12)

### lordhansolo: vLLM nightly, launched from his TAAF bundle's setup commands

Server command:

```
vllm serve qwen3-8-flash-next-mixed-nvfp4-fp8 (primitive-ai NVFP4/FP8 mixed, built-in MTP)
  --max-model-len 147072 --max-num-seqs 14 --max-num-batched-tokens 2048
  --async-scheduling --enable-chunked-prefill --enable-prefix-caching
  --gpu-memory-utilization 0.98 --kv-cache-dtype fp8_e4m3 --mamba-ssm-cache-dtype bfloat16
  --speculative-config {"method": "mtp", "num_speculative_tokens": 3}
  --cpu-offload-params embed_tokens --engram-config {"cpu_offload": true}
  --mm-processor-kwargs {"max_pixels": 65536}
  --default-chat-template-kwargs {"preserve_thinking": true, "reasoning_effort": "xhigh"}
```

**Notes:**
- GPU KV cache: 1,410,972 tokens.
- His images are capped at 65,536 pixels, about 256×256. Franzen uses 640×640 (10× upscale), which he reports as his biggest image-related gain.
- His `reasoning_effort: xhigh` is untested with Franzen's harness.

### Lohit Siriki: SGLang Pennyroyal v2.5.0, the same server family as Franzen's

His version notes:
- **v18.1gc:** FP8 KV, 16 games, trims 57,344 → 45,056 (was 36,864 → 26,624).
- **v18.1gs:** deleted two phrases from the prompt, "the edge bar is the action budget; do not tell the model to ignore it".

Server arguments:

```
--quantization auto-round --kv-cache-dtype fp8_e4m3 --mem-fraction-static 0.97
--context-length 69632 --max-running-requests 16 --chunked-prefill-size 4096
--mamba-radix-cache-strategy extra_buffer --max-mamba-cache-size 80
--speculative-algorithm NEXTN (NVFP4 MTP draft, modelopt_fp4)
--enable-hierarchical-cache --hicache-size 48 --hicache-write-policy write_through --hicache-io-backend kernel
```

**Notes:**
- KV pool: 1,004,288 tokens on the GPU, plus the 48 GB system-RAM tier.
- The boot log reports 176.9 GiB of system RAM and 48 CPUs.
- His harness diverges heavily from Franzen's: a UCB scheduler, a reasoning ledger, solved-level memory, and a port of the Wang/Ludvig harness. It scored lower (22.53 against 27.89), so only the serving parts are worth borrowing. The [hierarchical-cache experiment](hicache/README.md) does that.

## Sources

- Kaggle discussions (pasted 2026-10-12):
  - "Comparing the Milestone 2 winning solutions" (Tong Hui Kang)
  - "What Have You Tried So Far?" (Fususu)
  - "Finetuning a model (SFT or RL) on the RTX 6000 Pro?" (Nick Pellegrin)
  - "Open-sourcing winning-trajectory datasets + a LoRA for the duck harness" (manas joshi)
- LamDang/arc-agi-3-solution-da-fr: PRs [#10](https://github.com/LamDang/arc-agi-3-solution-da-fr/pull/10), [#19](https://github.com/LamDang/arc-agi-3-solution-da-fr/pull/19), [#24](https://github.com/LamDang/arc-agi-3-solution-da-fr/pull/24)
- [WaveCut/Qwen3.8-Flash-Next-REAM-288](https://huggingface.co/WaveCut/Qwen3.8-Flash-Next-REAM-288)
- [TechTimes, 2026-10-06](https://www.techtimes.com/articles/328542/20261006/arc-agi-3-scaffolding-beats-model-upgrades-same-ai-two-settings-49x-score-gain.htm)
