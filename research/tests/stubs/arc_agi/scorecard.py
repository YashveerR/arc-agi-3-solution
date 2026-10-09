"""TEST-ONLY stand-in (see arc_agi/__init__.py)."""


class EnvironmentScoreCalculator:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("arc_agi stub: the real toolkit is not available in this test")
