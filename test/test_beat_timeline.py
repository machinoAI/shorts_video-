"""Tests for the word-synced beat timeline planner (manim_engine/choreography/timeline.py)."""

from manim_engine.choreography.timeline import (
    EXIT_TIME,
    cue_tokens,
    find_anchor_time,
    plan_beat_timeline,
)


def _words(text, start=10.0, step=0.4):
    out = []
    for i, w in enumerate(text.split()):
        t = start + i * step
        out.append({"word": w, "clean_word": w.lower().strip(".,?"), "start": t, "end": t + 0.35,
                    "frame_ahead_trigger": t - 0.04})
    return out


SPLIT_CUES = [
    ["TOKEN SEQUENCE"],
    ["ROUTER"],
    ["ATTENTION HEADS"],
    ["FEED-FORWARD EXPERTS"],
]


def test_steps_fire_on_the_words_that_name_them():
    words = _words("Every token hits the router which sends it either to attention heads or to feed-forward experts here")
    events = plan_beat_timeline(10.0, 18.0, SPLIT_CUES, words, anchor_word="experts")
    steps = [e for e in events if e.kind == "step"]
    assert [s.index for s in steps] == [0, 1, 2, 3]
    assert steps[0].time == 10.0
    assert steps[1].cue.startswith("route")       # "router"
    assert steps[2].cue == "attention"
    assert steps[3].cue in ("feedforward", "experts")
    times = [s.time for s in steps]
    assert times == sorted(times)


def test_unmatched_steps_are_spread_over_the_build_window():
    events = plan_beat_timeline(0.0, 8.0, [["A"], ["B"], ["C"]], word_timings=[], anchor_word=None)
    steps = [e for e in events if e.kind == "step"]
    assert [round(s.time, 2) for s in steps] == [0.0, 1.92, 3.84]


def test_focus_lands_on_anchor_word_after_the_build():
    words = _words("Recurrence forces one step at a time so the GPU sits idle while waiting", start=0.0, step=0.5)
    events = plan_beat_timeline(0.0, 8.0, [["X"], ["Y"]], words, anchor_word="idle")
    focus = [e for e in events if e.kind == "focus"]
    assert len(focus) == 1
    assert abs(focus[0].time - find_anchor_time(words, "idle")) < 1e-6
    assert focus[0].time > max(e.time for e in events if e.kind == "step")


def test_events_never_overlap_and_end_with_exit():
    words = _words("a b c d e f g h i j k l m n o p", start=5.0, step=0.3)
    events = plan_beat_timeline(5.0, 11.0, [["a"], ["b"], ["c"], ["d"]], words, anchor_word="m", has_formula=True)
    for cur, nxt in zip(events, events[1:]):
        assert cur.time + cur.run_time <= nxt.time + 1e-6
    assert events[-1].kind == "exit"
    assert abs(events[-1].time - (11.0 - EXIT_TIME)) < 1e-6
    assert all(5.0 <= e.time <= 11.0 for e in events)


def test_formula_rides_with_second_step():
    events = plan_beat_timeline(0.0, 6.0, [["a"], ["b"], ["c"]], [], None, has_formula=True)
    with_formula = [e for e in events if e.with_formula]
    assert len(with_formula) == 1 and with_formula[0].index == 1


def test_short_beat_with_many_steps_is_compressed():
    events = plan_beat_timeline(0.0, 2.5, [["a"], ["b"], ["c"], ["d"]], [], None)
    steps = [e for e in events if e.kind == "step"]
    assert len(steps) == 4
    assert steps[-1].time < 2.5 - EXIT_TIME
    for cur, nxt in zip(events, events[1:]):
        assert cur.time + cur.run_time <= nxt.time + 1e-6


def test_cue_tokens_skip_stopwords_and_short_words():
    assert cue_tokens(["THE INPUT STREAM", "KV CACHE", "Attention Heads"]) == ["cache", "attention", "heads"]
