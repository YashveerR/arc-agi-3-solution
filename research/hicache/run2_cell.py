# === Run 2 of the RAM-cache test: admit 12 games to the GPU at once ===========
# From the research branch of https://github.com/YashveerR/arc-agi-3-solution
# (research/hicache/run2.md).
#
# Paste as a NEW cell directly AFTER section "1. Environment and submission mode"
# and BEFORE "2. Precaching".
#
# This cell only tells the harness to admit 12 games. Two other things are needed
# for run 2:
#   - section 5, inside CFG = dict(...): MAXREQ=12, CUDAGRAPH_MAXBS=12, MAMBA_CACHE=68
#   - the RAM-cache snippet in section 5 stays as it is (HICACHE_GB = 32)
ACTIVE_STREAMS = 12

import os
os.environ["ARC3_MAX_ACTIVE_STREAMS"] = str(int(ACTIVE_STREAMS))
print(f"admitted games at once: ARC3_MAX_ACTIVE_STREAMS={os.environ['ARC3_MAX_ACTIVE_STREAMS']}")
