"""TEST-ONLY stand-in for the arc_agi toolkit (not installable in this sandbox).

The TAAF framework imports arc_agi at package load, but the offline test only
plays taaf.game_examples.ExampleGame, which never calls into arc_agi. These
names exist so the import succeeds; using any of them raises loudly.
"""
import enum

from . import models, scorecard  # noqa: F401


class OperationMode(enum.Enum):
    NORMAL = "normal"
    ONLINE = "online"
    OFFLINE = "offline"
    COMPETITION = "competition"


class _Unavailable:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("arc_agi stub: the real toolkit is not available in this test")


class Arcade(_Unavailable):
    @staticmethod
    def make(*args, **kwargs):
        raise RuntimeError("arc_agi stub: the real toolkit is not available in this test")


class EnvironmentWrapper(_Unavailable):
    pass


class EnvironmentScorecard(_Unavailable):
    pass
