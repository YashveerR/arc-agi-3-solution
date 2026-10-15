# Sandbox out-of-memory guard

**Status:** built and tested offline (2026-10-14). On in the [12-game run of 2026-10-14](../results/2026-10-14-hicache-12games-guard/README.md), which survived the full run. It never fired there, so no snippet ran away in that run.

## Why

The [12-game run](../results/2026-10-13-hicache-12games-crashed/README.md) lost its model server after 2.1 hours: `scheduler_0 ... crashed with exit code -9`, a SIGKILL from outside the process.

The notebook's `[sys]` lines from that run:
- RAM used rose from 136.5 to 148.4 of 176.9 GiB. Run 3 showed this is a first-hour ramp, not steady growth.
- The last line before the crash, 80 seconds earlier, still showed about 28 GB free.
- After the crash, RAM in use fell to 5.2 GiB. The server held about 143 GB of the 148; the harness and everything else held about 5 GB.

So slow growth alone doesn't explain it: something took 28 GB within 80 seconds. The likeliest cause is a Python snippet the model wrote, for example a search that builds a huge list.
- The sandbox limits CPU time (31 s), file size and open files, but **not memory**.
- One pure-Python process can allocate several GB a second, so 28 GB fits in one 30-second snippet.
- When RAM runs out, Linux's out-of-memory killer takes the process with the highest score, which is roughly its share of RAM. That's the server, at about 80%. The snippet that caused it survives, and every game loses its model.

**Not ruled out:**
- a container memory limit below the 176.9 GiB the machine reports;
- a sudden jump inside the server itself.

If run 3 crashes again with no guard line in the log (see below), the cause is one of these, and the next step is a smaller RAM cache (`HICACHE_GB = 16`).

## The change

[`sandbox-guard.patch`](sandbox-guard.patch) changes `ARC3-Inference/inference/agent/python_tool_sandbox.py` only, behind the switch `ARC3_SANDBOX_OOM_FIRST=1`. With the switch on:

1. **Each sandbox volunteers as the first victim.** It writes 1000 to its own `/proc/self/oom_score_adj` (the maximum, which any process may set on itself without special rights). Every sandbox now outranks the server. Among sandboxes, the one using the most RAM goes first.
2. **One stderr line each time the guard fires:** `[sandbox guard] a Python snippet was killed by SIGKILL ... (kill #n, RAM available now X GiB); its game continues`.
   - Only an outside SIGKILL produces this line. Timeouts are handled elsewhere, and the 31-second CPU limit can't come before the 30-second wall-clock timeout.
   - So these lines confirm or rule out runaway snippets.

**What the game sees.** The killed snippet returns the harness's ordinary `Sandbox process exited unexpectedly.` tool error, and the game carries on.

**When nothing runs out, nothing changes.** Models get exactly the same requests.

With the switch off, the harness behaves exactly as before.

## Using it

Paste [`notebook_cell.py`](notebook_cell.py) as a new cell directly after section 1 of Franzen's notebook (after his harness patch is applied).

The cell does four things:
- checks the patch survived copying (SHA-256);
- applies the patch;
- sets the switch;
- checks the kernel accepts the setting, and prints:
  ```
  sandbox guard: ON (ARC3_SANDBOX_OOM_FIRST=1), kernel accepted oom_score_adj=1000
  ```

Running it twice is safe: the second time it reports `patch already applied`. Rebuild it after changing the patch with `python3 research/sandbox_guard/make_cell.py`.

## Tests (offline, all passing on 2026-10-14)

Run on the competition bundle's tree with Franzen's patch and this patch applied. Paths are in [`../tests/README.md`](../tests/README.md).

**[`tests/test_sandbox_guard.py`](tests/test_sandbox_guard.py)** (4/4 pass):
- switch off: the sandbox keeps the parent's score (0);
- switch on: the score is 1000;
- an ordinary snippet still works;
- a sandbox killed with SIGKILL mid-snippet, as the out-of-memory killer would, returns the ordinary tool error within 0.1 s and logs the guard line.

**[`../tests/e2e_play.py`](../tests/e2e_play.py)** (the real harness playing TAAF's example game against the stand-in model):
- with the switch on, it wins the game, and every sandbox process caught by the watcher showed score 1000 (0 only in the instant before it sets it);
- with the switch on, off, and without the patch at all, the shared model requests are identical (9 of 9, clock values masked);
- no guard lines appear in normal play.

**The notebook cell**, simulated against a fresh copy of the bundle tree:
- it applies the patch;
- the result matches this repository's file byte for byte;
- a second run skips;
- a damaged copy is caught by the checksum.
