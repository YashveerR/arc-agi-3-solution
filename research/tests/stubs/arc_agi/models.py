"""TEST-ONLY stand-in (see arc_agi/__init__.py)."""
from dataclasses import dataclass


@dataclass
class EnvironmentInfo:
    game_id: str = ""
