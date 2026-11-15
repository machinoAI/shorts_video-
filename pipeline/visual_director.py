"""
The Model Verse — Script-Driven Visual Director (Visual Engine 4.0)
Reads the voiceover script, conceptual shifts, and physical analogies for each beat,
and maps them to full-screen composable Manim visual primitives and authentic arXiv figures.
Eliminates canned toy motifs and fragile SVG synthesizers.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from pipeline.config import WORKSPACE_ROOT
from manim_engine.primitives.visual_compositions import BLUEPRINT_COMPOSITION_REGISTRY

VISUAL_ASSETS_DIR = PROJECT_ROOT / "public" / "visual_assets"
VISUAL_ASSETS_DIR.mkdir(parents=True, exist_ok=True)


class VisualDirector:
    """
    Script-Driven Visual Director that designs bespoke graphic scenes for every beat.
    Directly aligns voiceover beats to intuitive, full-screen 3Blue1Brown visual compositions.
    """

    NUMERIC_LAYOUTS = {
        "horizontal_race_bars", "race_bars", "benchmark_race", "drag_race_bars", "comparative_bars",
        "radar_pareto_plot", "radar_plot", "spider_chart", "pareto_frontier", "pareto_tradeoff",
    }
    RADAR_LAYOUTS = {"radar_pareto_plot", "radar_plot", "spider_chart", "pareto_frontier", "pareto_tradeoff"}

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")

    @staticmethod
    def _contestant_params(benchmark: Any) -> List[Dict[str, Any]]:
        return [
            {"name": c.name, "value": c.value, "display_val": c.raw_str, "is_hero": c.is_hero, "color": c.color}
            for c in benchmark.contestants
        ]

    CODE_LAYOUTS = {
        "chalkboard_code_block", "chalkboard_code", "code_block", "code_execution_trace",
        "syntax_code_block", "code_kernel", "ast_code_trace", "ast_tree",
    }

    def _numeric_layout_has_data(self, blueprint: Dict[str, Any], verified_benchmark: Any, verified_code: bool = False) -> bool:
        """
        True if the blueprint is a plain layout, or a data layout with real data to show.
        Fills race-bar contestants from the verified benchmark when the blueprint has none.
        A numeric/code layout without data would otherwise render the primitive's demo
        numbers or demo code, or invented values from the LLM.
        """
        layout = blueprint.get("layout")
        if layout in self.CODE_LAYOUTS:
            return verified_code  # code layouts are filled from the repo snippet by the code branch
        if layout not in self.NUMERIC_LAYOUTS:
            return True
        params = blueprint.get("params") if isinstance(blueprint.get("params"), dict) else {}
        if layout in self.RADAR_LAYOUTS:
            return bool(params.get("models") or blueprint.get("models"))
        if params.get("contestants") or blueprint.get("contestants"):
            return True
        if verified_benchmark is not None:
            params = dict(params)
            params["contestants"] = self._contestant_params(verified_benchmark)
            params.setdefault("metric_name", verified_benchmark.metric_name)
            params.setdefault("unit", verified_benchmark.unit)
            if verified_benchmark.delta_badge:
                params.setdefault("delta_badge", verified_benchmark.delta_badge)
            blueprint["params"] = params
            return True
        return False

    def synthesize_visual_blueprint(
        self,
        beat: Dict[str, Any],
        topic: str,
        beat_id: int,
        used_layouts: Optional[set] = None,
        verified_benchmark: Any = None,
        verified_code: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Derives a rich, context-specific visual blueprint for a beat if not already provided
        by the script generator. Analyzes spoken text, visual focus, analogies, and SVO actions.
        Guarantees layout diversity so no two beats in the same video repeat the same layout.
        """
        used = used_layouts or set()
        text = (beat.get("text", "") + " " + beat.get("visual_focus", "") + " " + str(beat.get("everyday_analogy", ""))).lower()
        svo = beat.get("svo_action", {})
        hl_keys = list(beat.get("highlight_words", {}).keys())

        subj = svo.get("subject", hl_keys[0] if hl_keys else "Signal Stream")
        action = svo.get("action_verb", "transforms")
        obj = svo.get("direct_object", hl_keys[1] if len(hl_keys) > 1 else "Latent Output")
        v_focus = beat.get("visual_focus", "")

        candidates = []

        # Physics Simulation 1: Vector Flow Field / Continuous Latent Trajectory
        if any(k in text for k in ["vector", "flow", "drift", "field", "manifold", "trajectory", "stream", "continuous", "velocity", "diffusion", "denois", "fluid"]):
            candidates.append({
                "layout": "vector_flow_field",
                "title": f"VECTOR FLOW FIELD: {subj.upper()[:16]}",
                "sub": v_focus[:65] or "Continuous velocity streamlines guiding latent trajectory drift",
                "accent_color": "#38BDF8",
                "field_title": f"CONTINUOUS {topic.upper()[:16]} MANIFOLD",
                "source_label": f"SOURCE: {subj.upper()[:14]}",
                "target_label": f"TARGET: {obj.upper()[:14]}",
                "stream_formula": "dx/dt = v_theta(x, t)"
            })

        # Physics Simulation 2: Neural Activation Wave / Synaptic Network
        if any(k in text for k in ["neural", "activation", "synap", "network", "pulse", "firing", "deep layer", "neuron", "forward pass", "cascade"]):
            candidates.append({
                "layout": "neural_activation_wave",
                "title": f"SYNAPTIC PROPAGATION: {subj.upper()[:14]}",
                "sub": v_focus[:65] or "Propagating activation wave across dense synaptic layers",
                "accent_color": "#A855F7",
                "input_label": f"L1: {subj.upper()[:14]}",
                "hidden_label": "L2: LATENT REASONING",
                "output_label": f"L3: {obj.upper()[:14]}"
            })

        # Physics Simulation 3: Attention Prism Refraction / Optical Splitting
        if any(k in text for k in ["prism", "attention", "refract", "query", "key", "value", "qkv", "beam", "optical", "token split"]):
            candidates.append({
                "layout": "attention_prism_refraction",
                "title": "ATTENTION PRISM REFRACTION",
                "sub": v_focus[:65] or "Token laser beam refracted into Query, Key, and Value vectors",
                "accent_color": "#F59E0B",
                "token_label": f"TOKEN: {subj.upper()[:14]}",
                "matrix_title": f"{topic.upper()[:16]} ATTENTION"
            })

        # Physics Simulation 4: 2.5D Loss Landscape / Gradient Descent Basin
        if any(k in text for k in ["loss", "landscape", "surface", "gradient", "basin", "descent", "roll", "valley", "minimum", "optimiz", "energy"]):
            candidates.append({
                "layout": "optimization_landscape",
                "title": "LOSS LANDSCAPE DESCENT",
                "sub": v_focus[:65] or "Optimization trajectory rolling through energy basin into global minimum",
                "accent_color": "#34D399",
                "landscape_title": f"{topic.upper()[:16]} OBJECTIVE SURFACE",
                "optima_label": f"OPTIMA: {obj.upper()[:14]}"
            })

        # 1. Split / Diverging / Bifurcated Flow
        if any(k in text for k in ["split", "dual", "bifurcat", "two path", "branch", "two stream", "decoupl", "separate semantic"]):
            candidates.append({
                "layout": "split_flow",
                "title": f"BIFURCATED ROUTING: {subj.upper()[:18]}",
                "sub": v_focus[:65] or "Decoupling high-level semantics from low-level geometric depth",
                "accent_color": "#38BDF8",
                "input_label": f"UNIFIED {topic.upper()[:16]} STREAM",
                "router_label": f"{subj.upper()[:14]} ROUTER",
                "branch_a_label": f"STREAM A: {subj.upper()[:14]}",
                "branch_a_sub": "Semantic Representation",
                "branch_b_label": f"STREAM B: {obj.upper()[:14]}",
                "branch_b_sub": "Geometric Spatial Depth"
            })

        # 2. Catalog / Library / Index / Drawer Dispatch
        if any(k in text for k in ["library", "catalog", "index", "desk", "drawer", "dispatch", "sort", "unbounded"]):
            candidates.append({
                "layout": "catalog_routing",
                "title": f"CENTRAL INDEX DISPATCH: {subj.upper()[:16]}",
                "sub": v_focus[:65] or "Instant O(1) hash map routing queries to specialized drawers",
                "accent_color": "#38BDF8",
                "index_label": f"{topic.upper()[:18]} INDEX DESK",
                "drawer_a_label": f"EXPERT 1: {subj[:12]}",
                "drawer_b_label": f"EXPERT 2: {obj[:12]}",
                "drawer_c_label": "EXPERT 3: REASONING"
            })

        # 3. Camera / Spatial Ray-casting / Perspective / Coordinates
        if any(k in text for k in ["camera math", "camera rays", "projective", "perspective", "sightline", "ray", "focal plane"]):
            candidates.append({
                "layout": "projection_rays",
                "title": f"PROJECTIVE GEOMETRY: {subj.upper()[:18]}",
                "sub": v_focus[:65] or "Mapping camera rays to local stored spatial feature anchors",
                "accent_color": "#38BDF8",
                "camera_label": "OBSERVER CAMERA POSE",
                "focal_plane_label": f"{topic.upper()[:18]} FOCAL PLANE",
                "target_label": f"ANCHOR: {obj.upper()[:22]}"
            })

        # 4. Memory / Cache / Grid / Matrix / Spatial Slots
        if any(k in text for k in ["memory", "grid", "cache", "kv", "buffer", "matrix", "cell", "store", "slot"]):
            candidates.append({
                "layout": "grid_memory",
                "title": f"SPATIAL MEMORY MATRIX: {subj.upper()[:18]}",
                "sub": v_focus[:65] or "O(1) constant-latency query over persistent memory grid",
                "accent_color": "#38BDF8",
                "grid_title": f"{topic.upper()[:22]} COORDINATE GRID",
                "active_cell_label": f"HIT: {subj.upper()[:14]}",
                "efficiency_label": "O(1) CONSTANT LATENCY"
            })

        # Showdown: Horizontal Benchmark Race Bars — only with verified numbers.
        # (A radar plot is never synthesized here: we have no real multi-metric data.)
        if verified_benchmark is not None and any(k in text for k in ["throughput", "tflops", "race", "speedup", "faster", "benchmark", "leaderboard", "tokens/s", "drag race", "baseline", "outperform", "gflops", "speed", "accuracy", "score"]):
            candidates.append({
                "layout": "horizontal_race_bars",
                "title": verified_benchmark.title,
                "sub": v_focus[:65] or "Results reported in the paper",
                "accent_color": "#10B981",
                "metric_name": verified_benchmark.metric_name,
                "unit": verified_benchmark.unit,
                "contestants": self._contestant_params(verified_benchmark),
                "delta_badge": verified_benchmark.delta_badge
            })

        # Code Execution: Chalkboard Code Block — only with real repository code.
        # (Previously this generated fake lines like `def execute_<verb>(tensor_in): ...`.)
        if verified_code and verified_code.get("lines") and (beat_id in [3, 4, 5] or beat_id is None) and any(k in (text + " " + topic.lower()) for k in ["function", "kernel", "algorithm", "implementation", "compile", "python", "cuda", "syntax", "source code", "snippet"]):
            candidates.append({
                "layout": "chalkboard_code_block",
                "title": f"KERNEL IMPLEMENTATION: {subj.upper()[:16]}",
                "sub": v_focus[:65] or "Core loop from the open-source repository",
                "accent_color": "#38BDF8",
                "filename": verified_code.get("filename", "kernel.py"),
                "language": verified_code.get("language", "python"),
                "lines": verified_code.get("lines", []),
                "highlight_lines": verified_code.get("highlight_lines", [1]),
                "trace_register": verified_code.get("trace_register", f"⚡ ACTIVE STATE: {obj.upper()[:24]}"),
                "delta_badge": (verified_code.get("explanation") or "")[:52]
            })

        # 5. Mirror / Blur / Contrast / Side-by-Side Comparison
        if any(k in text for k in ["mirror", "reflection", "forget", "blur", "versus", "compare", "traditional", "prior", "baseline", "monolithic"]):
            candidates.append({
                "layout": "comparison_side_by_side",
                "title": f"COHERENCE VS DECAY: {subj.upper()[:16]}",
                "sub": v_focus[:65] or "Contrasting persistent spatial memory against temporal decay",
                "accent_color": "#34D399",
                "col_a_title": "TEMPORAL FORGETTING",
                "col_a_stat": "Blur & Memory Wipeout",
                "col_b_title": f"{topic.upper()[:14]} PERSISTENCE",
                "col_b_stat": "O(1) Sharp Coherence"
            })

        # 6. Barrier / Wall / Penalty / Anti-bleed / Isolation
        if any(k in text for k in ["barrier", "wall", "penalty", "bleed", "isolate", "prevent", "guard", "forcefield"]):
            candidates.append({
                "layout": "barrier_separation",
                "title": f"ORTHOGONAL BARRIER: {subj.upper()[:18]}",
                "sub": v_focus[:65] or "Strict penalty prevents cross-talk between latent streams",
                "accent_color": "#EF4444",
                "stream_a_label": f"STREAM 1: {subj.upper()[:14]}",
                "stream_b_label": f"STREAM 2: {obj.upper()[:14]}",
                "barrier_label": "ORTHOGONAL PENALTY BARRIER",
                "barrier_sub": "Zero cross-stream interference"
            })

        # 7. Tree / Decision Hierarchy / Search / Reasoning / Choice
        if any(k in text for k in ["tree", "search", "mcts", "reason", "decision", "choice", "prun", "binary game"]):
            candidates.append({
                "layout": "tree_hierarchy",
                "title": f"DECISION TREE: {subj.upper()[:18]}",
                "sub": v_focus[:65] or "Pruning low-confidence candidates to isolate optimal choice",
                "accent_color": "#34D399",
                "root_label": f"{topic.upper()[:16]} QUERY",
                "optimal_label": f"CHOSEN: {subj.upper()[:16]}",
                "pruned_label": "PRUNED DEAD END"
            })

        # 8. Stack / Layers / Judgment / Deep Hierarchy
        if any(k in text for k in ["layer", "stack", "deep", "hierarchy", "level", "judgment", "scores"]):
            candidates.append({
                "layout": "layer_stack",
                "title": f"LAYERED COMPOSITION: {subj.upper()[:18]}",
                "sub": v_focus[:65] or "Hierarchical abstraction assembling high-confidence decisions",
                "accent_color": "#38BDF8",
                "bottom_layer": f"L1: {subj.upper()[:18]} INPUTS",
                "mid_layer": "L2: ROUTING & CONFIDENCE",
                "top_layer": f"L3: {obj.upper()[:18]} OUTPUT"
            })

        # 9. Convergence / Funnel / Multimodal Fusion
        if any(k in text for k in ["funnel", "multimodal", "fuse", "combine", "converge", "aggregate", "condens"]):
            candidates.append({
                "layout": "convergence_funnel",
                "title": f"MULTIMODAL FUSION: {subj.upper()[:18]}",
                "sub": v_focus[:65] or "Harmonizing multiple streams into a unified representation",
                "accent_color": "#38BDF8",
                "input_1_label": "STREAM A",
                "input_2_label": f"{subj[:12]}",
                "input_3_label": f"{obj[:12]}",
                "fused_label": f"{topic.upper()[:20]} UNIFIED CORE"
            })

        # Default fallback candidate: Sequential Pipeline Stages
        pipeline_cand = {
            "layout": "pipeline_stages",
            "title": f"{topic.upper()[:20]}: {subj.upper()[:16]}",
            "sub": v_focus[:65] or f"Sequential transformation from {subj.lower()} to {obj.lower()}",
            "accent_color": "#38BDF8",
            "stage_1_label": f"STAGE 1: {subj.upper()[:18]}",
            "stage_1_sub": "Raw high-dimensional inputs",
            "stage_2_label": f"STAGE 2: {action.upper()[:18]} ENGINE",
            "stage_2_sub": "Core mathematical transformation",
            "stage_3_label": f"STAGE 3: {obj.upper()[:18]}",
            "stage_3_sub": "Target reconstructed state"
        }
        candidates.append(pipeline_cand)

        # Score and sort candidates using Retention Genome evolutionary multipliers (Engine 7.0)
        try:
            from pipeline.retention_genome import retention_genome
            sorted_candidates = sorted(
                candidates,
                key=lambda c: retention_genome.get_blueprint_multiplier(c.get("layout", "")),
                reverse=True
            )
        except Exception:
            sorted_candidates = candidates

        # Select highest-retention candidate not already used in this video
        for cand in sorted_candidates:
            if cand["layout"] not in used:
                return cand

        # Keyword matches exhausted: rotate through other non-numeric layouts so beats
        # that lost a fake race-bar / code visual don't all collapse to pipeline_stages.
        generic_fallbacks = [
            {
                "layout": "layer_stack",
                "title": f"LAYERED VIEW: {subj.upper()[:18]}",
                "sub": v_focus[:65] or f"How {subj.lower()} builds up to {obj.lower()}",
                "accent_color": "#38BDF8",
                "bottom_layer": f"L1: {subj.upper()[:18]}",
                "mid_layer": f"L2: {action.upper()[:18]}",
                "top_layer": f"L3: {obj.upper()[:18]}"
            },
            {
                "layout": "split_flow",
                "title": f"BEFORE VS AFTER: {subj.upper()[:16]}",
                "sub": v_focus[:65] or f"Contrasting the old path with {subj.lower()}",
                "accent_color": "#34D399",
                "input_label": f"{topic.upper()[:18]} INPUT",
                "router_label": f"{action.upper()[:14]}",
                "branch_a_label": "BASELINE PATH",
                "branch_a_sub": "Prior approach",
                "branch_b_label": f"{subj.upper()[:16]}",
                "branch_b_sub": f"{obj[:24]}"
            },
            {
                "layout": "convergence_funnel",
                "title": f"WHAT IT COMBINES: {subj.upper()[:16]}",
                "sub": v_focus[:65] or f"Inputs converging into {obj.lower()}",
                "accent_color": "#A855F7",
                "input_1_label": f"{subj[:12]}",
                "input_2_label": f"{action[:12]}",
                "input_3_label": f"{obj[:12]}",
                "fused_label": f"{topic.upper()[:20]}"
            },
            {
                "layout": "tree_hierarchy",
                "title": f"DECISION PATH: {subj.upper()[:18]}",
                "sub": v_focus[:65] or f"Which branch leads to {obj.lower()}",
                "accent_color": "#F59E0B",
                "root_label": f"{topic.upper()[:16]}",
                "optimal_label": f"{obj.upper()[:16]}",
                "pruned_label": "DISCARDED PATH"
            },
        ]
        for cand in generic_fallbacks:
            if cand["layout"] not in used:
                return cand

        # If all candidates used, fallback to the top match
        return sorted_candidates[0]

    def prepare_storyboard_for_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plans the visual choreography for each beat based on the voiceover script.
        Assigns:
          - Beat 5: comparative_bars
          - Beat 3: paper_figure (if authentic arXiv vector diagram is available)
          - Beats 1, 2, 4 (and Beat 3 if no paper figure): composable visual blueprint
        """
        clean_id = re.sub(r"[^a-zA-Z0-9_\-]", "_", spec.get("id", "short_topic")).lower()
        topic = spec.get("title", clean_id)
        beats = spec.get("beats", [])
        paper_figures = [f for f in spec.get("paper_figures", []) if isinstance(f, dict)]
        arxiv_target = spec.get("arxiv_id")
        if not paper_figures and arxiv_target and not str(arxiv_target).startswith("perk_") and not str(arxiv_target).startswith("gh_"):
            try:
                from pipeline.arxiv_vector_extractor import extract_paper_figures, clean_arxiv_id
                clean_id = clean_arxiv_id(str(arxiv_target))
                print(f"   ℹ️ VisualDirector fallback: lazily extracting paper figures for arXiv '{clean_id}'...")
                extracted = extract_paper_figures(clean_id, max_figures=5)
                paper_figures = [f for f in extracted if isinstance(f, dict)]
                if paper_figures:
                    spec["paper_figures"] = paper_figures
            except Exception as e_figs:
                print(f"⚠️ VisualDirector fallback figure extraction notice: {e_figs}")

        used_layouts = set()

        # Benchmark numbers backed by the spec (grounded) or the paper's LaTeX tables.
        # None means there is nothing real to chart, so no beat gets a numeric layout.
        from pipeline.benchmark_extractor import BenchmarkExtractor
        verified_benchmark = BenchmarkExtractor().extract_verified(spec)
        from pipeline.grounding import has_verified_code
        verified_code = has_verified_code(spec)
        if spec.get("code_snippet") and not verified_code:
            print("   ℹ️ Ignoring code_snippet: not from a real repository (no repo_metadata or placeholder code).")
        if verified_benchmark is None:
            print("   ℹ️ No verified benchmark numbers found — numeric layouts (race bars / radar) disabled for this video.")

        print(f"\n🎬 [VisualDirector 4.0] Designing Script-Driven Visual Storyboard for '{topic}'...")

        for i, b in enumerate(beats):
            b_id = b.get("beat_id", i + 1)
            if b_id > 5:
                continue

            # -------------------------------------------------------------
            # BEAT 5: Automated Showdown & Benchmark Visualizer (Visual Engine 5.0)
            # -------------------------------------------------------------
            if b_id == 5 and verified_benchmark is not None:
                v_foc = b.get("visual_focus", "")
                if len(v_foc) > 55:
                    v_foc = v_foc[:55].rsplit(" ", 1)[0]

                b_comp = verified_benchmark

                b_text = (b.get("text", "") + " " + v_foc).lower()
                if b_comp.radar_models and any(k in b_text for k in ["radar", "spider", "pareto", "tradeoff", "trade-off", "frontier", "dimensions"]):
                    layout_name = "radar_pareto_plot"
                    params = {
                        "title": f"PARETO FRONTIER: {topic.upper()[:18]}",
                        "sub": v_foc or "Multi-dimensional performance tradeoff across frontier architectures",
                        "axes": b_comp.radar_axes,
                        "models": b_comp.radar_models,
                        "delta_badge": b_comp.delta_badge
                    }
                    action = "pulse"
                else:
                    layout_name = "horizontal_race_bars"
                    params = {
                        "title": b_comp.title,
                        "sub": v_foc or "Quantitative empirical evaluation against frontier baselines",
                        "metric_name": b_comp.metric_name,
                        "unit": b_comp.unit,
                        "contestants": [
                            {
                                "name": c.name,
                                "value": c.value,
                                "display_val": c.raw_str,
                                "is_hero": c.is_hero,
                                "color": c.color
                            }
                            for c in b_comp.contestants
                        ],
                        "delta_badge": b_comp.delta_badge
                    }
                    action = "bar_fill"

                b["motif_type"] = layout_name
                b["kinetic_action"] = action
                b["visual_blueprint"] = {
                    "layout": layout_name,
                    "title": params["title"],
                    "sub": params["sub"],
                    "params": params
                }
                b["motif_params"] = params
                used_layouts.add(layout_name)
                print(f"   ✨ Beat 5: Assigned '{layout_name}' (Automated Benchmark Showdown)")
                continue


            # -------------------------------------------------------------
            # BEAT 3: Authentic Paper Figure (if extracted from arXiv)
            # -------------------------------------------------------------
            if paper_figures and b_id == 3:
                top_fig = paper_figures[0]
                if not isinstance(top_fig, dict):
                    top_fig = {}
                fig_svg = top_fig.get("svg_path")
                fig_img = top_fig.get("image_path")
                arxiv_id = spec.get("arxiv_id") or ""

                # Resolve relative paths if cached
                if fig_svg and not os.path.exists(fig_svg):
                    if (PROJECT_ROOT / fig_svg).exists():
                        fig_svg = str(PROJECT_ROOT / fig_svg)
                    else:
                        rel_match = re.search(r"(public/arxiv_cache/.*)", fig_svg)
                        if rel_match:
                            loc = str(PROJECT_ROOT / rel_match.group(1))
                            if os.path.exists(loc):
                                fig_svg = loc
                            else:
                                fig_svg = None

                if fig_img and not os.path.exists(fig_img):
                    if (PROJECT_ROOT / fig_img).exists():
                        fig_img = str(PROJECT_ROOT / fig_img)
                    else:
                        rel_match = re.search(r"(public/arxiv_cache/.*)", fig_img)
                        if rel_match:
                            loc = str(PROJECT_ROOT / rel_match.group(1))
                            if os.path.exists(loc):
                                fig_img = loc
                            else:
                                fig_img = None

                if (fig_svg and os.path.exists(fig_svg)) or (fig_img and os.path.exists(fig_img)):
                    topic_core = topic.split(":")[0].strip().upper()
                    fig_title = f"{topic_core[:18]} ARCHITECTURE"
                    b["motif_type"] = "paper_figure"
                    b["visual_blueprint"] = {
                        "layout": "paper_figure",
                        "title": fig_title,
                        "sub": b.get("visual_focus", "")[:65] or "Official architectural diagram from arXiv source",
                        "params": {
                            "svg_path": fig_svg,
                            "image_path": fig_img,
                            "arxiv_id": arxiv_id,
                            "title": fig_title,
                            "sub": b.get("visual_focus", "")[:65] or "Official architectural diagram from arXiv source",
                            "badge_text": "PRIMARY ARCHITECTURE SPECIFICATION",
                            "caption": top_fig.get("caption", "Architecture Overview"),
                            "preferred_renderer": "vector" if fig_svg else "raster"
                        }
                    }
                    b["motif_params"] = b["visual_blueprint"]["params"]
                    b["kinetic_action"] = "figure_scan"
                    used_layouts.add("paper_figure")
                    active_path = fig_svg or fig_img
                    print(f"   ✨ Beat 3: Assigned Authentic arXiv Paper Diagram '{os.path.basename(active_path)}'")
                    continue

            # -------------------------------------------------------------
            # BEAT 3 or 4: Open-Source Code Kernel (if code_snippet present)
            # -------------------------------------------------------------
            code_data = spec.get("code_snippet") if verified_code else None
            if code_data and "chalkboard_code_block" not in used_layouts and (b_id == 4 or (b_id == 3 and not paper_figures)):
                code_filename = code_data.get("filename", "kernel.py")
                b["motif_type"] = "chalkboard_code_block"
                b["kinetic_action"] = "pulse"
                code_params = {
                    "title": f"KERNEL CODE: {topic.upper()[:18]}",
                    "sub": b.get("visual_focus", "")[:65] or "Open-source kernel executing inside GPU memory",
                    "filename": code_filename,
                    "language": code_data.get("language", "python"),
                    "lines": code_data.get("lines", []),
                    "highlight_lines": code_data.get("highlight_lines", [2, 3]),
                    "trace_register": code_data.get("trace_register", "⚡ ACTIVE STATE TRACE"),
                    "delta_badge": code_data.get("explanation", "⚡ ZERO OVERHEAD HARDWARE KERNEL")[:52]
                }
                b["visual_blueprint"] = {
                    "layout": "chalkboard_code_block",
                    "title": code_params["title"],
                    "sub": code_params["sub"],
                    "params": code_params
                }
                b["motif_params"] = code_params
                used_layouts.add("chalkboard_code_block")
                print(f"   ✨ Beat {b_id}: Assigned 'chalkboard_code_block' ({code_filename})")
                continue

            # -------------------------------------------------------------
            # NARRATIVE BEATS (1, 2, 4, and 3 without paper figure):
            # Composable Visual Blueprint (Visual Engine 4.0)
            # -------------------------------------------------------------
            blueprint = b.get("visual_blueprint")
            if (
                not blueprint or not isinstance(blueprint, dict) or not blueprint.get("layout")
                or blueprint.get("layout") in used_layouts
                or not self._numeric_layout_has_data(blueprint, verified_benchmark, verified_code)
            ):
                blueprint = self.synthesize_visual_blueprint(
                    b, topic, b_id, used_layouts=used_layouts, verified_benchmark=verified_benchmark,
                    verified_code=spec.get("code_snippet") if verified_code else None
                )
                b["visual_blueprint"] = blueprint

            layout = blueprint.get("layout", "pipeline_stages")
            used_layouts.add(layout)
            params = blueprint.get("params", {})
            # Flatten top-level blueprint metadata into params for the composition
            composition_params = {
                "layout": layout,
                "title": blueprint.get("title", f"{topic.upper()[:22]}: BEAT {b_id}"),
                "sub": blueprint.get("sub", b.get("visual_focus", "")[:65]),
                "accent_color": blueprint.get("accent_color", "#38BDF8"),
            }
            # Merge any explicit sub-params
            for k, v in blueprint.items():
                if k not in ["layout", "title", "sub", "accent_color", "params"]:
                    composition_params[k] = v
            if isinstance(params, dict):
                composition_params.update(params)

            b["motif_type"] = "visual_composition"
            b["motif_params"] = composition_params
            b["kinetic_action"] = "blueprint_transform"
            print(f"   ✨ Beat {b_id}: Assigned Composable Visual Blueprint '{layout}' ({composition_params.get('title')})")

        spec["script_driven_visuals"] = True
        return spec
