"""
The Model Verse — Composable Manim Visual Primitives (Visual Engine 4.0)
Deterministic, full-screen, script-aligned mathematical and algorithmic compositions
for 9:16 mobile YouTube Shorts. Replaces fragile SVG synthesizers and canned toy motifs.

Layouts:
1. BlueprintSplitFlow: Diverging pathways, dual-track routing, semantic vs geometric decoupling.
2. BlueprintPipelineStages: Sequential multi-stage architectures with connecting conduits.
3. BlueprintGridMemory: 2D spatial coordinate memory, KV-cache grid, voxel matrices.
4. BlueprintProjectionRays: Camera projective geometry, ray-casting, coordinate transformation.
5. BlueprintBarrierSeparation: Two distinct latent streams separated by an anti-bleed barrier.
6. BlueprintTreeHierarchy: Decision trees, MCTS search, branching logic with pruning.
7. BlueprintLayerStack: Multi-layer hierarchical representations, stacked latent planes.
8. BlueprintConvergenceFunnel: Multi-input aggregation, bottleneck fusion, unified output.
9. BlueprintCatalogRouting: Central index/router dispatching queries to specialized buckets.
10. BlueprintSideBySideComparison: Direct contrasting architectures (Dense vs Sparse, Monolithic vs Modular).
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import manim_engine.pillow_compat
from manim import *
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from pipeline.config import FONT_HELVETICA
from manim_engine.primitives.typography import CleanText, trim_words
from manim_engine.primitives.isometric import create_isometric_slab, create_isometric_layer_stack

# Standard 3b1b Palette
COLOR_CYAN = "#38BDF8"
COLOR_MINT = "#34D399"
COLOR_AMBER = "#F59E0B"
COLOR_CORAL = "#EF4444"
COLOR_PURPLE = "#A855F7"
COLOR_WHITE = "#F8FAFC"
COLOR_SLATE = "#94A3B8"
COLOR_DARK_SLATE = "#334155"
COLOR_PANEL_BG = "#0D1117"


class BaseBlueprintComposition(Group):
    """Base class for all full-screen script-driven visual compositions."""
    def __init__(
        self,
        title: str = "CONCEPT SPECIFICATION",
        sub: str = "Script-driven architectural visualization",
        accent_color: str = COLOR_CYAN,
        **kwargs
    ):
        # Filter kwargs to only those accepted by Mobject to avoid unexpected keyword errors
        mobject_kwargs = {k: v for k, v in kwargs.items() if k in ("color", "name", "dim", "target", "z_index")}
        super().__init__(**mobject_kwargs)
        self.accent_color = accent_color

        # Clean top titles formatted for 9:16 mobile canvas (word-boundary trimmed, readable on phones)
        self.title = CleanText(
            trim_words(str(title).upper(), 40),
            font=FONT_HELVETICA,
            font_size=20,
            color=accent_color,
            weight=BOLD
        ).move_to([0, 5.3, 0])
        if self.title.width > 7.4:
            self.title.scale_to_fit_width(7.4)

        self.sub = CleanText(
            trim_words(str(sub), 70),
            font=FONT_HELVETICA,
            font_size=13,
            color=COLOR_SLATE,
            weight=NORMAL
        ).next_to(self.title, DOWN, buff=0.15)
        if self.sub.width > 7.4:
            self.sub.scale_to_fit_width(7.4)

        self.content_group = Group()
        self.kinetic_elements = Group()
        # Element outlined on the anchor word by the word-synced choreography (optional)
        self.focus_target = None

    def get_entrance_animation(self, run_time: float = 1.0) -> Animation:
        """Returns the entrance animation for this composition. Defaults to FadeIn."""
        return FadeIn(self, scale=0.96, run_time=run_time)

    def get_kinetic_animation(self, run_time: float = 1.5) -> Animation:
        """Returns the primary kinetic transformation animation for this composition."""
        if self.kinetic_elements and len(self.kinetic_elements) > 0:
            return self.kinetic_elements.animate(rate_func=there_and_back, run_time=run_time).scale(1.04)
        return self.content_group.animate(rate_func=there_and_back, run_time=run_time).scale(1.02)

    def get_ambient_animation(self, run_time: float = 4.0) -> Animation:
        """Returns subtle continuous micro-motion during voiceover speech."""
        return self.content_group.animate(rate_func=there_and_back, run_time=run_time).scale(1.015)


class BlueprintSplitFlow(BaseBlueprintComposition):
    """
    Diverging pathways: Single incoming stream split by a router node into two distinct streams.
    Perfect for: Decoupling semantics from geometry, bifurcated paths, dual decoders.
    """
    def __init__(
        self,
        input_label: str = "UNIFIED INPUT STREAM",
        router_label: str = "DISPATCH ROUTER",
        branch_a_label: str = "SEMANTIC STREAM",
        branch_a_sub: str = "High-Level Context",
        branch_b_label: str = "GEOMETRIC STREAM",
        branch_b_sub: str = "Spatial Depth Map",
        branch_a_color: str = COLOR_CYAN,
        branch_b_color: str = COLOR_AMBER,
        **kwargs
    ):
        super().__init__(**kwargs)

        # 1. Top Input Node
        in_box = RoundedRectangle(corner_radius=0.12, width=4.8, height=0.9, color=COLOR_DARK_SLATE, fill_color=COLOR_PANEL_BG, fill_opacity=0.95, stroke_width=2.5).move_to([0, 3.4, 0])
        in_txt = CleanText(trim_words(input_label, 28).upper(), font=FONT_HELVETICA, font_size=12, color=COLOR_WHITE, weight=BOLD).move_to(in_box)
        in_node = VGroup(in_box, in_txt)

        # 2. Central Splitter / Router Gate
        router_diamond = Polygon(
            [-1.4, 1.4, 0], [0, 2.1, 0], [1.4, 1.4, 0], [0, 0.7, 0],
            color=self.accent_color, fill_color="#0F172A", fill_opacity=0.95, stroke_width=3.0
        )
        router_txt = CleanText(trim_words(router_label, 20).upper(), font=FONT_HELVETICA, font_size=11, color=self.accent_color, weight=BOLD).move_to(router_diamond)
        router_node = VGroup(router_diamond, router_txt)

        in_arrow = Arrow(start=in_box.get_bottom(), end=router_diamond.get_top(), color=COLOR_WHITE, buff=0.1, stroke_width=4.0)

        # 3. Branch A (Left)
        branch_a_box = RoundedRectangle(corner_radius=0.14, width=3.3, height=2.2, color=branch_a_color, fill_color=COLOR_PANEL_BG, fill_opacity=0.95, stroke_width=3.0).move_to([-1.9, -1.2, 0])
        a_title = CleanText(trim_words(branch_a_label, 22).upper(), font=FONT_HELVETICA, font_size=12, color=branch_a_color, weight=BOLD).move_to(branch_a_box.get_top() + DOWN * 0.4)
        a_sub = CleanText(trim_words(branch_a_sub, 28), font=FONT_HELVETICA, font_size=10, color=COLOR_SLATE).next_to(a_title, DOWN, buff=0.15) if str(branch_a_sub).strip() else VGroup()
        # Visual wave / grid inside branch A
        a_sample_axes = Axes(x_range=[0, 3, 1], y_range=[-1, 1, 1], x_length=2.5, y_length=0.7, axis_config={"color": branch_a_color, "stroke_width": 1.0}).move_to(branch_a_box.get_bottom() + UP * 0.55)
        a_wave = a_sample_axes.plot(lambda x: np.sin(2 * PI * x), color=branch_a_color, stroke_width=3.5)
        branch_a_group = VGroup(branch_a_box, a_title, a_sub, a_sample_axes, a_wave)

        # 4. Branch B (Right)
        branch_b_box = RoundedRectangle(corner_radius=0.14, width=3.3, height=2.2, color=branch_b_color, fill_color=COLOR_PANEL_BG, fill_opacity=0.95, stroke_width=3.0).move_to([1.9, -1.2, 0])
        b_title = CleanText(trim_words(branch_b_label, 22).upper(), font=FONT_HELVETICA, font_size=12, color=branch_b_color, weight=BOLD).move_to(branch_b_box.get_top() + DOWN * 0.4)
        b_sub = CleanText(trim_words(branch_b_sub, 28), font=FONT_HELVETICA, font_size=10, color=COLOR_SLATE).next_to(b_title, DOWN, buff=0.15) if str(branch_b_sub).strip() else VGroup()
        # Visual discrete steps inside branch B
        b_steps = VGroup(*[
            Rectangle(width=0.6, height=0.25 + 0.18 * i, color=branch_b_color, fill_color=branch_b_color, fill_opacity=0.8, stroke_width=1.5).move_to(branch_b_box.get_bottom() + UP * (0.35 + 0.1 * i) + LEFT * (0.8 - 0.7 * i))
            for i in range(3)
        ])
        branch_b_group = VGroup(branch_b_box, b_title, b_sub, b_steps)

        # Diverging connecting arrows
        arrow_a = CurvedArrow(router_diamond.get_left() + DOWN * 0.1, branch_a_box.get_top(), radius=2.5, color=branch_a_color, stroke_width=4.0)
        arrow_b = CurvedArrow(router_diamond.get_right() + DOWN * 0.1, branch_b_box.get_top(), radius=-2.5, color=branch_b_color, stroke_width=4.0)

        self.in_node = in_node
        self.router_node = router_node
        self.branch_a_group = branch_a_group
        self.branch_b_group = branch_b_group
        self.in_arrow = in_arrow
        self.arrow_a = arrow_a
        self.arrow_b = arrow_b
        self.focus_target = router_node

        self.content_group.add(in_node, in_arrow, router_node, arrow_a, arrow_b, branch_a_group, branch_b_group)
        self.kinetic_elements.add(router_node, arrow_a, arrow_b)
        self.add(self.title, self.sub, self.content_group)

    def get_build_steps(self):
        """Input -> router -> branch A -> branch B, each revealed as the narration reaches it."""
        return [
            [self.in_node],
            [self.in_arrow, self.router_node],
            [self.arrow_a, self.branch_a_group],
            [self.arrow_b, self.branch_b_group],
        ]


class BlueprintPipelineStages(BaseBlueprintComposition):
    """
    Sequential multi-stage pipeline: 3 interconnected vertical stages.
    Perfect for: Step-by-step transformations, token ingestion -> processing -> synthesis.
    """
    def __init__(
        self,
        stage_1_label: str = "INPUT",
        stage_1_sub: str = "",
        stage_2_label: str = "PROCESS",
        stage_2_sub: str = "",
        stage_3_label: str = "OUTPUT",
        stage_3_sub: str = "",
        accent_color: str = COLOR_CYAN,
        **kwargs
    ):
        super().__init__(accent_color=accent_color, **kwargs)

        stages_data = [
            (stage_1_label, stage_1_sub, COLOR_SLATE, 2.5),
            (stage_2_label, stage_2_sub, accent_color, 0.4),
            (stage_3_label, stage_3_sub, COLOR_MINT, -1.7),
        ]

        stage_groups = []
        for idx, (lbl, sub_lbl, col, y_pos) in enumerate(stages_data):
            box = RoundedRectangle(
                corner_radius=0.16,
                width=6.6,
                height=1.45,
                color=col,
                fill_color=COLOR_PANEL_BG,
                fill_opacity=0.92,
                stroke_width=2.5
            ).move_to([0, y_pos, 0])

            badge = RoundedRectangle(
                corner_radius=0.08,
                width=1.2,
                height=0.4,
                color=col,
                fill_color=col,
                fill_opacity=0.25,
                stroke_width=1.5
            ).move_to(box.get_left() + RIGHT * 0.9)
            badge_txt = CleanText(f"STEP {idx+1}", font=FONT_HELVETICA, font_size=10, color=col, weight=BOLD).move_to(badge)

            t = CleanText(trim_words(lbl, 26).upper(), font=FONT_HELVETICA, font_size=13, color=col, weight=BOLD).next_to(badge, RIGHT, buff=0.3)
            if str(sub_lbl).strip():
                s = CleanText(trim_words(sub_lbl, 45), font=FONT_HELVETICA, font_size=10, color=COLOR_SLATE).next_to(t, DOWN, buff=0.1, aligned_edge=LEFT)
            else:
                t.move_to([t.get_center()[0], box.get_center()[1], 0])
                s = VGroup()

            grp = VGroup(box, badge, badge_txt, t, s)
            stage_groups.append(grp)
            self.content_group.add(grp)

        # Connecting vertical arrows
        arrow_1 = Arrow(start=stage_groups[0].get_bottom(), end=stage_groups[1].get_top(), color=COLOR_WHITE, buff=0.1, stroke_width=4.0)
        arrow_2 = Arrow(start=stage_groups[1].get_bottom(), end=stage_groups[2].get_top(), color=COLOR_MINT, buff=0.1, stroke_width=4.0)

        self.stage_groups = stage_groups
        self.stage_1_group = stage_groups[0] if len(stage_groups) > 0 else None
        self.stage_2_group = stage_groups[1] if len(stage_groups) > 1 else None
        self.stage_3_group = stage_groups[2] if len(stage_groups) > 2 else None

        self.arrow_1 = arrow_1
        self.arrow_2 = arrow_2
        self.focus_target = stage_groups[1]

        self.content_group.add(arrow_1, arrow_2)
        self.kinetic_elements.add(stage_groups[1], arrow_1, arrow_2)
        self.add(self.title, self.sub, self.content_group)

    def get_build_steps(self):
        """Stage 1 -> arrow + stage 2 -> arrow + stage 3."""
        return [
            [self.stage_groups[0]],
            [self.arrow_1, self.stage_groups[1]],
            [self.arrow_2, self.stage_groups[2]],
        ]

    def get_kinetic_animation(self, run_time: float = 1.5) -> Animation:
        """Sequential packet flow across pipeline stages with glowing flash highlights."""
        anim1 = self.arrow_1.animate(rate_func=there_and_back, run_time=run_time * 0.45).set_stroke(color=COLOR_CYAN, width=6.0)
        anim2 = self.stage_2_group.animate(rate_func=there_and_back, run_time=run_time * 0.5).scale(1.03)
        anim3 = self.arrow_2.animate(rate_func=there_and_back, run_time=run_time * 0.45).set_stroke(color=COLOR_MINT, width=6.0)
        return AnimationGroup(anim1, anim2, anim3, lag_ratio=0.3)


class BlueprintGridMemory(BaseBlueprintComposition):
    """
    2D / 3D spatial coordinate memory: Structured grid of memory cells / voxels.
    Perfect for: Spatial memory (LOCI), KV-cache buffers, coordinate retrieval.
    """
    def __init__(
        self,
        grid_title: str = "SPATIAL MEMORY MATRIX",
        active_cell_label: str = "QUERY HIT: (x, y, θ)",
        efficiency_label: str = "O(1) CONSTANT LATENCY",
        accent_color: str = COLOR_CYAN,
        **kwargs
    ):
        super().__init__(accent_color=accent_color, **kwargs)

        # Grid container chassis
        chassis = RoundedRectangle(
            corner_radius=0.16,
            width=6.8,
            height=4.8,
            color=COLOR_DARK_SLATE,
            fill_color=COLOR_PANEL_BG,
            fill_opacity=0.92,
            stroke_width=2.0
        ).move_to([0, 0.4, 0])

        header = CleanText(trim_words(grid_title, 28).upper(), font=FONT_HELVETICA, font_size=12, color=accent_color, weight=BOLD).move_to(chassis.get_top() + DOWN * 0.4)

        # 4x4 coordinate cell matrix
        cells = VGroup()
        rows, cols = 4, 4
        cell_w, cell_h = 1.25, 0.62
        start_x = -1.9
        start_y = 1.55

        hit_cell = None
        for r in range(rows):
            for c in range(cols):
                cx = start_x + c * (cell_w + 0.15)
                cy = start_y - r * (cell_h + 0.14)
                is_hit = (r == 1 and c == 2)
                is_active = (r in [0, 1] and c in [1, 2, 3])

                color = COLOR_MINT if is_hit else (accent_color if is_active else COLOR_DARK_SLATE)
                fill_op = 0.85 if is_hit else (0.35 if is_active else 0.1)

                rect = Rectangle(width=cell_w, height=cell_h, color=color, fill_color=color, fill_opacity=fill_op, stroke_width=2.0).move_to([cx, cy, 0])
                coord_txt = CleanText(f"[{r},{c}]", font=FONT_HELVETICA, font_size=8, color=COLOR_WHITE if is_hit else COLOR_SLATE).move_to(rect)
                cell_item = VGroup(rect, coord_txt)
                cells.add(cell_item)
                if is_hit:
                    hit_cell = cell_item

        # Bottom query hit badge cleanly separated below row 4
        hit_badge = RoundedRectangle(corner_radius=0.1, width=3.3, height=0.5, color=COLOR_MINT, fill_color="#064E3B", fill_opacity=0.9, stroke_width=1.8).move_to([-1.65, chassis.get_bottom()[1] + 0.45, 0])
        hit_txt = CleanText(trim_words(active_cell_label, 24), font=FONT_HELVETICA, font_size=9, color=COLOR_MINT, weight=BOLD).move_to(hit_badge)

        eff_badge = RoundedRectangle(corner_radius=0.1, width=3.1, height=0.5, color=COLOR_AMBER, fill_color="#451A03", fill_opacity=0.9, stroke_width=1.8).move_to([1.65, chassis.get_bottom()[1] + 0.45, 0])
        eff_txt = CleanText(trim_words(efficiency_label, 20), font=FONT_HELVETICA, font_size=9, color=COLOR_AMBER, weight=BOLD).move_to(eff_badge)

        badge_group = VGroup(hit_badge, hit_txt, eff_badge, eff_txt)

        self.cells = cells
        self.hit_cell = hit_cell
        self.active_cell = hit_cell
        self.badge_group = badge_group
        self.chassis = chassis
        self.grid_header = header
        self.focus_target = hit_cell

        self.content_group.add(chassis, header, cells, badge_group)
        self.kinetic_elements.add(hit_cell, badge_group)
        self.add(self.title, self.sub, self.content_group)

    def get_build_steps(self):
        """Empty memory -> cells fill row by row -> hit / efficiency badges."""
        return [
            [self.chassis, self.grid_header],
            {"mobjects": [self.cells],
             "animate": lambda rt: LaggedStart(*[FadeIn(c, scale=0.85) for c in self.cells], lag_ratio=0.06, run_time=rt)},
            [self.badge_group],
        ]

    def get_kinetic_animation(self, run_time: float = 1.5) -> Animation:
        """Matrix cell laser flash and query hit activation."""
        if self.hit_cell:
            hit_rect = self.hit_cell[0]
            anim1 = hit_rect.animate(rate_func=there_and_back, run_time=run_time * 0.5).set_fill(color=COLOR_MINT, opacity=1.0).set_stroke(color=COLOR_WHITE, width=4.0)
            anim2 = self.badge_group.animate(rate_func=there_and_back, run_time=run_time * 0.5).scale(1.04)
            return AnimationGroup(anim1, anim2, lag_ratio=0.2)
        return super().get_kinetic_animation(run_time=run_time)


class BlueprintProjectionRays(BaseBlueprintComposition):
    """
    Projective geometry: Camera/Observer casting rays onto 3D feature points/plane.
    Perfect for: World models, camera math, spatial mapping, view synthesis.
    """
    def __init__(
        self,
        camera_label: str = "OBSERVER CAMERA POSE",
        focal_plane_label: str = "PERSPECTIVE PROJECTION PLANE",
        target_label: str = "SPATIAL FEATURE ANCHOR",
        accent_color: str = COLOR_CYAN,
        **kwargs
    ):
        super().__init__(accent_color=accent_color, **kwargs)

        # 1. Top Camera Icon
        cam_body = RoundedRectangle(corner_radius=0.1, width=2.4, height=0.9, color=COLOR_WHITE, fill_color=COLOR_PANEL_BG, fill_opacity=0.95, stroke_width=2.5).move_to([0, 3.2, 0])
        cam_lens = Polygon([0.4, 2.9, 0], [0.9, 2.5, 0], [-0.9, 2.5, 0], [-0.4, 2.9, 0], color=COLOR_WHITE, fill_color=COLOR_WHITE, fill_opacity=0.3, stroke_width=2.0)
        cam_txt = CleanText(trim_words(camera_label, 20).upper(), font=FONT_HELVETICA, font_size=10, color=COLOR_WHITE, weight=BOLD).move_to(cam_body)
        cam_group = VGroup(cam_body, cam_lens, cam_txt)

        # 2. Middle Focal Plane (Tilted perspective rectangle)
        focal_plane = Polygon(
            [-2.8, 1.0, 0], [2.8, 1.0, 0], [2.2, 0.2, 0], [-2.2, 0.2, 0],
            color=accent_color, fill_color=accent_color, fill_opacity=0.2, stroke_width=2.5
        )
        focal_txt = CleanText(trim_words(focal_plane_label, 30).upper(), font=FONT_HELVETICA, font_size=9, color=accent_color, weight=BOLD).move_to(focal_plane)
        plane_group = VGroup(focal_plane, focal_txt)

        # 3. Ray lines projecting from lens through focal plane to ground points
        ray_left = Line(start=[0, 2.5, 0], end=[-2.0, -1.8, 0], color=COLOR_MINT, stroke_width=3.5)
        ray_center = Line(start=[0, 2.5, 0], end=[0, -2.0, 0], color=COLOR_CYAN, stroke_width=4.0)
        ray_right = Line(start=[0, 2.5, 0], end=[2.0, -1.8, 0], color=COLOR_AMBER, stroke_width=3.5)
        rays_group = VGroup(ray_left, ray_center, ray_right)

        # 4. Target Spatial Anchors (Ground feature points)
        pt_left = Dot(point=[-2.0, -1.8, 0], radius=0.18, color=COLOR_MINT)
        pt_center = Dot(point=[0, -2.0, 0], radius=0.22, color=COLOR_CYAN)
        pt_right = Dot(point=[2.0, -1.8, 0], radius=0.18, color=COLOR_AMBER)

        target_banner = RoundedRectangle(corner_radius=0.12, width=5.8, height=0.65, color=COLOR_CYAN, fill_color="#0F172A", fill_opacity=0.92, stroke_width=2.0).move_to([0, -2.7, 0])
        target_txt = CleanText(trim_words(target_label, 32).upper(), font=FONT_HELVETICA, font_size=11, color=COLOR_CYAN, weight=BOLD).move_to(target_banner)
        target_group = VGroup(pt_left, pt_center, pt_right, target_banner, target_txt)

        self.cam_group = cam_group
        self.plane_group = plane_group
        self.rays_group = rays_group
        self.target_group = target_group
        self.focus_target = pt_center

        self.content_group.add(cam_group, plane_group, rays_group, target_group)
        self.kinetic_elements.add(rays_group, pt_center)
        self.add(self.title, self.sub, self.content_group)

    def get_build_steps(self):
        """Camera -> rays cast -> projection plane -> landing points."""
        return [
            [self.cam_group],
            {"mobjects": [self.rays_group],
             "animate": lambda rt: LaggedStart(*[Create(r) for r in self.rays_group], lag_ratio=0.25, run_time=rt)},
            [self.plane_group],
            [self.target_group],
        ]

    def get_focus_animation(self, run_time: float = 1.0):
        flashes = [ShowPassingFlash(r.copy().set_stroke(color=YELLOW, width=7), time_width=0.5) for r in self.rays_group]
        return AnimationGroup(
            AnimationGroup(*flashes),
            Circumscribe(self.target_group, color=self.accent_color, time_width=0.6),
            run_time=run_time,
        )


class BlueprintBarrierSeparation(BaseBlueprintComposition):
    """
    Orthogonal anti-bleed barrier: Two flowing conduits separated by an active wall/barrier.
    Perfect for: Preventing cross-talk, orthogonal penalties, isolating representations.
    """
    def __init__(
        self,
        stream_a_label: str = "SEMANTIC LATENT CONDUIT",
        stream_b_label: str = "PIXEL DEPTH CONDUIT",
        barrier_label: str = "ORTHOGONAL PENALTY BARRIER",
        barrier_sub: str = "Strict zero cross-talk constraint",
        **kwargs
    ):
        super().__init__(**kwargs)

        # Left Conduit (Stream A)
        tube_a = RoundedRectangle(corner_radius=0.16, width=2.6, height=5.2, color=COLOR_CYAN, fill_color=COLOR_PANEL_BG, fill_opacity=0.92, stroke_width=2.5).move_to([-2.1, 0.4, 0])
        lbl_a = CleanText(trim_words(stream_a_label, 20).upper(), font=FONT_HELVETICA, font_size=10, color=COLOR_CYAN, weight=BOLD).move_to(tube_a.get_top() + DOWN * 0.4)
        arrows_a = VGroup(*[
            Arrow(start=[-2.1, 1.6 - 1.2 * i, 0], end=[-2.1, 0.8 - 1.2 * i, 0], color=COLOR_CYAN, stroke_width=3.5, buff=0)
            for i in range(3)
        ])
        group_a = VGroup(tube_a, lbl_a, arrows_a)

        # Right Conduit (Stream B)
        tube_b = RoundedRectangle(corner_radius=0.16, width=2.6, height=5.2, color=COLOR_AMBER, fill_color=COLOR_PANEL_BG, fill_opacity=0.92, stroke_width=2.5).move_to([2.1, 0.4, 0])
        lbl_b = CleanText(trim_words(stream_b_label, 20).upper(), font=FONT_HELVETICA, font_size=10, color=COLOR_AMBER, weight=BOLD).move_to(tube_b.get_top() + DOWN * 0.4)
        arrows_b = VGroup(*[
            Arrow(start=[2.1, 1.6 - 1.2 * i, 0], end=[2.1, 0.8 - 1.2 * i, 0], color=COLOR_AMBER, stroke_width=3.5, buff=0)
            for i in range(3)
        ])
        group_b = VGroup(tube_b, lbl_b, arrows_b)

        # Central Glowing Wall Barrier
        barrier_wall = Rectangle(width=0.45, height=5.4, color=COLOR_CORAL, fill_color=COLOR_CORAL, fill_opacity=0.85, stroke_width=3.0).move_to([0, 0.4, 0])
        # Energy hatch lines
        hatches = VGroup(*[
            Line(start=[-0.3, -2.0 + 0.6 * i, 0], end=[0.3, -1.8 + 0.6 * i, 0], color=COLOR_WHITE, stroke_width=2.0)
            for i in range(8)
        ])
        barrier_badge = RoundedRectangle(corner_radius=0.1, width=4.6, height=0.6, color=COLOR_CORAL, fill_color="#450A0A", fill_opacity=0.95, stroke_width=2.0).move_to([0, -1.6, 0])
        barrier_txt = CleanText(trim_words(barrier_label, 26).upper(), font=FONT_HELVETICA, font_size=10, color=COLOR_CORAL, weight=BOLD).move_to(barrier_badge)
        barrier_group = VGroup(barrier_wall, hatches, barrier_badge, barrier_txt)

        self.group_a = group_a
        self.group_b = group_b
        self.barrier_group = barrier_group
        self.arrows_a = arrows_a
        self.arrows_b = arrows_b
        self.focus_target = barrier_group

        self.content_group.add(group_a, group_b, barrier_group)
        self.kinetic_elements.add(barrier_group)
        self.add(self.title, self.sub, self.content_group)

    def get_build_steps(self):
        """Stream A -> stream B -> the barrier slams down between them."""
        return [
            [self.group_a],
            [self.group_b],
            {"mobjects": [self.barrier_group],
             "animate": lambda rt: AnimationGroup(
                 GrowFromEdge(self.barrier_group[0], UP), FadeIn(self.barrier_group[1:]), run_time=rt)},
        ]

    def get_focus_animation(self, run_time: float = 1.0):
        flows = [ShowPassingFlash(a.copy().set_stroke(color=YELLOW, width=7), time_width=0.6)
                 for a in list(self.arrows_a) + list(self.arrows_b)]
        return AnimationGroup(
            LaggedStart(*flows, lag_ratio=0.1),
            Circumscribe(self.barrier_group, color=COLOR_CORAL, time_width=0.6),
            run_time=run_time,
        )


class BlueprintTreeHierarchy(BaseBlueprintComposition):
    """
    Branching search / decision hierarchy: Root node expanding into search branches.
    Perfect for: Reasoning models, MCTS, decision logic, pruning dead ends.
    """
    def __init__(
        self,
        root_label: str = "DECISION QUERY",
        optimal_label: str = "HIGH-CONFIDENCE PATH",
        pruned_label: str = "PRUNED BRANCH",
        left_node_label: str = "DEAD END",
        right_node_label: str = "EXPLORE",
        leaf_label: str = "PRUNE",
        optimal_sub: str = "",
        accent_color: str = COLOR_MINT,
        **kwargs
    ):
        super().__init__(accent_color=accent_color, **kwargs)

        # Root Node
        root_box = RoundedRectangle(corner_radius=0.12, width=3.8, height=0.85, color=COLOR_WHITE, fill_color=COLOR_PANEL_BG, fill_opacity=0.95, stroke_width=2.5).move_to([0, 3.2, 0])
        root_txt = CleanText(trim_words(root_label, 22).upper(), font=FONT_HELVETICA, font_size=11, color=COLOR_WHITE, weight=BOLD).move_to(root_box)
        root_grp = VGroup(root_box, root_txt)

        # Level 1 Nodes
        node_left = Circle(radius=0.55, color=COLOR_CORAL, fill_color="#450A0A", fill_opacity=0.8, stroke_width=2.5).move_to([-2.1, 1.4, 0])
        txt_l = CleanText(trim_words(left_node_label, 10).upper(), font=FONT_HELVETICA, font_size=9, color=COLOR_CORAL, weight=BOLD, max_width=0.95).move_to(node_left)
        edge_l = Line(start=root_box.get_bottom(), end=node_left.get_top(), color=COLOR_CORAL, stroke_width=2.5)

        node_right = Circle(radius=0.6, color=accent_color, fill_color="#064E3B", fill_opacity=0.9, stroke_width=3.5).move_to([2.1, 1.4, 0])
        txt_r = CleanText(trim_words(right_node_label, 10).upper(), font=FONT_HELVETICA, font_size=9, color=accent_color, weight=BOLD, max_width=1.05).move_to(node_right)
        edge_r = Line(start=root_box.get_bottom(), end=node_right.get_top(), color=accent_color, stroke_width=4.0)

        # Level 2 Nodes (from right node)
        leaf_1 = Circle(radius=0.45, color=COLOR_SLATE, fill_color="#1E293B", fill_opacity=0.8, stroke_width=2.0).move_to([0.6, -0.6, 0])
        txt_leaf_1 = CleanText(trim_words(leaf_label, 8).upper(), font=FONT_HELVETICA, font_size=8, color=COLOR_SLATE, weight=BOLD, max_width=0.8).move_to(leaf_1)
        edge_leaf_1 = Line(start=node_right.get_bottom(), end=leaf_1.get_top(), color=COLOR_SLATE, stroke_width=2.0)

        leaf_2 = RoundedRectangle(corner_radius=0.12, width=3.4, height=1.1, color=accent_color, fill_color="#064E3B", fill_opacity=0.95, stroke_width=3.0).move_to([2.2, -1.8, 0])
        leaf_2_t = CleanText(trim_words(optimal_label, 20).upper(), font=FONT_HELVETICA, font_size=10, color=accent_color, weight=BOLD).move_to(leaf_2.get_top() + DOWN * 0.35)
        edge_leaf_2 = Arrow(start=node_right.get_bottom() + RIGHT * 0.2, end=leaf_2.get_top(), color=accent_color, stroke_width=4.5, buff=0.1)
        if optimal_sub:
            # No hard-coded stats: the old "Optimal 99.4% Choice" appeared in every video.
            leaf_2_s = CleanText(trim_words(optimal_sub, 26), font=FONT_HELVETICA, font_size=9, color=COLOR_WHITE).next_to(leaf_2_t, DOWN, buff=0.1)
            leaf_grp = VGroup(leaf_2, leaf_2_t, leaf_2_s)
        else:
            leaf_2_t.move_to(leaf_2)
            leaf_grp = VGroup(leaf_2, leaf_2_t)

        # Pruned badge on left
        pruned_box = RoundedRectangle(corner_radius=0.1, width=2.4, height=0.5, color=COLOR_CORAL, fill_color="#450A0A", fill_opacity=0.9, stroke_width=1.5).next_to(node_left, DOWN, buff=0.4)
        pruned_txt = CleanText(trim_words(pruned_label, 16).upper(), font=FONT_HELVETICA, font_size=8, color=COLOR_CORAL, weight=BOLD).move_to(pruned_box)

        self.root_node = root_grp
        self.optimal_group = leaf_grp
        self.pruned_group = VGroup(node_left, txt_l, edge_l, pruned_box, pruned_txt)
        self.focus_target = leaf_grp
        self._tree_parts = dict(
            root=root_grp, edge_l=edge_l, node_l=VGroup(node_left, txt_l), edge_r=edge_r,
            node_r=VGroup(node_right, txt_r), pruned=VGroup(pruned_box, pruned_txt),
            edge_leaf_1=edge_leaf_1, leaf_1=VGroup(leaf_1, txt_leaf_1), edge_leaf_2=edge_leaf_2, leaf=leaf_grp,
        )

        self.content_group.add(root_grp, edge_l, node_left, txt_l, pruned_box, pruned_txt, edge_r, node_right, txt_r, edge_leaf_1, leaf_1, txt_leaf_1, edge_leaf_2, leaf_grp)
        self.kinetic_elements.add(leaf_grp, edge_leaf_2)
        self.add(self.title, self.sub, self.content_group)

    def get_build_steps(self):
        """Root -> two branches -> dead ends get pruned -> winning path."""
        p = self._tree_parts
        return [
            [p["root"]],
            [p["edge_l"], p["node_l"], p["edge_r"], p["node_r"]],
            [p["edge_leaf_1"], p["leaf_1"], p["pruned"]],
            [p["edge_leaf_2"], p["leaf"]],
        ]

    def get_focus_animation(self, run_time: float = 1.0):
        p = self._tree_parts
        path = [p["edge_r"], p["edge_leaf_2"]]
        flashes = [ShowPassingFlash(e.copy().set_stroke(color=YELLOW, width=7), time_width=0.6) for e in path]
        return AnimationGroup(
            Succession(*flashes),
            p["pruned"].animate.set_opacity(0.35),
            Circumscribe(p["leaf"], color=self.accent_color, time_width=0.6),
            run_time=run_time,
        )


class BlueprintLayerStack(BaseBlueprintComposition):
    """
    Stacked 2.5D Isometric Layers: Authentic axonometric projection showing
    hierarchical abstraction levels building to output.
    """
    def __init__(
        self,
        bottom_layer: str = "RAW TOKEN EMBEDDINGS",
        mid_layer: str = "CONTEXTUAL ROUTING SCORES",
        top_layer: str = "SYNTHESIZED DECISION",
        accent_color: str = COLOR_CYAN,
        **kwargs
    ):
        super().__init__(accent_color=accent_color, **kwargs)

        layers_data = [
            (bottom_layer, COLOR_SLATE, -0.2),
            (mid_layer, accent_color, 0.0),
            (top_layer, COLOR_MINT, 0.2),
        ]

        stack_grp, proj_rays = create_isometric_layer_stack(
            layers_data=layers_data,
            width=5.2,
            height=1.8,
            thickness=0.3,
            spacing=1.75,
            base_y=-1.8
        )

        self.stack_group = stack_grp
        self.proj_rays = proj_rays
        self.layer_groups = [stack_grp[i] for i in range(len(stack_grp))]
        self.focus_target = stack_grp[-1]

        self.content_group.add(stack_grp, proj_rays)
        self.kinetic_elements.add(stack_grp[-1], proj_rays)
        self.add(self.title, self.sub, self.content_group)

    def get_build_steps(self):
        """Layers stack up from the bottom; projection rays connect them with the top layer."""
        steps = [[layer] for layer in self.layer_groups]
        if steps:
            steps[-1] = [self.proj_rays] + steps[-1]
        return steps

    def get_focus_animation(self, run_time: float = 1.0):
        flashes = [ShowPassingFlash(r.copy().set_stroke(color=YELLOW, width=6), time_width=0.6) for r in self.proj_rays]
        return AnimationGroup(
            LaggedStart(*flashes, lag_ratio=0.15),
            Circumscribe(self.stack_group[-1], color=self.accent_color, time_width=0.6),
            run_time=run_time,
        )

    def get_kinetic_animation(self, run_time: float = 1.5) -> Animation:
        """Ascending vertical projection beam kinetics into top synthesized tier."""
        ray_flash = self.proj_rays.animate(rate_func=there_and_back, run_time=run_time * 0.5).set_stroke(color=COLOR_WHITE, width=3.5, opacity=1.0)
        top_pulse = self.stack_group[-1].animate(rate_func=there_and_back, run_time=run_time * 0.6).scale(1.04)
        return AnimationGroup(ray_flash, top_pulse, lag_ratio=0.3)


class BlueprintConvergenceFunnel(BaseBlueprintComposition):
    """
    Multi-input aggregation: Multiple diverse inputs funneled into a single core.
    Perfect for: Multimodal fusion, combining sensory inputs, bottleneck compression.
    """
    def __init__(
        self,
        input_1_label: str = "TEXT STREAM",
        input_2_label: str = "VISION TOKENS",
        input_3_label: str = "AUDIO SIGNALS",
        fused_label: str = "UNIFIED MULTIMODAL CORE",
        fused_sub: str = "",
        accent_color: str = COLOR_CYAN,
        **kwargs
    ):
        super().__init__(accent_color=accent_color, **kwargs)

        inputs = [
            (input_1_label, COLOR_CYAN, -2.4),
            (input_2_label, COLOR_MINT, 0.0),
            (input_3_label, COLOR_AMBER, 2.4),
        ]

        in_nodes = []
        in_arrows = []
        fused_pos = [0, -1.6, 0]

        for lbl, col, x_pos in inputs:
            box = RoundedRectangle(corner_radius=0.1, width=2.1, height=0.8, color=col, fill_color=COLOR_PANEL_BG, fill_opacity=0.95, stroke_width=2.0).move_to([x_pos, 2.8, 0])
            txt = CleanText(trim_words(lbl, 16).upper(), font=FONT_HELVETICA, font_size=9, color=col, weight=BOLD).move_to(box)
            node = VGroup(box, txt)
            in_nodes.append(node)
            self.content_group.add(node)

            arr = Arrow(start=box.get_bottom(), end=fused_pos + UP * 0.9, color=col, stroke_width=3.5, buff=0.1)
            in_arrows.append(arr)
            self.content_group.add(arr)

        # Fused Core
        fused_box = RoundedRectangle(corner_radius=0.16, width=6.2, height=1.6, color=accent_color, fill_color="#0F172A", fill_opacity=0.95, stroke_width=3.5).move_to(fused_pos)
        fused_t = CleanText(trim_words(fused_label, 28).upper(), font=FONT_HELVETICA, font_size=13, color=accent_color, weight=BOLD).move_to(fused_box.get_top() + DOWN * 0.45)
        if fused_sub:
            fused_s = CleanText(trim_words(fused_sub, 36), font=FONT_HELVETICA, font_size=10, color=COLOR_WHITE).next_to(fused_t, DOWN, buff=0.15)
            fused_group = VGroup(fused_box, fused_t, fused_s)
        else:
            fused_t.move_to(fused_box)
            fused_group = VGroup(fused_box, fused_t)

        self.in_nodes = in_nodes
        self.in_arrows = in_arrows
        self.fused_group = fused_group
        self.focus_target = fused_group

        self.content_group.add(fused_group)
        self.kinetic_elements.add(fused_group)
        self.add(self.title, self.sub, self.content_group)

    def get_build_steps(self):
        """Each input appears as it is named; then all arrows converge into the fused core."""
        steps = [[n] for n in self.in_nodes]
        steps.append(list(self.in_arrows) + [self.fused_group])
        return steps


class BlueprintCatalogRouting(BaseBlueprintComposition):
    """
    Central card catalog / index dispatch: Fast index router dispatching queries.
    Perfect for: Jev index routing, library card catalog analogies, token dispatching.
    """
    def __init__(
        self,
        index_label: str = "CENTRAL INDEX DESK",
        drawer_a_label: str = "DOMAIN EXPERT A",
        drawer_b_label: str = "DOMAIN EXPERT B",
        drawer_c_label: str = "DOMAIN EXPERT C",
        index_sub: str = "",
        accent_color: str = COLOR_CYAN,
        **kwargs
    ):
        super().__init__(accent_color=accent_color, **kwargs)

        # Top Central Index Desk
        index_box = RoundedRectangle(corner_radius=0.14, width=5.8, height=1.2, color=COLOR_WHITE, fill_color=COLOR_PANEL_BG, fill_opacity=0.95, stroke_width=2.5).move_to([0, 2.8, 0])
        index_t = CleanText(trim_words(index_label, 24).upper(), font=FONT_HELVETICA, font_size=12, color=COLOR_WHITE, weight=BOLD).move_to(index_box.get_top() + DOWN * 0.35)
        if index_sub:
            index_s = CleanText(trim_words(index_sub, 34), font=FONT_HELVETICA, font_size=9, color=COLOR_SLATE).next_to(index_t, DOWN, buff=0.1)
            index_group = VGroup(index_box, index_t, index_s)
        else:
            index_t.move_to(index_box)
            index_group = VGroup(index_box, index_t)

        # 3 Destination Drawers / Buckets
        drawers_data = [
            (drawer_a_label, COLOR_CYAN, -2.2),
            (drawer_b_label, COLOR_MINT, 0.0),
            (drawer_c_label, COLOR_AMBER, 2.2),
        ]

        drawers = []
        arrows = []
        for lbl, col, x_pos in drawers_data:
            d_box = RoundedRectangle(corner_radius=0.12, width=2.1, height=2.4, color=col, fill_color=COLOR_PANEL_BG, fill_opacity=0.92, stroke_width=2.5).move_to([x_pos, -1.0, 0])
            d_t = CleanText(trim_words(lbl, 16).upper(), font=FONT_HELVETICA, font_size=9, color=col, weight=BOLD).move_to(d_box.get_top() + DOWN * 0.35)

            # Slot lines inside drawer
            slots = VGroup(*[
                Line(start=[x_pos - 0.7, -0.3 - 0.4 * i, 0], end=[x_pos + 0.7, -0.3 - 0.4 * i, 0], color=col, stroke_width=1.5)
                for i in range(3)
            ])
            d_grp = VGroup(d_box, d_t, slots)
            drawers.append(d_grp)
            self.content_group.add(d_grp)

            arr = Arrow(start=index_box.get_bottom(), end=d_box.get_top(), color=col, stroke_width=3.5, buff=0.1)
            arrows.append(arr)
            self.content_group.add(arr)

        self.content_group.add(index_group)
        self.kinetic_elements.add(drawers[1], arrows[1])  # Middle drawer active
        self.index_group = index_group
        self.drawers = drawers
        self.drawer_arrows = arrows
        self.focus_target = drawers[1]
        self.add(self.title, self.sub, self.content_group)

    def get_build_steps(self):
        """Index first, then each destination as the narration routes to it."""
        return [[self.index_group]] + [[a, d] for a, d in zip(self.drawer_arrows, self.drawers)]

    def get_focus_animation(self, run_time: float = 1.0):
        arrow = self.drawer_arrows[1]
        return AnimationGroup(
            ShowPassingFlash(arrow.copy().set_stroke(color=YELLOW, width=7), time_width=0.6),
            Circumscribe(self.drawers[1], color=self.accent_color, time_width=0.6),
            run_time=run_time,
        )


class BlueprintSideBySideComparison(BaseBlueprintComposition):
    """
    Direct dual-column contrast: two approaches compared side by side.

    Only shows what the script provides (titles, tags, up to 3 spec lines, optional stat
    pill, optional load bar when a real ratio is given). The previous version always drew
    BitNet-specific FP16 vs ternary matrices and "100% / 10%" load bars, which appeared in
    every comparison regardless of the paper.
    """
    def __init__(
        self,
        col_a_title: str = "BASELINE",
        col_a_stat: str = "",
        col_a_tag: str = "BEFORE",
        col_a_metric_lbl: str = "",
        col_a_ratio: Optional[float] = None,
        col_b_title: str = "PROPOSED",
        col_b_stat: str = "",
        col_b_tag: str = "AFTER",
        col_b_metric_lbl: str = "",
        col_b_ratio: Optional[float] = None,
        col_a_specs: Optional[List[str]] = None,
        col_b_specs: Optional[List[str]] = None,
        accent_color: str = COLOR_MINT,
        **kwargs
    ):
        super().__init__(accent_color=accent_color, **kwargs)

        def _column(x, title, tag, stat, specs, ratio, metric_lbl, edge_col, title_col, fill_col, dot_col):
            box = RoundedRectangle(corner_radius=0.16, width=3.5, height=4.8, color=edge_col,
                                   fill_color=fill_col, fill_opacity=0.92, stroke_width=2.5).move_to([x, 0.6, 0])
            parts = VGroup(box)
            tag_m = CleanText(trim_words(str(tag).upper(), 18), font=FONT_HELVETICA, font_size=11, color=COLOR_SLATE,
                              weight=BOLD, max_width=3.0).move_to(box.get_top() + DOWN * 0.38)
            title_m = CleanText(trim_words(str(title).upper(), 24), font=FONT_HELVETICA, font_size=15, color=title_col,
                                weight=BOLD, max_width=3.1).next_to(tag_m, DOWN, buff=0.16)
            parts.add(tag_m, title_m)
            y = title_m.get_bottom()[1] - 0.45
            spec_rows = VGroup()
            for spec_text in (specs or [])[:3]:
                if not str(spec_text).strip():
                    continue
                dot = Dot(radius=0.05, color=dot_col)
                t = CleanText(trim_words(str(spec_text), 30), font=FONT_HELVETICA, font_size=11, color=COLOR_WHITE,
                              max_width=2.75)
                row = VGroup(dot, t).arrange(RIGHT, buff=0.14)
                row.move_to([x, y, 0]).align_to(box, LEFT).shift(RIGHT * 0.3)
                spec_rows.add(row)
                y -= 0.55
            parts.add(spec_rows)
            if ratio is not None:
                try:
                    r = max(0.05, min(1.0, float(ratio)))
                    bar_bg = RoundedRectangle(corner_radius=0.06, width=2.8, height=0.26, color="#1E293B",
                                              fill_color="#0F172A", fill_opacity=0.9, stroke_width=1.0).move_to([x, y - 0.1, 0])
                    bar = RoundedRectangle(corner_radius=0.06, width=2.75 * r, height=0.22, color=dot_col,
                                           fill_color=dot_col, fill_opacity=0.9, stroke_width=0)
                    bar.move_to(bar_bg).align_to(bar_bg, LEFT).shift(RIGHT * 0.025)
                    parts.add(bar_bg, bar)
                    if metric_lbl:
                        parts.add(CleanText(trim_words(str(metric_lbl), 26), font=FONT_HELVETICA, font_size=10,
                                            color=dot_col, weight=BOLD, max_width=2.9).next_to(bar_bg, DOWN, buff=0.1))
                except (TypeError, ValueError):
                    pass
            if str(stat).strip():
                stat_t = CleanText(trim_words(str(stat), 28), font=FONT_HELVETICA, font_size=12, color=COLOR_WHITE,
                                   weight=BOLD, max_width=2.9)
                pill = RoundedRectangle(corner_radius=0.08, width=stat_t.width + 0.4, height=0.42, color=edge_col,
                                        fill_color="#0F172A", fill_opacity=0.9, stroke_width=1.2)
                pill.move_to([x, box.get_bottom()[1] + 0.45, 0])
                stat_t.move_to(pill)
                parts.add(pill, stat_t)
            return parts

        grp_a = _column(-1.9, col_a_title, col_a_tag, col_a_stat, col_a_specs, col_a_ratio, col_a_metric_lbl,
                        "#334155", COLOR_CORAL, COLOR_PANEL_BG, COLOR_CORAL)
        grp_b = _column(1.9, col_b_title, col_b_tag, col_b_stat, col_b_specs, col_b_ratio, col_b_metric_lbl,
                        accent_color, COLOR_WHITE, "#052E26", accent_color)

        vs_pill = RoundedRectangle(corner_radius=0.1, width=0.8, height=0.46, color="#475569", fill_color="#0F172A",
                                   fill_opacity=0.95, stroke_width=1.5).move_to([0, 0.6, 0])
        vs_txt = CleanText("VS", font=FONT_HELVETICA, font_size=12, color="#38BDF8", weight=BOLD).move_to(vs_pill)
        vs_grp = VGroup(vs_pill, vs_txt)

        self.col_a = grp_a
        self.col_b = grp_b
        self.vs_grp = vs_grp
        self.focus_target = grp_b

        self.content_group.add(grp_a, grp_b, vs_grp)
        self.kinetic_elements.add(grp_b)
        self.add(self.title, self.sub, self.content_group)

    def get_build_steps(self):
        """Old approach -> VS -> new approach."""
        return [[self.col_a], [self.vs_grp], [self.col_b]]

    def get_focus_animation(self, run_time: float = 1.0):
        return AnimationGroup(
            self.col_a.animate.set_opacity(0.45),
            Circumscribe(self.col_b, color=self.accent_color, time_width=0.6),
            run_time=run_time,
        )


class BlueprintPaperFigure(BaseBlueprintComposition):
    """
    Official arXiv Paper Figure Composition.
    Renders authentic architectural schematics, neural diagrams, or benchmark plots
    directly extracted from the cited publication's e-print bundle.
    Supports:
      1. Standalone vector SVGs recolored for the 3Blue1Brown carbon chalkboard (#0A0D14)
      2. High-resolution raster images (PNG/JPG) with clean dark-mode framing and glowing chassis
    Guarantees strict safe zones: centered at [0, 0.9, 0], bottom citation badge at y = -2.1,
    with zero collision against subtitles at y = -3.45 and math tray at y = -4.6.
    """
    def __init__(
        self,
        svg_path: Optional[str] = None,
        image_path: Optional[str] = None,
        title: str = "OFFICIAL ARCHITECTURE",
        sub: str = "Primary architectural diagram from arXiv source",
        arxiv_id: Optional[str] = None,
        badge_text: str = "ARXIV PUBLICATION FIGURE",
        accent_color: str = COLOR_CYAN,
        max_width: float = 7.5,
        max_height: float = 5.0,
        caption: Optional[str] = None,
        preferred_renderer: Optional[str] = None,
        **kwargs
    ):
        super().__init__(title=title, sub=sub, accent_color=accent_color, **kwargs)

        fig_mobj = None

        # 1. Prioritize high-resolution raster image (350 DPI master asset)
        if image_path and os.path.exists(image_path):
            try:
                im = ImageMobject(str(image_path))
                if im.width > max_width:
                    im.scale_to_fit_width(max_width)
                if im.height > max_height:
                    im.scale_to_fit_height(max_height)
                # Scale up small diagrams so they are crisp and prominent
                if im.width < 5.2 and im.height < 3.2:
                    scale_factor = min(max_width / max(im.width, 0.1), max_height / max(im.height, 0.1), 1.5)
                    im.scale(scale_factor)
                im.move_to([0, 0.9, 0])
                fig_mobj = im
            except Exception as e:
                print(f"⚠️ Error loading paper figure image: {e}")

        # 2. Try vector SVG as fallback
        if not fig_mobj and svg_path and os.path.exists(svg_path):
            try:
                m = SVGMobject(str(svg_path))
                if m.width > max_width:
                    m.scale_to_fit_width(max_width)
                if m.height > max_height:
                    m.scale_to_fit_height(max_height)
                # Scale up small diagrams so they are crisp and prominent
                if m.width < 5.2 and m.height < 3.2:
                    scale_factor = min(max_width / max(m.width, 0.1), max_height / max(m.height, 0.1), 1.5)
                    m.scale(scale_factor)
                m.move_to([0, 0.9, 0])
                fig_mobj = m
            except Exception as e:
                print(f"⚠️ Error loading paper figure SVG: {e}")

        # 3. Fallback placeholder if neither exists
        if not fig_mobj:
            box = RoundedRectangle(corner_radius=0.18, width=6.2, height=3.6, color=accent_color, stroke_width=2).move_to([0, 0.9, 0])
            lbl = CleanText(trim_words(title, 28), font_size=13, color=accent_color, weight=BOLD).move_to(box)
            fig_mobj = Group(box, lbl)

        # Architectural lightbox chassis behind figure with glowing accent and corner brackets
        chassis_w = min(max(fig_mobj.width + 0.6, 5.8), 7.8)
        chassis_h = max(fig_mobj.height + 0.6, 2.4)
        chassis_center = fig_mobj.get_center()

        # Outer subtle glow chassis
        self.glow_chassis = RoundedRectangle(
            corner_radius=0.18,
            width=chassis_w + 0.12,
            height=chassis_h + 0.12,
            color=accent_color,
            stroke_width=1.0,
            stroke_opacity=0.35,
            fill_color="#050811",
            fill_opacity=0.6
        ).move_to(chassis_center)

        # Primary inner chassis
        self.chassis = RoundedRectangle(
            corner_radius=0.15,
            width=chassis_w,
            height=chassis_h,
            color=COLOR_DARK_SLATE,
            stroke_width=2.0,
            fill_color=COLOR_PANEL_BG,
            fill_opacity=0.92
        ).move_to(chassis_center)

        # Four architectural corner brackets
        cx, cy = chassis_center[0], chassis_center[1]
        hw, hh = chassis_w / 2.0, chassis_h / 2.0
        self.corner_brackets = VGroup()
        for x_edge, y_edge, dx, dy in [
            (cx - hw, cy + hh, 1, -1),
            (cx + hw, cy + hh, -1, -1),
            (cx - hw, cy - hh, 1, 1),
            (cx + hw, cy - hh, -1, 1),
        ]:
            b_line_h = Line([x_edge, y_edge, 0], [x_edge + dx * 0.35, y_edge, 0], stroke_width=2.5, color=accent_color)
            b_line_v = Line([x_edge, y_edge, 0], [x_edge, y_edge + dy * 0.35, 0], stroke_width=2.5, color=accent_color)
            self.corner_brackets.add(b_line_h, b_line_v)

        # Top chassis telemetry header pill
        header_bar_w = min(chassis_w - 0.6, 4.4)
        header_pill = RoundedRectangle(
            corner_radius=0.08,
            width=header_bar_w,
            height=0.30,
            color="#0284C7",
            stroke_width=1.0,
            fill_color="#0369A1",
            fill_opacity=0.35
        ).move_to([cx, cy + hh - 0.22, 0])
        header_lbl = CleanText("ARXIV ARCHITECTURAL SCHEMATIC", font_size=8, color="#38BDF8", weight=BOLD).move_to(header_pill)
        self.lightbox_header = Group(header_pill, header_lbl)

        # Bottom citation badge (safe at y = -2.1, well above subtitles at y = -3.45)
        raw_b = badge_text.strip().upper()
        if arxiv_id and not raw_b.startswith("ARXIV"):
            badge_str = f"ARXIV: {arxiv_id} • {raw_b}"
        else:
            badge_str = raw_b
        badge_txt = CleanText(trim_words(badge_str, 42), font_size=9, color="#10B981", weight=BOLD)
        badge_pill = RoundedRectangle(
            corner_radius=0.12,
            width=badge_txt.width + 0.45,
            height=0.34,
            color="#10B981",
            stroke_width=1.2,
            fill_color="#064E3B",
            fill_opacity=0.65
        )
        badge_txt.move_to(badge_pill)
        self.badge = Group(badge_pill, badge_txt).move_to([0, -2.1, 0])

        # Kinetic laser sweep line
        self.laser_line = Line(
            [cx - hw + 0.2, cy + hh - 0.45, 0],
            [cx + hw - 0.2, cy + hh - 0.45, 0],
            color="#38BDF8",
            stroke_width=2.0,
            stroke_opacity=0.6
        )

        self.fig_mobj = fig_mobj
        self.content_group.add(
            self.glow_chassis,
            self.chassis,
            self.corner_brackets,
            self.lightbox_header,
            self.fig_mobj,
            self.badge,
            self.laser_line
        )
        self.kinetic_elements.add(self.fig_mobj)
        self.focus_target = self.fig_mobj
        self.add(self.title, self.sub, self.content_group)

    def get_build_steps(self):
        """Lightbox frame -> the paper's figure -> citation badge (laser is used by the focus only)."""
        return [
            [self.glow_chassis, self.chassis, self.corner_brackets, self.lightbox_header],
            {"mobjects": [self.fig_mobj], "animate": lambda rt: FadeIn(self.fig_mobj, scale=0.94, run_time=rt)},
            [self.badge],
        ]

    def get_focus_animation(self, run_time: float = 1.0):
        """A single scan line sweeps down the figure, then the figure is outlined."""
        top_y = self.chassis.get_top()[1] - 0.45
        bot_y = self.chassis.get_bottom()[1] + 0.45
        return Succession(
            FadeIn(self.laser_line, run_time=0.15 * run_time),
            self.laser_line.animate(run_time=0.6 * run_time, rate_func=linear).shift(DOWN * (top_y - bot_y)),
            AnimationGroup(FadeOut(self.laser_line), Circumscribe(self.fig_mobj, color=self.accent_color, time_width=0.6),
                           run_time=0.25 * run_time),
        )

    def get_kinetic_animation(self, run_time: float = 1.5) -> Animation:
        """Returns kinetic architectural laser sweep across the diagram."""
        if hasattr(self, "laser_line") and hasattr(self, "chassis"):
            top_y = self.chassis.get_top()[1] - 0.45
            bot_y = self.chassis.get_bottom()[1] + 0.45
            return AnimationGroup(
                self.fig_mobj.animate(rate_func=there_and_back, run_time=run_time).scale(1.03),
                self.laser_line.animate(rate_func=there_and_back, run_time=run_time).shift(DOWN * (top_y - bot_y))
            )
        return super().get_kinetic_animation(run_time=run_time)


# Registry mapping layout names to concrete composition classes
BLUEPRINT_COMPOSITION_REGISTRY = {
    "split_flow": BlueprintSplitFlow,
    "dual_stream": BlueprintSplitFlow,
    "bifurcated_tracks": BlueprintSplitFlow,
    "pipeline_stages": BlueprintPipelineStages,
    "sequential_flow": BlueprintPipelineStages,
    "grid_memory": BlueprintGridMemory,
    "spatial_matrix": BlueprintGridMemory,
    "kv_cache_grid": BlueprintGridMemory,
    "projection_rays": BlueprintProjectionRays,
    "camera_geometry": BlueprintProjectionRays,
    "barrier_separation": BlueprintBarrierSeparation,
    "anti_bleed_barrier": BlueprintBarrierSeparation,
    "tree_hierarchy": BlueprintTreeHierarchy,
    "branching_search": BlueprintTreeHierarchy,
    "layer_stack": BlueprintLayerStack,
    "hierarchical_composition": BlueprintLayerStack,
    "convergence_funnel": BlueprintConvergenceFunnel,
    "multimodal_fusion": BlueprintConvergenceFunnel,
    "catalog_routing": BlueprintCatalogRouting,
    "index_dispatch": BlueprintCatalogRouting,
    "comparison_side_by_side": BlueprintSideBySideComparison,
    "side_by_side": BlueprintSideBySideComparison,
    "paper_figure": BlueprintPaperFigure,
    "paper_architecture_figure": BlueprintPaperFigure,
    "arxiv_figure": BlueprintPaperFigure,
    "official_figure": BlueprintPaperFigure
}


def _register_extended_blueprints():
    """Dynamically register showdown, code execution, and physics primitives into the registry."""
    # 1. Showdown Engine
    try:
        from manim_engine.primitives.showdown_engine import (
            BlueprintHorizontalRaceBars,
            BlueprintRadarParetoPlot
        )
        BLUEPRINT_COMPOSITION_REGISTRY.update({
            "horizontal_race_bars": BlueprintHorizontalRaceBars,
            "race_bars": BlueprintHorizontalRaceBars,
            "benchmark_race": BlueprintHorizontalRaceBars,
            "drag_race_bars": BlueprintHorizontalRaceBars,
            "radar_pareto_plot": BlueprintRadarParetoPlot,
            "radar_plot": BlueprintRadarParetoPlot,
            "spider_chart": BlueprintRadarParetoPlot,
            "pareto_frontier": BlueprintRadarParetoPlot,
            "pareto_tradeoff": BlueprintRadarParetoPlot
        })
    except Exception:
        pass

    # 2. Code Execution Engine
    try:
        from manim_engine.primitives.code_execution_engine import BlueprintChalkboardCodeBlock
        BLUEPRINT_COMPOSITION_REGISTRY.update({
            "chalkboard_code_block": BlueprintChalkboardCodeBlock,
            "chalkboard_code": BlueprintChalkboardCodeBlock,
            "code_block": BlueprintChalkboardCodeBlock,
            "code_execution_trace": BlueprintChalkboardCodeBlock,
            "syntax_code_block": BlueprintChalkboardCodeBlock,
            "code_kernel": BlueprintChalkboardCodeBlock,
            "ast_code_trace": BlueprintChalkboardCodeBlock,
            "ast_tree": BlueprintChalkboardCodeBlock
        })
    except Exception:
        pass

    # 3. Physics Simulations
    try:
        from manim_engine.primitives.physics_simulations import PHYSICS_SIMULATION_REGISTRY
        BLUEPRINT_COMPOSITION_REGISTRY.update(PHYSICS_SIMULATION_REGISTRY)
    except Exception:
        pass


def create_blueprint_composition(layout: str, params: Optional[Dict[str, Any]] = None) -> BaseBlueprintComposition:
    """
    Factory function to instantiate any composable visual blueprint with provided parameters.
    Falls back gracefully to BlueprintPipelineStages if layout unknown.
    """
    if layout not in BLUEPRINT_COMPOSITION_REGISTRY:
        _register_extended_blueprints()

    cls = BLUEPRINT_COMPOSITION_REGISTRY.get(layout, BlueprintPipelineStages)
    clean_params = dict(params) if params else {}
    clean_params.pop("layout", None)

    # Data guard: the race-bar and radar primitives fall back to built-in demo numbers
    # (e.g. FlashAttention-3 TFLOPS) when given no data. Never let that reach a render:
    # without real contestants/models, show a non-numeric composition instead.
    numeric_data_key = {
        "horizontal_race_bars": "contestants", "race_bars": "contestants", "benchmark_race": "contestants",
        "drag_race_bars": "contestants", "radar_pareto_plot": "models", "radar_plot": "models",
        "spider_chart": "models", "pareto_frontier": "models", "pareto_tradeoff": "models",
    }.get(layout)
    code_layouts = {"chalkboard_code_block", "chalkboard_code", "code_block", "code_execution_trace",
                    "syntax_code_block", "code_kernel", "ast_code_trace", "ast_tree"}
    missing_data = (
        (numeric_data_key and not clean_params.get(numeric_data_key))
        or (layout in code_layouts and not (clean_params.get("lines") or clean_params.get("code_lines")))
    )
    if missing_data:
        print(f"⚠️ Layout '{layout}' has no verified data; rendering pipeline_stages instead of demo content.")
        cls = BlueprintPipelineStages
        clean_params = {k: v for k, v in clean_params.items() if k in ("title", "sub", "accent_color")}
    try:
        return cls(**clean_params)
    except Exception as e:
        print(f"⚠️ Error creating composition for layout '{layout}': {e}. Falling back with filtered parameters.")
        try:
            import inspect
            sig = inspect.signature(cls)
            filtered = {k: v for k, v in clean_params.items() if k in sig.parameters}
            return cls(**filtered)
        except Exception as e2:
            print(f"⚠️ Secondary fallback failed: {e2}. Falling back to default stages.")
            return BlueprintPipelineStages()

# Populate extended registries on module load
_register_extended_blueprints()
