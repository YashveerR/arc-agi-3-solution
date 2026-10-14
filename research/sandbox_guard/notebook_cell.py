# === Sandbox out-of-memory guard ==============================================
# From the research branch of https://github.com/YashveerR/arc-agi-3-solution
# (research/sandbox_guard/). Each Python snippet the model runs is volunteered
# as the first process Linux kills if the machine runs out of RAM, so a runaway
# snippet dies (its game gets an ordinary tool error and carries on) instead of
# the model server. Nothing changes unless RAM actually runs out.
#
# Paste as a NEW cell directly AFTER section "1. Environment and submission mode"
# (the cell that applies Franzen's harness patch) and BEFORE "2. Precaching".
# It can sit before or after the 12-games cell; the order doesn't matter.
import base64, hashlib, os, subprocess, sys
from pathlib import Path

_PATCH_SHA256 = "dcea09224ec9284b7ed76ea1fc1a1d040b1a935845b16285d536d1ac5d30c34f"
_PATCH_B64 = (
    "ZGlmZiAtLWdpdCBhL0FSQzMtSW5mZXJlbmNlL2luZmVyZW5jZS9hZ2VudC9weXRob25fdG9vbF9z"
    "YW5kYm94LnB5IGIvQVJDMy1JbmZlcmVuY2UvaW5mZXJlbmNlL2FnZW50L3B5dGhvbl90b29sX3Nh"
    "bmRib3gucHkKaW5kZXggNThhOTRiMy4uNmExOGZlNiAxMDA2NDQKLS0tIGEvQVJDMy1JbmZlcmVu"
    "Y2UvaW5mZXJlbmNlL2FnZW50L3B5dGhvbl90b29sX3NhbmRib3gucHkKKysrIGIvQVJDMy1JbmZl"
    "cmVuY2UvaW5mZXJlbmNlL2FnZW50L3B5dGhvbl90b29sX3NhbmRib3gucHkKQEAgLTI4Myw2ICsy"
    "ODMsMTUgQEAgX1NBTkRCT1hfQk9PVFNUUkFQID0gdGV4dHdyYXAuZGVkZW50KAogCiAKICAgICBk"
    "ZWYgX3NldF9saW1pdHModGltZW91dF9zZWNvbmRzKToKKyAgICAgICAgaWYgb3MuZW52aXJvbi5n"
    "ZXQoIkFSQzNfU0FOREJPWF9PT01fRklSU1QiKSA9PSAiMSI6CisgICAgICAgICAgICAjIFZvbHVu"
    "dGVlciB0aGlzIHNhbmRib3ggYXMgdGhlIGZpcnN0IHByb2Nlc3MgdGhlIGtlcm5lbCdzCisgICAg"
    "ICAgICAgICAjIG91dC1vZi1tZW1vcnkga2lsbGVyIHRha2VzLCBzbyBhIHJ1bmF3YXkgc25pcHBl"
    "dCBkaWVzIGluc3RlYWQgb2YKKyAgICAgICAgICAgICMgdGhlIG1vZGVsIHNlcnZlci4gUmFpc2lu"
    "ZyBvbmUncyBvd24gc2NvcmUgbmVlZHMgbm8gcHJpdmlsZWdlcy4KKyAgICAgICAgICAgIHRyeToK"
    "KyAgICAgICAgICAgICAgICB3aXRoIG9wZW4oIi9wcm9jL3NlbGYvb29tX3Njb3JlX2FkaiIsICJ3"
    "IikgYXMgaGFuZGxlOgorICAgICAgICAgICAgICAgICAgICBoYW5kbGUud3JpdGUoIjEwMDAiKQor"
    "ICAgICAgICAgICAgZXhjZXB0IE9TRXJyb3I6CisgICAgICAgICAgICAgICAgcGFzcwogICAgICAg"
    "ICBpZiByZXNvdXJjZSBpcyBOb25lOgogICAgICAgICAgICAgcmV0dXJuCiAgICAgICAgIGNwdV9s"
    "aW1pdCA9IG1heCgxLCBpbnQodGltZW91dF9zZWNvbmRzKSkgKyAxCkBAIC03NjIsNiArNzcxLDM5"
    "IEBAIGRlZiBfc2FuaXRpemVfaG9zdF9lcnJvcl90ZXh0KHRleHQ6IHN0cikgLT4gc3RyOgogICAg"
    "IHJldHVybiAiU2FuZGJveCBwcm9jZXNzIGV4aXRlZCB1bmV4cGVjdGVkbHkuIgogCiAKK2RlZiBf"
    "c2FuZGJveF9vb21fZmlyc3QoKSAtPiBib29sOgorICAgICIiIkFSQzNfU0FOREJPWF9PT01fRklS"
    "U1Q6IGVhY2ggc2FuZGJveCB2b2x1bnRlZXJzIGFzIHRoZSBvdXQtb2YtbWVtb3J5CisgICAga2ls"
    "bGVyJ3MgZmlyc3QgdmljdGltIChzZWUgX3NldF9saW1pdHMgaW4gdGhlIGJvb3RzdHJhcCkuIE9m"
    "ZiBieSBkZWZhdWx0LiIiIgorICAgIHJldHVybiBvcy5lbnZpcm9uLmdldCgiQVJDM19TQU5EQk9Y"
    "X09PTV9GSVJTVCIsICIiKS5zdHJpcCgpLmxvd2VyKCkgaW4geyIxIiwgInRydWUiLCAieWVzIiwg"
    "Im9uIn0KKworCitfU0FOREJPWF9LSUxMUyA9IDAKKworCitkZWYgX3JlcG9ydF9zYW5kYm94X2tp"
    "bGxlZCgpIC0+IE5vbmU6CisgICAgIiIiT25lIGxpbmUgb24gc3RkZXJyIGVhY2ggdGltZSBhIHNh"
    "bmRib3ggZGllcyBvZiBTSUdLSUxMIHdpdGggdGhlIGd1YXJkIG9uLgorICAgIE9ubHkgdGhlIG91"
    "dC1vZi1tZW1vcnkga2lsbGVyIHNlbmRzIHRoYXQgaGVyZSAoYSB0aW1lb3V0IHRha2VzIHRoZSBv"
    "dGhlcgorICAgIGJyYW5jaCksIHNvIHRoZXNlIGxpbmVzIGNvbmZpcm0gb3IgcnVsZSBvdXQgcnVu"
    "YXdheSBzbmlwcGV0cyBhcyB0aGUgY2F1c2UKKyAgICBvZiBhIGxvc3Qgc2VydmVyLiBUaGUgbW9k"
    "ZWwgaXMgdG9sZCBub3RoaW5nIG5ldy4iIiIKKyAgICBnbG9iYWwgX1NBTkRCT1hfS0lMTFMKKyAg"
    "ICBfU0FOREJPWF9LSUxMUyArPSAxCisgICAgYXZhaWxhYmxlID0gIj8iCisgICAgdHJ5OgorICAg"
    "ICAgICBmb3IgbGluZSBpbiBvcGVuKCIvcHJvYy9tZW1pbmZvIik6CisgICAgICAgICAgICBpZiBs"
    "aW5lLnN0YXJ0c3dpdGgoIk1lbUF2YWlsYWJsZToiKToKKyAgICAgICAgICAgICAgICBhdmFpbGFi"
    "bGUgPSBmIntpbnQobGluZS5zcGxpdCgpWzFdKSAvIDEwMjQgKiogMjouMWZ9IEdpQiIKKyAgICAg"
    "ICAgICAgICAgICBicmVhaworICAgIGV4Y2VwdCAoT1NFcnJvciwgVmFsdWVFcnJvciwgSW5kZXhF"
    "cnJvcik6CisgICAgICAgIHBhc3MKKyAgICBwcmludCgKKyAgICAgICAgZiJbc2FuZGJveCBndWFy"
    "ZF0gYSBQeXRob24gc25pcHBldCB3YXMga2lsbGVkIGJ5IFNJR0tJTEwsIG1vc3QgbGlrZWx5IGJ5"
    "IHRoZSAiCisgICAgICAgIGYib3V0LW9mLW1lbW9yeSBraWxsZXIgKGtpbGwgI3tfU0FOREJPWF9L"
    "SUxMU30sIFJBTSBhdmFpbGFibGUgbm93IHthdmFpbGFibGV9KTsgIgorICAgICAgICBmIml0cyBn"
    "YW1lIGNvbnRpbnVlcyIsCisgICAgICAgIGZpbGU9c3lzLnN0ZGVyciwKKyAgICAgICAgZmx1c2g9"
    "VHJ1ZSwKKyAgICApCisKKwogZGVmIF9zYW5kYm94X2VudigpIC0+IGRpY3Rbc3RyLCBzdHJdOgog"
    "ICAgIHJldHVybiB7CiAgICAgICAgICJQWVRIT05VTkJVRkZFUkVEIjogIjEiLApAQCAtNzcwLDYg"
    "KzgxMiw3IEBAIGRlZiBfc2FuZGJveF9lbnYoKSAtPiBkaWN0W3N0ciwgc3RyXToKICAgICAgICAg"
    "IkhPTUUiOiAiL3RtcCIsCiAgICAgICAgICJUTVBESVIiOiAiL3RtcCIsCiAgICAgICAgICJQQVRI"
    "Ijogb3MuZW52aXJvbi5nZXQoIlBBVEgiLCAiIiksCisgICAgICAgICoqKHsiQVJDM19TQU5EQk9Y"
    "X09PTV9GSVJTVCI6ICIxIn0gaWYgX3NhbmRib3hfb29tX2ZpcnN0KCkgZWxzZSB7fSksCiAgICAg"
    "fQogCiAKQEAgLTg4Miw2ICs5MjUsOCBAQCBkZWYgcnVuX3NhbmRib3hlZF9weXRob24oCiAgICAg"
    "ICAgICAgICBpZiBsaW5lIGlzIE5vbmU6CiAgICAgICAgICAgICAgICAgc3RkZXJyID0gcHJvY2Vz"
    "cy5zdGRlcnIucmVhZCgpCiAgICAgICAgICAgICAgICAgX3dhaXRfZm9yX3Byb2Nlc3NfZXhpdChw"
    "cm9jZXNzKQorICAgICAgICAgICAgICAgIGlmIHByb2Nlc3MucmV0dXJuY29kZSA9PSAtc2lnbmFs"
    "LlNJR0tJTEwgYW5kIF9zYW5kYm94X29vbV9maXJzdCgpOgorICAgICAgICAgICAgICAgICAgICBf"
    "cmVwb3J0X3NhbmRib3hfa2lsbGVkKCkKICAgICAgICAgICAgICAgICByZXR1cm4gewogICAgICAg"
    "ICAgICAgICAgICAgICAiZXJyb3IiOiBfc2FuaXRpemVfaG9zdF9lcnJvcl90ZXh0KHN0ZGVyciks"
    "CiAgICAgICAgICAgICAgICAgICAgICJzdGRvdXQiOiAiIiwK"
)
_patch = base64.b64decode("".join(_PATCH_B64.split()))
assert hashlib.sha256(_patch).hexdigest() == _PATCH_SHA256, (
    "sandbox-guard patch was damaged while copying: re-copy this whole cell"
)
_src = f"{BUNDLE_DIR}/src"
_patch_path = Path("/kaggle/sandbox-guard.patch")
_patch_path.write_bytes(_patch)
_git = ["git", "apply", "--include=ARC3-Inference/*"]
if subprocess.run(_git + ["-R", "--check", str(_patch_path)], cwd=_src, capture_output=True).returncode == 0:
    print("sandbox guard: patch already applied")
else:
    subprocess.run(_git + ["-v", str(_patch_path)], cwd=_src, check=True)
_sandbox_py = Path(_src) / "ARC3-Inference/inference/agent/python_tool_sandbox.py"
assert "ARC3_SANDBOX_OOM_FIRST" in _sandbox_py.read_text(), "sandbox guard: patch did not land"
os.environ["ARC3_SANDBOX_OOM_FIRST"] = "1"

# Check this machine lets a process volunteer itself (it should: raising your
# own score needs no special rights).
_probe = subprocess.run(
    [sys.executable, "-I", "-S", "-c",
     "open('/proc/self/oom_score_adj','w').write('1000');"
     "print(open('/proc/self/oom_score_adj').read().strip())"],
    capture_output=True, text=True,
)
if _probe.stdout.strip() == "1000":
    print("sandbox guard: ON (ARC3_SANDBOX_OOM_FIRST=1), kernel accepted oom_score_adj=1000")
else:
    print("sandbox guard: WARNING, this machine refused the setting, so the guard does nothing here:",
          (_probe.stderr or _probe.stdout).strip()[-300:])
