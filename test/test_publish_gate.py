"""Tests for the publish gate (pipeline/publish_gate.py)."""

import os
from unittest.mock import patch

from pipeline.publish_gate import (
    apply_gate_to_publishing,
    evaluate_publish_gate,
    load_gate_report,
    save_gate_report,
)

GOOD_VLM = {"vision_verified": True, "passed_quality_gate": True, "average_score": 9.1, "diversity_violations": []}


def _clean_spec(**extra):
    spec = {"script_provider": "gemini", "quality_flags": {"leaked_example_values": [], "ungrounded_narration_numbers": []},
            "hook_gating": {"kept_bespoke": True}}
    spec.update(extra)
    return spec


def test_clean_video_publishes():
    gate = evaluate_publish_gate(_clean_spec(), vlm_report=GOOD_VLM)
    assert gate["decision"] == "publish"
    assert gate["reasons"] == []


def test_fallback_script_is_held():
    gate = evaluate_publish_gate(_clean_spec(script_provider="deterministic_fallback"), vlm_report=GOOD_VLM)
    assert gate["decision"] == "hold"
    assert "fallback" in gate["reasons"][0]


def test_ungrounded_narration_and_leaks_are_held():
    spec = _clean_spec(quality_flags={
        "leaked_example_values": [{"where": "beats[1].text", "value": "98.2"}],
        "ungrounded_narration_numbers": [{"beat_id": 1, "numbers": ["98.2"]}],
    })
    gate = evaluate_publish_gate(spec, vlm_report=GOOD_VLM)
    assert gate["decision"] == "hold"
    assert any("98.2" in r for r in gate["reasons"])


def test_hook_needing_review_is_held():
    spec = _clean_spec(hook_gating={"needs_review": True, "rejection_reasons": ["ungrounded_numbers:98.2"]})
    assert evaluate_publish_gate(spec, vlm_report=GOOD_VLM)["decision"] == "hold"


def test_failed_vision_audit_is_held_but_unverified_only_warns_by_default():
    failed = dict(GOOD_VLM, passed_quality_gate=False, average_score=6.2)
    assert evaluate_publish_gate(_clean_spec(), vlm_report=failed)["decision"] == "hold"

    unverified = dict(GOOD_VLM, vision_verified=False)
    gate = evaluate_publish_gate(_clean_spec(), vlm_report=unverified)
    assert gate["decision"] == "publish"
    assert any("No vision model" in w for w in gate["warnings"])

    with patch.dict(os.environ, {"PUBLISH_GATE_REQUIRE_VLM": "true"}):
        assert evaluate_publish_gate(_clean_spec(), vlm_report=unverified)["decision"] == "hold"


def test_hold_actions_by_mode():
    hold = {"decision": "hold", "reasons": ["x"]}
    with patch.dict(os.environ, {"PUBLISH_GATE_MODE": "private"}):
        assert apply_gate_to_publishing(hold, "public") == {"youtube_upload": True, "privacy": "private", "cross_post": False, "mode": "private"}
    with patch.dict(os.environ, {"PUBLISH_GATE_MODE": "skip"}):
        assert apply_gate_to_publishing(hold, "public")["youtube_upload"] is False
    with patch.dict(os.environ, {"PUBLISH_GATE_MODE": "off"}):
        assert apply_gate_to_publishing(hold, "public") == {"youtube_upload": True, "privacy": "public", "cross_post": True, "mode": "off"}
    with patch.dict(os.environ, {"PUBLISH_GATE_MODE": "private"}):
        assert apply_gate_to_publishing({"decision": "publish"}, "public")["privacy"] == "public"


def test_gate_report_round_trip(tmp_path):
    video = tmp_path / "final_x.mp4"
    video.write_bytes(b"")
    save_gate_report({"decision": "hold", "reasons": ["r"]}, str(video))
    assert load_gate_report(str(video))["decision"] == "hold"


def test_vlm_heuristic_fallback_is_marked_unverified(tmp_path):
    from PIL import Image
    from pipeline.quota_tracker import quota_tracker
    from pipeline.vlm_critic import VLMCritic

    frames = tmp_path / "frames"
    frames.mkdir()
    Image.new("RGB", (90, 160), (10, 13, 20)).save(frames / "beat_01.png")
    quota_tracker.record_exhausted("gemini_vision", "test")
    quota_tracker.record_exhausted("ollama_vision", "test")

    report = VLMCritic(api_key=None).audit_batch_keyframes(str(frames), {"beats": [{"beat_id": 1, "text": "x"}]})
    assert report["vision_verified"] is False
    assert report["unverified_beats"] == [1]
    # ...so the publish gate warns instead of trusting the placeholder 8.8/10
    gate = evaluate_publish_gate(_clean_spec(), vlm_report=report)
    assert any("No vision model" in w for w in gate["warnings"])
