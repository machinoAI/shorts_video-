"""
Real-Manim checks for the word-synced choreography (skipped when Manim is not installed).

For every diagram type: build it with normalized labels, fit it to the 9:16 safe area,
derive build steps and construct every reveal / focus animation. Nothing is rendered,
so this runs in seconds, but it catches API misuse that only real Manim would reject.
"""

import pytest

manim = pytest.importorskip("manim")

from manim_engine.choreography.builders import (  # noqa: E402
    SAFE_BOTTOM_WITH_FORMULA, SAFE_TOP, SAFE_WIDTH, fit_to_safe_area, focus_animation,
    get_build_steps, reveal_step,
)
from manim_engine.primitives.visual_compositions import (  # noqa: E402
    BLUEPRINT_COMPOSITION_REGISTRY, create_blueprint_composition,
)
from pipeline.layout_params import normalize_layout_params  # noqa: E402

BEAT = {
    "svo_action": {"subject": "Router gate", "action_verb": "dispatches", "direct_object": "Top-2 experts",
                   "anchor_word": "experts"},
    "highlight_words": {"token": "#fff", "expert FFN": "#fff", "load balance": "#fff"},
}
DATA = {
    "horizontal_race_bars": {"contestants": [
        {"name": "Ours", "value": 3.0, "display_val": "3.0x", "is_hero": True},
        {"name": "Baseline", "value": 1.0, "display_val": "1.0x"}], "delta_badge": "3x faster on GPT-2"},
    "chalkboard_code_block": {"lines": ["def route(x):", "    return topk(gate(x), 2)"], "filename": "moe.py"},
}
LAYOUTS = sorted({
    name for name, cls in BLUEPRINT_COMPOSITION_REGISTRY.items()
    if name in ("split_flow", "pipeline_stages", "grid_memory", "projection_rays", "barrier_separation",
                "tree_hierarchy", "layer_stack", "convergence_funnel", "catalog_routing", "comparison_side_by_side",
                "vector_flow_field", "neural_activation_wave", "attention_prism_refraction",
                "optimization_landscape", "horizontal_race_bars", "chalkboard_code_block", "paper_figure")
})


@pytest.mark.parametrize("layout", LAYOUTS)
def test_composition_builds_steps_and_animations(layout):
    params, _ = normalize_layout_params(layout, {"title": "Mixture of experts", "sub": "Routing"}, BEAT, "MoE")
    params.update(DATA.get(layout, {}))
    comp = create_blueprint_composition(layout, params)

    fit_to_safe_area(comp, has_formula=True)
    content = getattr(comp, "content_group", comp)
    assert content.width <= SAFE_WIDTH + 0.05
    assert content.get_top()[1] <= SAFE_TOP + 0.05
    assert content.get_bottom()[1] >= SAFE_BOTTOM_WITH_FORMULA - 0.05

    steps = get_build_steps(comp)
    assert 1 <= len(steps) <= 6
    for step in steps:
        anim = reveal_step(step, 0.8)
        assert isinstance(anim, manim.Animation)
    assert isinstance(focus_animation(comp, 1.0), manim.Animation)


def test_no_demo_labels_in_split_flow():
    params, _ = normalize_layout_params("split_flow", {"title": "T"}, BEAT, "MoE")
    comp = create_blueprint_composition("split_flow", params)
    texts = [getattr(m, "original_text", "") for m in comp.get_family()]
    assert not {"SEMANTIC STREAM", "GEOMETRIC STREAM", "DISPATCH ROUTER"} & set(texts)
