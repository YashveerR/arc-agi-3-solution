"""Unit tests for the stuck review in inference/agent/tool_agent.py.

Run with the harness on PYTHONPATH (see research/tests/README.md):

    python3 research/tests/test_stuck_review_unit.py

Plain asserts, no pytest needed.
"""
from __future__ import annotations

import os
import sys
import traceback

# what the competition notebook sets before the harness is imported
os.environ.setdefault("LOCAL_ANALYZER_MODEL_ID", "flashnext")
os.environ.setdefault("LOCAL_ANALYZER_PROVIDER", "vllm")
os.environ.setdefault("LOCAL_ANALYZER_BASE_URL", "http://127.0.0.1:9/v1")

import inference.agent.tool_agent as ta  # noqa: E402
from inference.agent.runtime_state import Frame  # noqa: E402

KEYS = ("ARC3_STUCK_REVIEW_TOKENS", "ARC3_STUCK_REVIEW_MAX", "ARC3_STUCK_REVIEW_AB")


def _frame(level: int) -> Frame:
    return Frame(grid=((0,) * 4,) * 4, step=0, level=level)


def _set_env(**values: str | None) -> None:
    for key in KEYS:
        os.environ.pop(key, None)
    for key, value in values.items():
        if value is not None:
            os.environ[key] = value


def _agent() -> ta.ToolAgent:
    agent = ta.ToolAgent(model="local")
    agent._history_messages = [
        {"role": "user", "content": "opener"},
        {"role": "assistant", "content": "reply", "tool_calls": []},
        {"role": "tool", "content": "tool output", "tool_call_id": "x"},
    ]
    agent._last_step_summary = {"level": 2, "end_action_num": 40}
    agent._tokens_at_level_start = 1_000
    agent._actions_at_level_start = 25
    agent._session_generated_tokens = 1_000
    return agent


def test_off_by_default_changes_nothing() -> None:
    _set_env()
    agent = _agent()
    agent._session_generated_tokens = 10_000_000
    assert agent._maybe_stuck_review(_frame(2)) is None
    assert agent.stuck_review_events == []
    assert agent.stuck_review_arm == ""


def test_below_threshold_does_nothing() -> None:
    _set_env(ARC3_STUCK_REVIEW_TOKENS="40000")
    agent = _agent()
    agent._session_generated_tokens = 1_000 + 39_999
    assert agent._maybe_stuck_review(_frame(2)) is None
    assert agent.stuck_review_events == []


def test_fires_at_threshold_and_keeps_everything() -> None:
    _set_env(ARC3_STUCK_REVIEW_TOKENS="40000")
    agent = _agent()
    history = [dict(m) for m in agent._history_messages]
    agent._session_generated_tokens = 1_000 + 40_000
    note = agent._maybe_stuck_review(_frame(2))
    assert note is not None and note.startswith("REVIEW CHECKPOINT ON LEVEL 2."), note
    assert "40k generated tokens and 15 actions" in note, note
    assert agent._history_messages == history, "history must be untouched"
    # the scheduler's per-level counters are untouched too
    assert agent._tokens_at_level_start == 1_000
    assert agent._actions_at_level_start == 25
    assert agent.stuck_review_events == [{
        "level": 2, "review": 1, "tokens_on_level": 40_000, "actions_on_level": 15, "fired": True,
    }], agent.stuck_review_events


def test_second_review_needs_twice_the_threshold_and_max_is_respected() -> None:
    _set_env(ARC3_STUCK_REVIEW_TOKENS="40000")  # default max 2
    agent = _agent()
    agent._session_generated_tokens = 1_000 + 40_000
    assert agent._maybe_stuck_review(_frame(2)) is not None
    agent._session_generated_tokens = 1_000 + 79_999
    assert agent._maybe_stuck_review(_frame(2)) is None
    agent._session_generated_tokens = 1_000 + 80_000
    assert agent._maybe_stuck_review(_frame(2)) is not None
    agent._session_generated_tokens = 1_000 + 500_000
    assert agent._maybe_stuck_review(_frame(2)) is None
    assert [e["review"] for e in agent.stuck_review_events] == [1, 2]


def test_one_check_fires_at_most_one_review() -> None:
    _set_env(ARC3_STUCK_REVIEW_TOKENS="40000")
    agent = _agent()
    agent._session_generated_tokens = 1_000 + 200_000  # past both thresholds at once
    assert agent._maybe_stuck_review(_frame(2)) is not None
    assert len(agent.stuck_review_events) == 1
    assert agent._maybe_stuck_review(_frame(2)) is not None  # the next turn gets the second
    assert len(agent.stuck_review_events) == 2


def test_max_setting() -> None:
    _set_env(ARC3_STUCK_REVIEW_TOKENS="40000", ARC3_STUCK_REVIEW_MAX="1")
    agent = _agent()
    agent._session_generated_tokens = 1_000 + 200_000
    assert agent._maybe_stuck_review(_frame(2)) is not None
    assert agent._maybe_stuck_review(_frame(2)) is None


def test_new_level_gets_its_own_reviews() -> None:
    _set_env(ARC3_STUCK_REVIEW_TOKENS="40000", ARC3_STUCK_REVIEW_MAX="1")
    agent = _agent()
    agent._session_generated_tokens = 1_000 + 40_000
    assert agent._maybe_stuck_review(_frame(2)) is not None
    # level 3 begins: the solver-side level transition restarts the counters
    agent._tokens_at_level_start = agent._session_generated_tokens
    agent._actions_at_level_start = 40
    assert agent._maybe_stuck_review(_frame(3)) is None
    agent._session_generated_tokens += 40_000
    assert agent._maybe_stuck_review(_frame(3)) is not None
    assert [e["level"] for e in agent.stuck_review_events] == [2, 3]


def test_not_after_the_game_is_won() -> None:
    _set_env(ARC3_STUCK_REVIEW_TOKENS="40000")
    agent = _agent()
    agent._last_step_summary = {"level": 2, "end_action_num": 40, "run_complete": True}
    agent._session_generated_tokens = 1_000_000
    assert agent._maybe_stuck_review(_frame(2)) is None
    assert agent.stuck_review_events == []


def test_ab_arm_without_reviews_records_but_sends_nothing() -> None:
    _set_env(ARC3_STUCK_REVIEW_TOKENS="40000", ARC3_STUCK_REVIEW_AB="1")
    agent = _agent()
    assert agent.stuck_review_arm == "off", "unassigned agents must not review under A/B"
    game = "ab12-0000"
    off_pass = next(p for p in (0, 1) if not ta._stuck_review_arm_on(game, p))
    agent.configure_stuck_review(game, off_pass)
    assert agent.stuck_review_arm == "off"
    agent._session_generated_tokens = 1_000 + 40_000
    assert agent._maybe_stuck_review(_frame(2)) is None
    assert agent.stuck_review_events == [{
        "level": 2, "review": 1, "tokens_on_level": 40_000, "actions_on_level": 15, "fired": False,
    }]


def test_ab_assignment_alternates_passes_and_varies_by_game() -> None:
    _set_env(ARC3_STUCK_REVIEW_TOKENS="40000", ARC3_STUCK_REVIEW_AB="1")
    games = [f"g{i:03d}-abcd" for i in range(40)]
    for g in games:
        assert ta._stuck_review_arm_on(g, 0) != ta._stuck_review_arm_on(g, 1), g
    on_in_pass0 = sum(ta._stuck_review_arm_on(g, 0) for g in games)
    assert 0 < on_in_pass0 < len(games), on_in_pass0
    agent = _agent()
    on_pass = next(p for p in (0, 1) if ta._stuck_review_arm_on(games[0], p))
    agent.configure_stuck_review(games[0], on_pass)
    assert agent.stuck_review_arm == "on"
    agent._session_generated_tokens = 1_000 + 40_000
    assert agent._maybe_stuck_review(_frame(2)) is not None


def test_without_ab_every_configured_agent_reviews() -> None:
    _set_env(ARC3_STUCK_REVIEW_TOKENS="40000")
    agent = _agent()
    for pass_index in (0, 1, 2):
        agent.configure_stuck_review("any-game", pass_index)
        assert agent.stuck_review_arm == "on"


def main() -> int:
    tests = [(name, fn) for name, fn in globals().items() if name.startswith("test_") and callable(fn)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except Exception:
            failed += 1
            print(f"FAIL {name}")
            traceback.print_exc()
    _set_env()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
