"""Unit tests for the fresh-start mechanism in inference/agent/tool_agent.py.

Run with the harness on PYTHONPATH (see research/tests/README.md):

    python3 research/tests/test_fresh_start_unit.py

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


def _frame(level: int) -> Frame:
    return Frame(grid=((0,) * 4,) * 4, step=0, level=level)


def _opener(level: int, text: str) -> dict:
    return {"role": "user", "content": text, ta._LEVEL_MARK_KEY: level}


def _turn(level: int, tag: str) -> list[dict]:
    return [
        _opener(level, f"opener {tag}"),
        {"role": "assistant", "content": f"reply {tag}", "tool_calls": []},
        {"role": "tool", "content": f"tool {tag}", "tool_call_id": "x"},
    ]


def _agent() -> ta.ToolAgent:
    agent = ta.ToolAgent(model="local")
    agent._history_messages = [*_turn(1, "a"), *_turn(1, "b"), *_turn(2, "c"), *_turn(2, "d")]
    agent._last_step_summary = {"level": 2, "end_action_num": 40}
    agent._tokens_at_level_start = 1_000
    agent._actions_at_level_start = 25
    agent._session_generated_tokens = 1_000
    return agent


def _set_env(**values: str | None) -> None:
    for key, value in values.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def test_private_keys_never_sent() -> None:
    original = {"role": "user", "content": "x", ta._LEVEL_MARK_KEY: 3, ta._CONTROL_MESSAGE_KEY: "resume"}
    cleaned = ta._strip_control_keys([original, {"role": "assistant", "content": "y"}])
    assert all(not k.startswith("_arc3") for m in cleaned for k in m), cleaned
    assert ta._LEVEL_MARK_KEY in original, "the stored message must keep its tag"


def test_off_by_default_changes_nothing() -> None:
    _set_env(ARC3_FRESH_START_TOKENS=None, ARC3_FRESH_START_MAX=None)
    agent = _agent()
    before = list(agent._history_messages)
    agent._session_generated_tokens = 10_000_000
    assert agent._maybe_fresh_start(_frame(2)) is None
    assert agent._history_messages == before
    assert agent.fresh_start_events == []
    assert agent._tokens_at_level_start == 1_000


def test_below_threshold_does_nothing() -> None:
    _set_env(ARC3_FRESH_START_TOKENS="60000", ARC3_FRESH_START_MAX=None)
    agent = _agent()
    before = list(agent._history_messages)
    agent._session_generated_tokens = 1_000 + 59_999
    assert agent._maybe_fresh_start(_frame(2)) is None
    assert agent._history_messages == before


def test_fires_and_cuts_at_level_start() -> None:
    _set_env(ARC3_FRESH_START_TOKENS="60000", ARC3_FRESH_START_MAX=None)
    agent = _agent()
    agent._session_generated_tokens = 1_000 + 60_000
    agent._context_was_trimmed = False
    note = agent._maybe_fresh_start(_frame(2))
    assert note is not None and note.startswith("FRESH START ON LEVEL 2."), note
    assert "60k generated tokens and 15 actions" in note, note
    texts = [m["content"] for m in agent._history_messages]
    assert texts == ["opener a", "reply a", "tool a", "opener b", "reply b", "tool b"], texts
    event = agent.fresh_start_events[-1]
    assert event == {
        "level": 2, "attempt": 1, "tokens_on_level": 60_000,
        "actions_on_level": 15, "dropped_messages": 6,
    }, event
    # counters restart, and the scheduler is told the prefix changed
    assert agent._tokens_at_level_start == 61_000
    assert agent._actions_at_level_start == 40
    assert agent._context_was_trimmed is True


def test_one_fresh_start_per_level_by_default() -> None:
    _set_env(ARC3_FRESH_START_TOKENS="60000", ARC3_FRESH_START_MAX=None)
    agent = _agent()
    agent._session_generated_tokens = 61_000
    assert agent._maybe_fresh_start(_frame(2)) is not None
    agent._session_generated_tokens += 200_000
    assert agent._maybe_fresh_start(_frame(2)) is None
    assert len(agent.fresh_start_events) == 1


def test_max_allows_more_and_needs_a_full_threshold_each_time() -> None:
    _set_env(ARC3_FRESH_START_TOKENS="60000", ARC3_FRESH_START_MAX="2")
    agent = _agent()
    agent._session_generated_tokens = 61_000
    assert agent._maybe_fresh_start(_frame(2)) is not None
    agent._history_messages.extend(_turn(2, "e"))
    agent._session_generated_tokens += 59_999
    assert agent._maybe_fresh_start(_frame(2)) is None
    agent._session_generated_tokens += 1
    assert agent._maybe_fresh_start(_frame(2)) is not None
    assert [e["attempt"] for e in agent.fresh_start_events] == [1, 2]
    agent._session_generated_tokens += 60_000
    assert agent._maybe_fresh_start(_frame(2)) is None


def test_new_level_gets_its_own_budget() -> None:
    _set_env(ARC3_FRESH_START_TOKENS="60000", ARC3_FRESH_START_MAX=None)
    agent = _agent()
    agent._session_generated_tokens = 61_000
    assert agent._maybe_fresh_start(_frame(2)) is not None
    # level 3 begins: the solver-side level transition resets the counters
    agent._history_messages.extend(_turn(3, "f"))
    agent._tokens_at_level_start = agent._session_generated_tokens
    agent._session_generated_tokens += 60_000
    assert agent._maybe_fresh_start(_frame(3)) is not None
    assert [e["level"] for e in agent.fresh_start_events] == [2, 3]
    texts = [m["content"] for m in agent._history_messages]
    assert texts == ["opener a", "reply a", "tool a", "opener b", "reply b", "tool b"], texts


def test_front_trimmed_history_is_all_current_level() -> None:
    _set_env(ARC3_FRESH_START_TOKENS="60000", ARC3_FRESH_START_MAX=None)
    agent = _agent()
    agent._history_messages = [*_turn(2, "c"), *_turn(2, "d")]
    agent._session_generated_tokens = 61_000
    assert agent._maybe_fresh_start(_frame(2)) is not None
    assert agent._history_messages == []


def test_never_leaves_a_dangling_opener() -> None:
    _set_env(ARC3_FRESH_START_TOKENS="60000", ARC3_FRESH_START_MAX=None)
    agent = _agent()
    agent._history_messages = [*_turn(1, "a"), _opener(1, "dangling"), *_turn(2, "c")]
    agent._session_generated_tokens = 61_000
    assert agent._maybe_fresh_start(_frame(2)) is not None
    assert agent._history_messages[-1]["role"] != "user"
    assert [m["content"] for m in agent._history_messages] == ["opener a", "reply a", "tool a"]


def test_not_after_the_game_is_won() -> None:
    _set_env(ARC3_FRESH_START_TOKENS="60000", ARC3_FRESH_START_MAX=None)
    agent = _agent()
    agent._last_step_summary = {"level": 2, "end_action_num": 40, "run_complete": True}
    agent._session_generated_tokens = 1_000_000
    assert agent._maybe_fresh_start(_frame(2)) is None


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
    _set_env(ARC3_FRESH_START_TOKENS=None, ARC3_FRESH_START_MAX=None)
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
