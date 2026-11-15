"""
Normalizes visual-blueprint parameters so diagrams never fall back to placeholder labels.

Each diagram class has fixed constructor parameter names (e.g. split_flow takes
branch_a_label). The scriptwriter often used other names (left_label, flow_status) or
left params empty; the constructor silently ignored them and rendered its built-in demo
labels ("SEMANTIC STREAM", "GEOMETRIC STREAM", ...). That happened in ~48% of beats.

normalize_layout_params():
  1. keeps params whose names the diagram accepts,
  2. moves mis-named string params into the diagram's unfilled label slots,
  3. fills remaining slots from the beat itself (SVO subject / action / object,
     highlighted key terms, topic),
and reports which slots had to be filled so callers can log it.
Pure Python (no Manim) so it is unit-testable.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from manim_engine.primitives.text_utils import trim_words

# Role keys: SUBJ, ACTION, OBJ, H1..H3 (highlighted terms), TOPIC, BLANK
LAYOUT_SLOTS: Dict[str, List[Tuple[str, str]]] = {
    "split_flow": [("input_label", "SUBJ"), ("router_label", "ACTION"), ("branch_a_label", "H1"),
                   ("branch_a_sub", "BLANK"), ("branch_b_label", "H2"), ("branch_b_sub", "BLANK")],
    "pipeline_stages": [("stage_1_label", "SUBJ"), ("stage_1_sub", "BLANK"), ("stage_2_label", "ACTION"),
                        ("stage_2_sub", "BLANK"), ("stage_3_label", "OBJ"), ("stage_3_sub", "BLANK")],
    "grid_memory": [("grid_title", "SUBJ"), ("active_cell_label", "OBJ"), ("efficiency_label", "H1")],
    "projection_rays": [("camera_label", "SUBJ"), ("focal_plane_label", "ACTION"), ("target_label", "OBJ")],
    "barrier_separation": [("stream_a_label", "H1"), ("stream_b_label", "H2"), ("barrier_label", "SUBJ"),
                           ("barrier_sub", "BLANK")],
    "tree_hierarchy": [("root_label", "SUBJ"), ("optimal_label", "OBJ"), ("pruned_label", "H1")],
    "layer_stack": [("bottom_layer", "SUBJ"), ("mid_layer", "ACTION"), ("top_layer", "OBJ")],
    "convergence_funnel": [("input_1_label", "H1"), ("input_2_label", "H2"), ("input_3_label", "H3"),
                           ("fused_label", "OBJ")],
    "catalog_routing": [("index_label", "SUBJ"), ("drawer_a_label", "H1"), ("drawer_b_label", "OBJ"),
                        ("drawer_c_label", "H2")],
    "comparison_side_by_side": [("col_a_title", "H1"), ("col_b_title", "SUBJ")],
    "vector_flow_field": [("field_title", "TOPIC"), ("source_label", "SUBJ"), ("target_label", "OBJ"),
                          ("stream_formula", "BLANK")],
    "neural_activation_wave": [("input_label", "SUBJ"), ("hidden_label", "ACTION"), ("output_label", "OBJ")],
    "attention_prism_refraction": [("token_label", "SUBJ"), ("matrix_title", "OBJ")],
    "optimization_landscape": [("landscape_title", "TOPIC"), ("optima_label", "OBJ")],
}

ALIASES = {
    "dual_stream": "split_flow", "bifurcated_tracks": "split_flow",
    "sequential_flow": "pipeline_stages",
    "spatial_matrix": "grid_memory", "kv_cache_grid": "grid_memory",
    "camera_geometry": "projection_rays",
    "anti_bleed_barrier": "barrier_separation",
    "branching_search": "tree_hierarchy",
    "hierarchical_composition": "layer_stack",
    "multimodal_fusion": "convergence_funnel",
    "index_dispatch": "catalog_routing",
    "side_by_side": "comparison_side_by_side",
    "flow_field": "vector_flow_field", "latent_manifold": "vector_flow_field", "continuous_dynamics": "vector_flow_field",
    "synaptic_network": "neural_activation_wave", "deep_network": "neural_activation_wave",
    "sparse_autoencoder": "neural_activation_wave",
    "prism_refraction": "attention_prism_refraction", "optical_routing": "attention_prism_refraction",
    "qkv_projection": "attention_prism_refraction",
    "loss_landscape": "optimization_landscape", "gradient_descent": "optimization_landscape",
    "convergence_basin": "optimization_landscape",
}

# Last-resort neutral text per role (used only when the beat offers nothing).
NEUTRAL = {"SUBJ": "INPUT", "ACTION": "PROCESS", "OBJ": "OUTPUT", "H1": "OPTION A", "H2": "OPTION B",
           "H3": "OPTION C", "TOPIC": "HOW IT WORKS", "BLANK": " "}

_PLACEHOLDER = re.compile(r"^\s*(\.\.\.|<.*>|param_key_\d+|specific descriptive label|label|n/?a|none|null)?\s*$", re.I)


def canonical_layout(layout: Optional[str]) -> Optional[str]:
    if not layout:
        return None
    return ALIASES.get(layout, layout)


def _clean_phrase(text: Any, max_chars: int = 26) -> str:
    s = re.sub(r"[_]+", " ", str(text or "")).strip()
    s = re.sub(r"\s+", " ", s)
    return trim_words(s, max_chars)


def beat_roles(beat: Dict[str, Any], topic: str = "") -> Dict[str, str]:
    """Short phrases describing the beat, used to label diagram parts."""
    svo = beat.get("svo_action") or {}
    highlights = [k for k in (beat.get("highlight_words") or {}).keys() if isinstance(k, str)]
    subj = _clean_phrase(svo.get("subject"))
    obj = _clean_phrase(svo.get("direct_object"))
    action = _clean_phrase(svo.get("action_verb"), 18)

    pool: List[str] = []
    for h in highlights:
        p = _clean_phrase(h)
        if p and p.lower() not in {x.lower() for x in pool} and p.lower() not in (subj.lower(), obj.lower()):
            pool.append(p)

    roles = {
        "SUBJ": subj or (pool[0] if pool else ""),
        "ACTION": action,
        "OBJ": obj or (pool[1] if len(pool) > 1 else ""),
        "TOPIC": _clean_phrase(topic, 30),
        "BLANK": " ",
    }
    used = {roles["SUBJ"].lower(), roles["OBJ"].lower()}
    extras = [p for p in pool if p.lower() not in used]
    for i, key in enumerate(("H1", "H2", "H3")):
        roles[key] = extras[i] if i < len(extras) else ""
    return roles


RESERVED_KEYS = {"layout", "title", "sub", "accent_color", "motif_type", "kinetic_action"}

_KEY_HINTS = {
    "left": {"a", "1", "left"},
    "right": {"b", "2", "right"},
    "first": {"a", "1"}, "second": {"b", "2"}, "third": {"c", "3"},
    "input": {"input", "source", "1", "bottom", "root", "index", "camera", "token"},
    "source": {"input", "source", "1", "bottom", "root"},
    "output": {"output", "target", "optimal", "top", "fused", "3"},
    "target": {"output", "target", "optimal", "top", "fused"},
    "router": {"router", "index", "hidden", "mid", "2", "barrier"},
    "middle": {"mid", "hidden", "2", "router"},
}


def _slot_affinity(key: str, slot: str) -> int:
    k_tokens = set(re.split(r"[_\W]+", key.lower())) - {""}
    s_tokens = set(re.split(r"[_\W]+", slot.lower())) - {""}
    score = 2 * len(k_tokens & s_tokens - {"label", "title"})
    for tok in k_tokens:
        score += len(_KEY_HINTS.get(tok, set()) & s_tokens)
    return score


def _is_placeholder(val: Any) -> bool:
    return not isinstance(val, str) or bool(_PLACEHOLDER.match(val))


def normalize_layout_params(
    layout: Optional[str],
    params: Optional[Dict[str, Any]],
    beat: Dict[str, Any],
    topic: str = "",
) -> Tuple[Dict[str, Any], List[str]]:
    """Returns (params for the diagram constructor, list of slots filled from the beat)."""
    params = dict(params or {})
    canon = canonical_layout(layout)
    slots = LAYOUT_SLOTS.get(canon or "")
    if not slots:
        return params, []

    slot_names = [s for s, _ in slots]
    out: Dict[str, Any] = {k: v for k, v in params.items() if k not in slot_names}
    for name in slot_names:
        val = params.get(name)
        if not _is_placeholder(val):
            out[name] = val

    # Mis-named label-like params -> the best-matching unfilled label slot
    stray = [(k, v) for k, v in params.items()
             if k not in slot_names and k not in RESERVED_KEYS and isinstance(v, str) and not _is_placeholder(v)
             and re.search(r"(label|title|name|node|stream|stage|layer|input|output|target|source|left|right|status)", k, re.I)]
    open_slots = [name for name, role in slots if name not in out and role != "BLANK"]
    for key, val in stray:
        if not open_slots:
            break
        best = max(open_slots, key=lambda s: (_slot_affinity(key, s), -open_slots.index(s)))
        out[best] = val
        open_slots.remove(best)

    roles = beat_roles(beat, topic)
    filled: List[str] = []
    used_vals = {str(v).lower() for v in out.values() if isinstance(v, str)}
    for name, role in slots:
        if name in out:
            continue
        val = roles.get(role) or ""
        if role != "BLANK" and (not val or val.lower() in used_vals):
            # pick any unused beat phrase before falling back to neutral text
            for alt in ("H1", "H2", "H3", "SUBJ", "OBJ"):
                cand = roles.get(alt) or ""
                if cand and cand.lower() not in used_vals:
                    val = cand
                    break
            else:
                val = NEUTRAL.get(role, " ")
        out[name] = val
        if isinstance(val, str):
            used_vals.add(val.lower())
        filled.append(name)

    # Strip non-constructor junk that used to hide real labels (kept harmlessly otherwise)
    for junk in ("param_key_1", "param_key_2"):
        out.pop(junk, None)
    return out, filled
