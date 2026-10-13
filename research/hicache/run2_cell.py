# === Admit 12 games to the GPU at once (run 2 of the RAM-cache test) ========
# From the research branch of https://github.com/YashveerR/arc-agi-3-solution
# (research/throughput/).
#
# Section 1 admits 10 games, matching the server's limit of 10 running requests.
# A game keeps its slot while it runs Python between model requests, so on
# average only about 8.6 of the 10 server slots are generating. Admitting an
# 11th game lets it fill those gaps. The server still runs at most 10 requests
# at once (MAXREQ in section 5 is unchanged), so its batch size never grows.
#
# Paste as a NEW cell directly AFTER section "1. Environment and submission mode"
# and BEFORE "2. Precaching". Delete the stuck-review cell if it is still there.
# Set ACTIVE_STREAMS = 10 to get Franzen's original setting back.
ACTIVE_STREAMS = 12

import os
os.environ["ARC3_MAX_ACTIVE_STREAMS"] = str(int(ACTIVE_STREAMS))
print(f"admitted games at once: ARC3_MAX_ACTIVE_STREAMS={os.environ['ARC3_MAX_ACTIVE_STREAMS']} "
      f"(section 5 must also set MAXREQ=12, CUDAGRAPH_MAXBS=12, MAMBA_CACHE=68)")
