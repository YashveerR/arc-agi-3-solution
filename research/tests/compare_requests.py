"""Compare two requests.jsonl recordings from the end-to-end tests.

    python3 research/tests/compare_requests.py A/requests.jsonl B/requests.jsonl

Clock values the harness prints (elapsed and remaining seconds) are masked
first, since they differ between any two runs. Exits 0 if every request is
identical, 1 otherwise, and prints the first difference.
"""
from __future__ import annotations

import difflib
import re
import sys

_CLOCK = re.compile(r'((?:elapsed|remaining)[a-z_]*\W{1,4})\d+(?:\.\d+)?')


def _normalise(line: str) -> str:
    return _CLOCK.sub(r"\1#", line)


def main(argv: list[str]) -> int:
    a = [_normalise(line) for line in open(argv[1])]
    b = [_normalise(line) for line in open(argv[2])]
    if len(a) != len(b):
        print(f"different number of requests: {len(a)} vs {len(b)}")
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            ops = difflib.SequenceMatcher(None, x, y, autojunk=False).get_opcodes()
            op, i1, i2, j1, j2 = next(o for o in ops if o[0] != "equal")
            print(f"request {i} differs ({op}): ...{x[max(0, i1 - 80):i2 + 40]!r}\n  vs ...{y[max(0, j1 - 80):j2 + 40]!r}")
            return 1
    if len(a) != len(b):
        return 1
    print(f"all {len(a)} requests identical (clock values masked)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
