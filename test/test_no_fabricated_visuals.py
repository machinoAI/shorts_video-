"""
Guards against fabricated numbers on screen (benchmark fallbacks, radar scores,
thumbnail default stats). See pipeline/benchmark_extractor.py and pipeline/visual_director.py.
"""

import re

from pipeline.benchmark_extractor import BenchmarkExtractor
from pipeline.visual_director import VisualDirector

NUMERIC_LAYOUTS = VisualDirector.NUMERIC_LAYOUTS


def _spec(**extra):
    spec = {
        "id": "scaling_laws",
        "title": "Scaling Laws for Neural Language Models",
        "paper_figures": [],
        "beats": [
            {"beat_id": 1, "text": "Training a big model is a bet on an invisible power law.", "visual_focus": "Loss curve"},
            {
                "beat_id": 2,
                "text": "Teams guess compute budgets and hope the benchmark is faster.",
                "visual_focus": "Benchmark race",
                # LLM picked race bars but the grounding guard removed its invented contestants
                "visual_blueprint": {"layout": "horizontal_race_bars", "title": "GUESSWORK", "params": {}},
            },
            {"beat_id": 3, "text": "Small runs reveal a smooth loss landscape trend.", "visual_focus": "Landscape"},
            {"beat_id": 4, "text": "Model size and data form a layered stack of trade-offs.", "visual_focus": "Layers"},
            {"beat_id": 5, "text": "Bigger models outperform the baseline at equal compute speed.", "visual_focus": "Benchmark speed comparison"},
            {"beat_id": 6, "text": "Follow for more."},
        ],
    }
    spec.update(extra)
    return spec


def test_no_numeric_layout_without_verified_numbers():
    res = VisualDirector().prepare_storyboard_for_spec(_spec())
    for b in res["beats"]:
        bp = b.get("visual_blueprint") or {}
        assert bp.get("layout") not in NUMERIC_LAYOUTS, (b["beat_id"], bp.get("layout"))
        params = b.get("motif_params") or {}
        for c in params.get("contestants", []) or []:
            assert "1,180" not in str(c.get("display_val", ""))


def test_beat5_race_bars_use_only_verified_contestants():
    spec = _spec(benchmark_comparison={
        "title": "BENCHMARK SHOWDOWN: SPEEDUP", "metric_name": "Speedup", "unit": "x",
        "contestants": [
            {"name": "FlashAttention", "value": 3.0, "display_val": "3.0x", "is_hero": True},
            {"name": "PyTorch", "value": 1.0, "display_val": "1.0x"},
        ],
    })
    res = VisualDirector().prepare_storyboard_for_spec(spec)
    beat5 = next(b for b in res["beats"] if b["beat_id"] == 5)
    assert beat5["visual_blueprint"]["layout"] == "horizontal_race_bars"
    names = [c["name"] for c in beat5["visual_blueprint"]["params"]["contestants"]]
    assert names == ["FlashAttention", "PyTorch"]


def test_synthesized_blueprints_never_include_radar_or_fake_bars():
    director = VisualDirector()
    beat = {
        "text": "A pareto frontier tradeoff with faster throughput on the benchmark leaderboard.",
        "visual_focus": "radar of dimensions",
        "svo_action": {"subject": "Kernel", "action_verb": "races", "direct_object": "Throughput"},
    }
    used = set()
    for _ in range(12):
        bp = director.synthesize_visual_blueprint(beat, topic="Attention", beat_id=2, used_layouts=used)
        assert bp["layout"] not in NUMERIC_LAYOUTS
        used.add(bp["layout"])


def test_radar_data_is_never_synthesized():
    axes, models = BenchmarkExtractor().build_pareto_radar_data([], ["A", "B", "C"])
    assert axes == ["A", "B", "C"] and models == []


REAL_CODE = {
    "filename": "paged_attention.cu",
    "language": "cuda",
    "lines": ["__global__ void paged_attention(", "    const int* block_tables) {", "  int b = block_tables[seq_id];", "}"],
    "provenance": "curated",
}


def test_llm_code_for_papers_is_never_shown():
    spec = _spec(code_snippet={"filename": "core_kernel.py", "lines": ["def execute_step(tensor_in):", "    return 1"]})
    spec["beats"][3]["visual_blueprint"] = {"layout": "chalkboard_code_block", "title": "KERNEL", "params": {}}
    res = VisualDirector().prepare_storyboard_for_spec(spec)
    for b in res["beats"]:
        assert (b.get("visual_blueprint") or {}).get("layout") not in VisualDirector.CODE_LAYOUTS, b["beat_id"]


def test_repo_code_is_shown_for_github_topics():
    spec = _spec(code_snippet=REAL_CODE, repo_metadata={"repo_name": "vllm-project/vllm", "stars": 42000})
    res = VisualDirector().prepare_storyboard_for_spec(spec)
    code_beats = [b for b in res["beats"] if (b.get("visual_blueprint") or {}).get("layout") == "chalkboard_code_block"]
    assert len(code_beats) == 1
    assert code_beats[0]["visual_blueprint"]["params"]["lines"] == REAL_CODE["lines"]


def test_has_verified_code_rules():
    from pipeline.grounding import has_verified_code

    assert has_verified_code({"repo_metadata": {"repo_name": "a/b"}, "code_snippet": REAL_CODE})
    assert not has_verified_code({"code_snippet": REAL_CODE})  # no repository
    assert not has_verified_code({"repo_metadata": {"repo_name": "a/b"},
                                  "code_snippet": dict(REAL_CODE, provenance="placeholder")})
    assert not has_verified_code({"repo_metadata": {"repo_name": "a/b"},
                                  "code_snippet": {"lines": ["def execute_step(tensor_in):", "  out = fused_forward_pass(tensor_in)"]}})


def test_placeholder_kernel_is_not_attached_to_github_candidates():
    from pipeline.github_trending_fetcher import GitHubTrendingFetcher, TrendingRepo

    kernel = GitHubTrendingFetcher().extract_kernel_from_readme("unknown/repo", "No code here.")
    assert kernel.provenance == "placeholder"
    repo = TrendingRepo(repo_name="unknown/repo", title="t", description="d", stars=2000, language="Python",
                        url="https://github.com/unknown/repo", topics=[], code_kernel=kernel)
    assert "code_snippet" not in repo.to_spec_candidate()


def test_thumbnail_profiles_have_no_hardcoded_stats():
    from pipeline.thumbnail_generator import CATEGORY_PROFILES

    for name, profile in CATEGORY_PROFILES.items():
        assert not re.search(r"\d", profile["default_badge"]), (name, profile["default_badge"])
        assert profile.get("default_svg") is None, name
        assert "stat_val_1" not in profile and "stat_val_2" not in profile, name
