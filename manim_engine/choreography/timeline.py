"""
Beat timeline planner (pure Python, no Manim import — unit-testable anywhere).

Given a beat's time window, its build steps (with the words each step is "about"),
the narration word timings and the beat's anchor word, it returns an ordered list of
events:

  step    reveal build step i            (fires when the narration mentions it)
  focus   emphasise the key element      (fires on the anchor word)
  formula show the beat's equation       (attached to a mid-beat step)
  exit    clear the beat                 (last ~0.35s of the beat)

Each event carries a run_time that never overlaps the next event, so the scene can
play them back with plain wait()/play() calls and stay locked to the audio clock.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "onto", "over", "under",
    "your", "their", "them", "they", "what", "when", "where", "which", "while", "than",
    "then", "just", "only", "each", "every", "more", "most", "less", "very", "like",
    "stream", "streams", "layer", "stage", "step", "beat", "model", "models", "input",
    "output", "data", "path", "node", "block", "core", "unit", "system",
}

MIN_GAP = 0.55          # seconds between two events
EXIT_TIME = 0.35        # fade-out at the end of the beat
STEP_RUN = 0.8          # preferred duration of a reveal
FOCUS_RUN = 1.1         # preferred duration of the emphasis
BUILD_FRACTION = 0.72   # unmatched steps are spread over the first 72% of the beat


@dataclass
class TimelineEvent:
    kind: str                      # "step" | "focus" | "exit"
    time: float                    # absolute scene time in seconds
    run_time: float
    index: int = 0                 # step index for kind == "step"
    with_formula: bool = False     # also reveal the formula tray with this step
    cue: Optional[str] = None      # word that triggered it (for debugging/logs)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}


def normalize_word(word: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(word).lower())


def cue_tokens(texts: Iterable[str]) -> List[str]:
    """Meaningful tokens from a step's label texts (len >= 4, not stopwords)."""
    tokens: List[str] = []
    for t in texts:
        for w in re.split(r"[\s/_\-:,.()\[\]]+", str(t)):
            n = normalize_word(w)
            if len(n) >= 4 and n not in STOPWORDS and not n.isdigit() and n not in tokens:
                tokens.append(n)
    return tokens


def _matches(word: str, tokens: Sequence[str]) -> bool:
    if not word or len(word) < 3:
        return False
    for tok in tokens:
        if word == tok:
            return True
        # Shared stem: "routing"/"router", "attention"/"attend", "caches"/"cache"
        stem = min(5, len(tok), len(word))
        if stem >= 4 and word[:stem] == tok[:stem]:
            return True
    return False


def _word_time(w: Dict[str, Any]) -> Optional[float]:
    for key in ("frame_ahead_trigger", "start"):
        val = w.get(key)
        if isinstance(val, (int, float)):
            return float(val)
    return None


def find_anchor_time(word_timings: Sequence[Dict[str, Any]], anchor_word: Optional[str],
                     after: float = 0.0) -> Optional[float]:
    target = normalize_word(anchor_word or "")
    if not target:
        return None
    for w in word_timings or []:
        t = _word_time(w)
        if t is None or t < after:
            continue
        cw = normalize_word(w.get("clean_word") or w.get("word") or "")
        if cw and (cw == target or (len(target) >= 5 and cw.startswith(target[:5]))):
            return t
    return None


def plan_beat_timeline(
    beat_start: float,
    beat_end: float,
    step_cues: Sequence[Sequence[str]],
    word_timings: Optional[Sequence[Dict[str, Any]]] = None,
    anchor_word: Optional[str] = None,
    has_formula: bool = False,
    has_focus: bool = True,
) -> List[TimelineEvent]:
    """
    step_cues[i] = label texts shown by build step i (used to find the word that
    triggers it). Step 0 always fires at the beat start.
    """
    duration = max(0.5, beat_end - beat_start)
    n = max(1, len(step_cues))
    words = list(word_timings or [])
    usable_end = beat_end - EXIT_TIME
    build_end = beat_start + BUILD_FRACTION * duration

    # 1. Step trigger times
    times: List[float] = [beat_start]
    cues_used: List[Optional[str]] = [None]
    for i in range(1, n):
        earliest = times[-1] + MIN_GAP
        even_slot = beat_start + (i / n) * (build_end - beat_start)
        tokens = cue_tokens(step_cues[i])
        chosen, cue = None, None
        if tokens:
            for w in words:
                t = _word_time(w)
                if t is None or t < earliest or t > usable_end - MIN_GAP:
                    continue
                cw = normalize_word(w.get("clean_word") or w.get("word") or "")
                if _matches(cw, tokens):
                    chosen, cue = t, cw
                    break
        if chosen is None:
            chosen = max(earliest, even_slot)
        times.append(chosen)
        cues_used.append(cue)

    # 2. If steps overflow the beat, compress them evenly into the build window
    last_allowed = usable_end - (MIN_GAP if has_focus else 0.2)
    if times[-1] > last_allowed:
        span = max(0.3, last_allowed - beat_start)
        times = [beat_start + span * (i / max(1, n - 1)) * (0.0 if n == 1 else 1.0) for i in range(n)]

    events: List[TimelineEvent] = [
        TimelineEvent(kind="step", time=round(t, 3), run_time=STEP_RUN, index=i, cue=c)
        for i, (t, c) in enumerate(zip(times, cues_used))
    ]

    # 3. Formula rides along with a middle step (never the very first frame)
    if has_formula:
        target = min(1, n - 1) if n > 1 else 0
        events[target].with_formula = True

    # 4. Focus on the anchor word, after the build
    if has_focus:
        after = times[-1] + MIN_GAP
        t_focus = find_anchor_time(words, anchor_word, after=after)
        if t_focus is None or t_focus > usable_end - 0.4:
            remaining = usable_end - after
            t_focus = after + 0.3 * remaining if remaining >= 0.9 else None
        if t_focus is not None and t_focus <= usable_end - 0.4:
            events.append(TimelineEvent(kind="focus", time=round(t_focus, 3), run_time=FOCUS_RUN,
                                        cue=normalize_word(anchor_word or "") or None))

    events.append(TimelineEvent(kind="exit", time=round(usable_end, 3), run_time=EXIT_TIME))

    # 5. Clip run_times so no event overlaps the next one
    events.sort(key=lambda e: (e.time, 0 if e.kind == "step" else 1))
    for cur, nxt in zip(events, events[1:]):
        room = nxt.time - cur.time - 0.02
        cur.run_time = round(max(0.15, min(cur.run_time, room)), 3)
    return events
