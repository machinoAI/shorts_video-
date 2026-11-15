"""
Manim side of the word-synced choreography.

- get_build_steps(comp): ordered reveal steps for any composition. Compositions may
  define get_build_steps() for semantic order; otherwise steps are derived from the
  order of content_group (connectors are attached to the node they lead to).
- reveal_step(step, run_time): the reveal animation for one step.
- focus_animation(comp, run_time): emphasis on the anchor word — a signal flowing
  along the diagram's connectors plus an outline around the key element. This
  replaces the old whole-diagram scale "pulse".
- fit_to_safe_area(comp, ...): uniformly scales a composition to use the 9:16 safe
  area (bigger diagrams and text) without colliding with header / formula / captions.
"""

from typing import Any, Callable, Dict, List, Optional, Sequence

import numpy as np
from manim import (
    Animation, AnimationGroup, Arc, Arrow, Circumscribe, Create, CubicBezier, FadeIn,
    Group, GrowArrow, ImageMobject, LaggedStart, Line, Mobject, ShowPassingFlash,
    Succession, VMobject, Wait, UP, YELLOW,
)

# 9:16 safe area (frame is 9 x 16 units, y in [-8, 8])
SAFE_TOP = 6.35            # brand header sits at y = 7.1
SAFE_BOTTOM_WITH_FORMULA = -1.95   # formula tray centred at y = -2.6
SAFE_BOTTOM = -3.05        # caption pill centred at y = -3.85
SAFE_WIDTH = 8.1
MAX_UPSCALE = 1.3


class BuildStep:
    """One reveal step: the mobjects it shows, their label texts, optional custom animation."""

    def __init__(self, mobjects: Sequence[Mobject], cues: Optional[Sequence[str]] = None,
                 animate: Optional[Callable[[float], Animation]] = None):
        self.mobjects = [m for m in mobjects if m is not None]
        self.cues = list(cues) if cues is not None else texts_in(self.mobjects)
        self.animate = animate


# ---------------------------------------------------------------- helpers

def texts_in(mobjects: Sequence[Mobject]) -> List[str]:
    """Label strings of all Text-like mobjects in the given families."""
    out: List[str] = []
    for m in mobjects:
        try:
            family = m.get_family()
        except Exception:
            family = [m]
        for f in family:
            for attr in ("original_text", "text"):
                val = getattr(f, attr, None)
                if isinstance(val, str) and val.strip():
                    if val not in out:
                        out.append(val)
                    break
    return out


def is_connector(m: Mobject) -> bool:
    return isinstance(m, (Line, Arc, CubicBezier))


def _contains_image(m: Mobject) -> bool:
    try:
        return any(isinstance(f, ImageMobject) for f in m.get_family())
    except Exception:
        return isinstance(m, ImageMobject)


def reveal(m: Mobject) -> Animation:
    """Natural reveal for one mobject: arrows grow, strokes draw, everything else fades up."""
    if isinstance(m, Arrow):
        return GrowArrow(m)
    if is_connector(m):
        return Create(m)
    if _contains_image(m):
        return FadeIn(m, scale=0.97)
    return FadeIn(m, shift=UP * 0.12)


def _header(comp: Mobject) -> List[Mobject]:
    return [m for m in (getattr(comp, "title", None), getattr(comp, "sub", None)) if m is not None]


def _coerce_step(item: Any) -> Optional[BuildStep]:
    if isinstance(item, BuildStep):
        return item
    if isinstance(item, dict):
        return BuildStep(item.get("mobjects", []), item.get("cues"), item.get("animate"))
    if isinstance(item, (list, tuple)):
        return BuildStep(list(item))
    if isinstance(item, Mobject):
        return BuildStep([item])
    return None


def _chunk(items: List[List[Mobject]], max_steps: int) -> List[List[Mobject]]:
    if len(items) <= max_steps:
        return items
    out: List[List[Mobject]] = []
    per = len(items) / float(max_steps)
    for i in range(max_steps):
        lo, hi = int(round(i * per)), int(round((i + 1) * per))
        merged: List[Mobject] = []
        for chunk in items[lo:hi]:
            merged.extend(chunk)
        if merged:
            out.append(merged)
    return out


# ---------------------------------------------------------------- steps

def derive_default_steps(comp: Mobject, max_steps: int = 4) -> List[BuildStep]:
    content = getattr(comp, "content_group", None)
    header = _header(comp)
    if content is not None and len(content.submobjects) > 0:
        items = list(content.submobjects)
    else:
        items = [m for m in comp.submobjects if m not in header]

    chunks: List[List[Mobject]] = []
    pending: List[Mobject] = []
    for m in items:
        if is_connector(m):
            pending.append(m)       # an arrow appears together with the node it points to
            continue
        chunks.append(pending + [m])
        pending = []
    if pending:
        if chunks:
            chunks[-1].extend(pending)
        else:
            chunks.append(pending)

    chunks = _chunk(chunks, max_steps)
    steps = [BuildStep(c) for c in chunks] or [BuildStep([])]
    steps[0] = BuildStep(header + steps[0].mobjects, cues=steps[0].cues)
    return steps


def get_build_steps(comp: Mobject, max_steps: int = 4) -> List[BuildStep]:
    custom = getattr(comp, "get_build_steps", None)
    steps: List[BuildStep] = []
    if callable(custom):
        try:
            steps = [s for s in (_coerce_step(i) for i in (custom() or [])) if s is not None]
        except Exception as e:
            print(f"⚠️ get_build_steps failed for {type(comp).__name__}: {e}. Using default order.")
            steps = []
    if not steps:
        # LLM-written bespoke visuals (no content_group) keep their own entrance animation.
        if getattr(comp, "content_group", None) is None and hasattr(comp, "get_entrance_animation"):
            return [BuildStep([comp], cues=texts_in([comp]),
                              animate=lambda rt, c=comp: c.get_entrance_animation(run_time=rt))]
        return derive_default_steps(comp, max_steps=max_steps)

    # Make sure the composition title/sub appear with the first step.
    header = [h for h in _header(comp) if all(h not in s.mobjects for s in steps)]
    if header:
        first = steps[0]
        steps[0] = BuildStep(header + first.mobjects, cues=first.cues, animate=first.animate)
        if first.animate is not None:
            # custom first step: fade the header in alongside it
            steps[0].animate = lambda rt, f=first, h=header: AnimationGroup(
                *[FadeIn(m, shift=UP * 0.1) for m in h], f.animate(rt), run_time=rt)
    return steps


def reveal_step(step: BuildStep, run_time: float) -> Animation:
    if step.animate is not None:
        try:
            return step.animate(run_time)
        except Exception as e:
            print(f"⚠️ Custom step animation failed ({e}); using default reveal.")
    anims = [reveal(m) for m in step.mobjects]
    if not anims:
        return Wait(run_time)
    return LaggedStart(*anims, lag_ratio=0.22, run_time=run_time)


# ---------------------------------------------------------------- focus

def _flow_connectors(comp: Mobject) -> List[VMobject]:
    content = getattr(comp, "content_group", None)
    if content is None:
        return []
    conns: List[VMobject] = []
    for m in content.submobjects:
        if is_connector(m):
            conns.append(m)
    return conns[:4]


def _focus_target(comp: Mobject) -> Optional[Mobject]:
    target = getattr(comp, "focus_target", None)
    if target is not None:
        return target
    kin = getattr(comp, "kinetic_elements", None)
    if kin is not None and len(kin.submobjects) > 0:
        return kin.submobjects[0]
    return getattr(comp, "content_group", None)


def focus_animation(comp: Mobject, run_time: float) -> Animation:
    custom = getattr(comp, "get_focus_animation", None)
    if callable(custom):
        try:
            return custom(run_time=run_time)
        except Exception as e:
            print(f"⚠️ get_focus_animation failed for {type(comp).__name__}: {e}")

    # LLM-written bespoke visuals define their own "kinetic" action for the anchor word.
    if getattr(comp, "content_group", None) is None and callable(getattr(comp, "get_kinetic_animation", None)):
        try:
            return comp.get_kinetic_animation(run_time=run_time)
        except Exception as e:
            print(f"⚠️ Bespoke kinetic animation failed: {e}")

    accent = getattr(comp, "accent_color", YELLOW)
    anims: List[Animation] = []

    flows = []
    for c in _flow_connectors(comp):
        try:
            glow = c.copy().set_stroke(color=YELLOW, width=max(5.0, c.get_stroke_width() + 3.0), opacity=1.0)
            flows.append(ShowPassingFlash(glow, time_width=0.6))
        except Exception:
            continue
    if flows:
        anims.append(Succession(*flows))

    target = _focus_target(comp)
    if target is not None:
        try:
            anims.append(Circumscribe(target, color=accent, time_width=0.6, buff=0.12))
        except Exception:
            pass

    if not anims:
        return Wait(run_time)
    return AnimationGroup(*anims, run_time=run_time)


# ---------------------------------------------------------------- layout

def _scale_into_box(mob: Mobject, top: float, bottom: float, width: float) -> float:
    w, h = float(mob.width), float(mob.height)
    if w <= 0.01 or h <= 0.01 or top - bottom <= 0.5:
        return 1.0
    factor = min(width / w, (top - bottom) / h, MAX_UPSCALE)
    if factor < 0.999 or factor > 1.03:
        mob.scale(factor)
    mob.move_to(np.array([0.0, (top + bottom) / 2.0, 0.0]))
    return factor


def fit_to_safe_area(comp: Mobject, has_formula: bool) -> float:
    """
    Pins the title/sub to the top of the safe area and scales the diagram itself
    (content_group) up to 1.3x to fill the space between title and formula/captions.
    Returns the diagram's scale factor.
    """
    bottom = SAFE_BOTTOM_WITH_FORMULA if has_formula else SAFE_BOTTOM
    content = getattr(comp, "content_group", None)
    header = _header(comp)
    if content is None or len(content.submobjects) == 0 or not header:
        return _scale_into_box(comp, SAFE_TOP, bottom, SAFE_WIDTH)

    head = Group(*header)
    head.move_to(np.array([0.0, SAFE_TOP - head.height / 2.0, 0.0]))
    content_top = head.get_bottom()[1] - 0.35
    return _scale_into_box(content, content_top, bottom, SAFE_WIDTH)


def apply_layout_override(mob: Mobject, override: Optional[Dict[str, Any]]) -> None:
    """Applies a VLM-critic patch {dx, dy, scale_multiplier} to a mobject."""
    if not override or mob is None:
        return
    try:
        s = float(override.get("scale_multiplier", 1.0) or 1.0)
        if abs(s - 1.0) > 1e-3:
            mob.scale(s)
        dx, dy = float(override.get("dx", 0.0) or 0.0), float(override.get("dy", 0.0) or 0.0)
        if dx or dy:
            mob.shift(np.array([dx, dy, 0.0]))
    except Exception as e:
        print(f"⚠️ Layout override ignored: {e}")
