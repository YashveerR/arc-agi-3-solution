# === System-RAM tier for the prompt cache (SGLang hierarchical cache) =========
# From the research branch of https://github.com/YashveerR/arc-agi-3-solution
# (research/hicache/). Flags as used in Lohit Siriki's Milestone 2 notebook.
#
# Prompts pushed out of GPU memory are kept in system RAM and copied back when
# their game returns, instead of being re-processed from scratch.
#
# Paste into section "5. Start serving", directly ABOVE the line
#     # ---- launch detached and wait for health ----
# Set HICACHE_GB = 0 to get Franzen's original server back.
#
# System RAM is 176.9 GiB. Franzen's BF16 PLE table already takes about 96 GB of
# it, so keep this at 32 or less with the BF16 PLE.
HICACHE_GB = 32

if HICACHE_GB > 0:
    args += ["--enable-hierarchical-cache", "--hicache-size", str(int(HICACHE_GB)),
             "--hicache-write-policy", "write_through", "--hicache-io-backend", "kernel"]
    print(f"hicache: system-RAM cache tier of {int(HICACHE_GB)} GB enabled")
else:
    print("hicache: off")
