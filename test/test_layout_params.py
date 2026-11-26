"""Tests for diagram label normalization (pipeline/layout_params.py)."""

from pipeline.layout_params import LAYOUT_SLOTS, normalize_layout_params

BEAT = {
    "text": "Recurrence forces tokens through one hidden state at a time.",
    "svo_action": {"subject": "Recurrent hidden state", "action_verb": "serializes",
                   "direct_object": "token sequence", "anchor_word": "time"},
    "highlight_words": {"Recurrence": "#EF4444", "hidden state": "#38BDF8", "one at a time": "#F59E0B"},
}

DEMO_LABELS = {"UNIFIED INPUT STREAM", "DISPATCH ROUTER", "SEMANTIC STREAM", "GEOMETRIC STREAM",
               "High-Level Context", "Spatial Depth Map"}


def test_misnamed_params_are_mapped_and_gaps_filled_from_the_beat():
    params = {"title": "SEQUENTIAL BOTTLENECK", "left_label": "RNN STEP t", "right_label": "RNN STEP t+1",
              "flow_status": "BLOCKED"}
    out, filled = normalize_layout_params("split_flow", params, BEAT, topic="Attention Is All You Need")
    for slot, _ in LAYOUT_SLOTS["split_flow"]:
        assert slot in out
    assert out["branch_a_label"] == "RNN STEP t"       # left_label -> branch A
    assert out["branch_b_label"] == "RNN STEP t+1"     # right_label -> branch B
    assert out["title"] == "SEQUENTIAL BOTTLENECK"     # title is never used as a label
    assert "SEQUENTIAL BOTTLENECK" not in (out["input_label"], out["router_label"])
    assert not (set(map(str, out.values())) & DEMO_LABELS)


def test_placeholders_are_not_kept():
    params = {"stage_1_label": "...", "stage_2_label": "<label>", "stage_3_label": "param_key_1"}
    out, filled = normalize_layout_params("pipeline_stages", params, BEAT)
    assert out["stage_1_label"] == "Recurrent hidden state"
    assert out["stage_2_label"] == "serializes"
    assert out["stage_3_label"] == "token sequence"
    assert {"stage_1_label", "stage_2_label", "stage_3_label"} <= set(filled)


def test_valid_params_are_kept_untouched():
    params = {"root_label": "QUERY", "optimal_label": "BEST PROOF", "pruned_label": "BAD BRANCH"}
    out, filled = normalize_layout_params("tree_hierarchy", params, BEAT)
    assert out["root_label"] == "QUERY" and out["optimal_label"] == "BEST PROOF"
    assert filled == []


def test_aliases_and_unknown_layouts():
    out, _ = normalize_layout_params("dual_stream", {}, BEAT)
    assert "branch_a_label" in out
    params = {"x": 1}
    assert normalize_layout_params("horizontal_race_bars", params, BEAT) == (params, [])


def test_empty_beat_falls_back_to_neutral_text_not_demo_labels():
    out, _ = normalize_layout_params("split_flow", {}, {"text": ""})
    assert not (set(map(str, out.values())) & DEMO_LABELS)
    assert out["input_label"] == "INPUT"
