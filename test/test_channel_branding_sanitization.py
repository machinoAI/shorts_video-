import pytest
import re
from pathlib import Path

from pipeline.config import CHANNEL_NAME, CHANNEL_HANDLE
from pipeline.script_generator import (
    sanitize_spec_channel_branding,
    SCRIPT_DIRECTIVES
)
from pipeline.developer_perks_script_engine import DeveloperPerksScriptEngine
from pipeline.bespoke_visual_synthesizer import BESPOKE_SYNTHESIZER_SYSTEM_PROMPT
from pipeline.hindi_localizer import HINDI_LOCALIZATION_PROMPT
from pipeline.subtitle_generator import export_ass
from pipeline.vsg_schema import convert_legacy_spec_to_vsg


def test_sanitize_spec_channel_branding_comprehensive():
    """Validates that legacy channel names are comprehensively rewritten to CHANNEL_NAME."""
    raw_spec = {
        "title": "The Model Verse",
        "category": "mechanism_deepdive",
        "beats": [
            {
                "beat_id": 1,
                "text": "Chopping technical papers into 500-token chunks completely blinds LLMs.",
                "visual_focus": "Grid visualization of chunks.",
                "highlight_words": {"Chopping": "#EF4444"},
                "svo_action": {"subject": "Hard Chunks", "action_verb": "fragments", "direct_object": "Context", "anchor_word": "chunks"},
                "visual_blueprint": {"layout": "grid_memory", "title": "CHUNK FRAGMENTATION", "sub": "Standard RAG limits"}
            },
            {
                "beat_id": 6,
                "text": "Break the hard boundaries of your data. Follow The Model Verse for daily deep-dives into frontier architectures.",
                "visual_focus": "A smooth animation of the GMM clusters pulsing, transforming back into The Model Verse logo.",
                "highlight_words": {
                    "Break the hard boundaries": "#38BDF8",
                    "The Model Verse": "#34D399"
                },
                "svo_action": {
                    "subject": "The Model Verse",
                    "action_verb": "analyzes",
                    "direct_object": "Model Verse architectures",
                    "anchor_word": "Modelverse"
                },
                "visual_blueprint": {
                    "layout": "layer_stack",
                    "title": "THE MODEL VERSE",
                    "sub": "Deep dive into model verse structural intelligence",
                    "params": {
                        "footer": "Follow modelverse"
                    }
                }
            }
        ]
    }

    sanitized = sanitize_spec_channel_branding(raw_spec)
    expected_brand = CHANNEL_NAME or "machinoAI"

    # Title check
    assert sanitized["title"] == expected_brand

    # Beat 6 text check
    b6 = sanitized["beats"][1]
    assert "The Model Verse" not in b6["text"]
    assert expected_brand in b6["text"]
    assert "The Model Verse" not in b6["visual_focus"]
    assert expected_brand in b6["visual_focus"]

    # Highlights check
    assert "The Model Verse" not in b6["highlight_words"]
    assert expected_brand in b6["highlight_words"]

    # SVO action check
    assert b6["svo_action"]["subject"] == expected_brand
    assert "The Model Verse" not in b6["svo_action"]["direct_object"]
    assert expected_brand in b6["svo_action"]["direct_object"]
    assert b6["svo_action"]["anchor_word"] == expected_brand

    # Visual blueprint check
    assert b6["visual_blueprint"]["title"] == expected_brand.upper()
    assert "model verse" not in b6["visual_blueprint"]["sub"].lower()
    assert "modelverse" not in b6["visual_blueprint"]["params"]["footer"].lower()
    assert expected_brand in b6["visual_blueprint"]["params"]["footer"]


def test_prompts_do_not_leak_legacy_branding():
    """Validates that system prompts do not contain hardcoded 'The Model Verse' examples."""
    expected_brand = CHANNEL_NAME or "machinoAI"

    # 1. script_generator.py SCRIPT_DIRECTIVES
    assert "The Model Verse" not in SCRIPT_DIRECTIVES
    assert expected_brand in SCRIPT_DIRECTIVES

    # 2. bespoke_visual_synthesizer.py BESPOKE_SYNTHESIZER_SYSTEM_PROMPT
    assert "The Model Verse" not in BESPOKE_SYNTHESIZER_SYSTEM_PROMPT
    assert expected_brand in BESPOKE_SYNTHESIZER_SYSTEM_PROMPT

    # 3. hindi_localizer.py HINDI_LOCALIZATION_PROMPT
    assert "The Model Verse" not in HINDI_LOCALIZATION_PROMPT
    assert expected_brand in HINDI_LOCALIZATION_PROMPT


def test_vsg_and_subtitles_default_to_active_channel_name(tmp_path):
    """Validates that defaults in schema converters and subtitle exporters use active CHANNEL_NAME."""
    expected_brand = CHANNEL_NAME or "machinoAI"

    # VSG Converter
    vsg = convert_legacy_spec_to_vsg({"id": "sample_spec", "category": "mechanism_deepdive"})
    assert vsg.project_title == expected_brand

    # Subtitle exporter
    ass_path = str(tmp_path / "test.ass")
    export_ass(
        chunks=[{"start": 0.0, "end": 1.0, "text": "Test"}],
        output_path=ass_path
    )
    with open(ass_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert f"Title: {expected_brand} Kinetic Captions" in content
