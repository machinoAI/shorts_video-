"""Tests for the numeric grounding guard (pipeline/grounding.py)."""

import copy

from pipeline.grounding import (
    apply_grounding_guard,
    build_source_text,
    extract_numbers,
    ungrounded_numbers,
)

SCALING_LAWS_META = {
    "title": "Scaling Laws for Neural Language Models",
    "abstract": (
        "We study empirical scaling laws for language model performance on the cross-entropy loss. "
        "The loss scales as a power-law with model size, dataset size, and the amount of compute used "
        "for training, with some trends spanning more than seven orders of magnitude."
    ),
}

FLASH_META = {
    "title": "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
    "abstract": (
        "FlashAttention trains Transformers faster than existing baselines: 15% end-to-end wall-clock "
        "speedup on BERT-large (seq. length 512) compared to the MLPerf 1.1 training speed record, "
        "3x speedup on GPT-2 (seq. length 1K), and 2.4x speedup on long-range arena (seq. length 1K-4K)."
    ),
}


def _leaky_spec():
    """A spec shaped like the real Scaling Laws template that leaked prompt-example values."""
    return {
        "id": "scaling_laws_prediction",
        "beats": [
            {"beat_id": 1, "text": "Why are leading AI teams switching to this after a 98.2% benchmark result?"},
            {"beat_id": 2, "text": "Researchers guess compute allocation without seeing the loss curve."},
            {
                "beat_id": 5,
                "text": "Larger models with less data consistently win.",
                "visual_blueprint": {
                    "layout": "horizontal_race_bars",
                    "params": {
                        "contestants": [
                            {"name": "Optimal Scaling", "value": 98.2, "display_val": "98.2%"},
                            {"name": "Naive Scaling", "value": 41.5, "display_val": "41.5%"},
                        ],
                        "delta_badge": "⚡ +56.7% EFFICIENCY GAIN",
                    },
                },
            },
        ],
        "metadata": {
            "payoff_stat": "98.2%",
            "payoff_label": "SCALING EFFICIENCY",
            "payoff_hero_stat": 98.2,
            "payoff_base_stat": 41.5,
            "payoff_delta_badge": "⚡ +56.7% SYNTACTIC RECOVERY GAIN",
            "scale_metric": "10^7",
            "solution_title": "POWER-LAW EXTRAPOLATION",
            "model_b": None,
            "benchmarks": [{"name": "Loss Reduction", "score_a": "98%", "score_b": "40%"}],
        },
        "benchmark_comparison": {
            "contestants": [
                {"name": "Optimal Scaling", "value": 98.2, "display_val": "98.2%"},
                {"name": "Naive Scaling", "value": 41.5, "display_val": "41.5%"},
            ],
            "delta_badge": "⚡ +56.7% EFFICIENCY GAIN",
        },
        "math_formulas": [
            {"beat_id": 1, "latex": r"$L(N) \approx (N_c / N)^{\alpha_N}$"},
            {"beat_id": 5, "latex": r"$\mathrm{Accuracy} = 98.2\%$"},
        ],
    }


def test_extract_numbers_normalizes_and_ignores_model_names():
    assert extract_numbers("1,180 TFLOPS and 3.0x on GPT-2 with H100 and FP8") == ["1180", "3"]
    assert extract_numbers("98.2% vs 41.5%") == ["98.2", "41.5"]
    assert extract_numbers(98.2) == ["98.2"]
    assert extract_numbers(None) == []


def test_ungrounded_numbers_skips_trivial_and_years():
    source = set(extract_numbers("3x speedup on GPT-2"))
    assert ungrounded_numbers("3x faster, 1.0x baseline, published in 2022", source) == []
    assert ungrounded_numbers("7x faster", source) == ["7"]


def test_scaling_laws_leak_is_scrubbed():
    spec = apply_grounding_guard(_leaky_spec(), build_source_text(SCALING_LAWS_META))
    meta = spec["metadata"]

    for key in ("payoff_stat", "payoff_label", "payoff_hero_stat", "payoff_base_stat",
                "payoff_delta_badge", "scale_metric", "benchmarks"):
        assert key not in meta, key
    assert meta["solution_title"] == "POWER-LAW EXTRAPOLATION"
    assert "model_b" not in meta  # null placeholders removed
    assert "benchmark_comparison" not in spec

    params = spec["beats"][2]["visual_blueprint"]["params"]
    assert "contestants" not in params and "delta_badge" not in params

    assert [f["beat_id"] for f in spec["math_formulas"]] == [1]

    flags = spec["quality_flags"]
    assert flags["ungrounded_narration_numbers"][0]["beat_id"] == 1
    assert flags["ungrounded_narration_numbers"][0]["numbers"] == ["98.2"]
    assert any(h["value"] == "98.2" for h in flags["leaked_example_values"])


def test_grounded_numbers_are_kept():
    spec = {
        "beats": [
            {
                "beat_id": 5,
                "text": "The result? A 3x speedup on GPT-2 and 2.4x on long-range arena.",
                "visual_blueprint": {
                    "layout": "horizontal_race_bars",
                    "params": {
                        "contestants": [
                            {"name": "FlashAttention", "value": 3.0, "display_val": "3.0x"},
                            {"name": "PyTorch Baseline", "value": 1.0, "display_val": "1.0x"},
                        ],
                        "delta_badge": "⚡ 3x FASTER ON GPT-2",
                    },
                },
            }
        ],
        "metadata": {"payoff_stat": "3x", "payoff_label": "GPT-2 SPEEDUP"},
        "benchmark_comparison": {
            "contestants": [
                {"name": "FlashAttention", "value": 3.0, "display_val": "3.0x"},
                {"name": "PyTorch Baseline", "value": 1.0, "display_val": "1.0x"},
            ]
        },
    }
    out = apply_grounding_guard(copy.deepcopy(spec), build_source_text(FLASH_META))

    assert out["metadata"]["payoff_stat"] == "3x"
    assert out["metadata"]["payoff_label"] == "GPT-2 SPEEDUP"
    assert out["benchmark_comparison"] == spec["benchmark_comparison"]
    assert out["beats"][0]["visual_blueprint"]["params"]["delta_badge"] == "⚡ 3x FASTER ON GPT-2"
    assert out["quality_flags"]["ungrounded_narration_numbers"] == []
    assert out["quality_flags"]["scrubbed_fields"] == []


def test_flag_only_mode_does_not_modify_fields():
    spec = apply_grounding_guard(_leaky_spec(), build_source_text(SCALING_LAWS_META), scrub=False)
    assert spec["metadata"]["payoff_stat"] == "98.2%"
    assert "benchmark_comparison" in spec
    assert "metadata.payoff_stat" in spec["quality_flags"]["scrubbed_fields"]


def test_source_text_includes_angle_and_key_facts():
    meta = {"title": "AlphaFold 2", "angle": "CASP14 average score of 92.4 GDT", "key_facts": ["$350k credits"]}
    src = build_source_text(meta)
    assert "92.4" in extract_numbers(src)
    assert "350" in extract_numbers(src)


def test_enforce_script_schema_does_not_invent_metrics():
    from pipeline.llm_router import enforce_script_schema

    spec = enforce_script_schema(
        {"title": "X", "beats": [], "metadata": {"payoff_stat": None}, "benchmark_comparison": None},
        topic="Some Paper",
    )
    assert "payoff_stat" not in spec["metadata"]
    assert "scale_metric" not in spec["metadata"]
    assert "benchmark_comparison" not in spec
    for f in spec["math_formulas"]:
        assert "2.5" not in f["latex"]
