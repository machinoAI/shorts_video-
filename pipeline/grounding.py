"""
Numeric grounding guard for generated script specs.

Problem this solves: the scriptwriter prompt used to contain concrete example
values (98.2%, 41.5%, "+56.7% SYNTACTIC RECOVERY GAIN", "1,180 TFLOPS", ...).
LLMs copied them into specs as if they were facts, and downstream code
(hook optimizer, race bars, thumbnails) put them on screen and in narration.

This module:
  1. Builds a "source text" from the ingested paper metadata (title, abstract,
     angle, key facts) — the only material the scriptwriter actually saw.
  2. Removes structured metric fields (metadata stats, benchmark tables,
     race-bar / radar params, delta badges) whose numbers do not appear in that
     source text.
  3. Removes formulas that contain known prompt-example sentinel values.
  4. Flags (but does not rewrite) narration numbers that are not in the source,
     so a publish gate can decide what to do.

Everything here is dependency-free so it can be unit-tested in isolation.
"""

import re
from typing import Any, Dict, Iterable, List, Optional, Set

# Values that appeared as concrete examples in older prompt/schema versions.
# If one of these shows up in a spec but NOT in the paper source text, it is
# almost certainly copied from the prompt rather than from the paper.
LEAKED_EXAMPLE_SENTINELS: Set[str] = {
    "98.2", "41.5", "56.7", "1180", "660", "610", "78.8", "94.5",
}
LEAKED_EXAMPLE_PHRASES: List[str] = [
    "SYNTACTIC RECOVERY",
    "Sparse SAE Latents",
]

# Metadata keys that hold quantitative claims.
METRIC_METADATA_KEYS = (
    "scale_metric", "payoff_stat", "payoff_hero_stat", "payoff_base_stat",
    "payoff_delta_badge", "model_a_stat", "model_b_stat", "efficiency_badge",
    "payoff_badge", "key_stat",
)
# Label keys that are meaningless once their paired stat is removed.
PAIRED_LABEL_KEYS = {
    "scale_metric": ("scale_label",),
    "payoff_stat": ("payoff_label", "payoff_sub"),
    "payoff_hero_stat": ("payoff_hero_label",),
    "payoff_base_stat": ("payoff_base_label",),
    "model_a_stat": ("model_a_stat_label",),
    "model_b_stat": ("model_b_stat_label",),
}

NUMERIC_LAYOUTS = ("horizontal_race_bars", "radar_pareto_plot", "comparative_bars", "benchmark_race", "race_bars")

# Numbers that carry no factual claim on their own (1.0x / 100% baselines, zero).
TRIVIAL_NUMBERS: Set[str] = {"0", "1", "100"}

# A standalone number: not glued to letters/hyphens/dots on the left (so "GPT-4",
# "H100", "FP8", "v2.1" are ignored), optional thousands separators/decimals.
_NUMBER_RE = re.compile(r"(?<![\w\-.])(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?")


def _normalize_number(int_part: str, frac_part: Optional[str]) -> str:
    raw = int_part.replace(",", "") + (frac_part or "")
    try:
        value = float(raw)
    except ValueError:
        return raw
    return f"{value:g}" if value < 1e15 else raw


def extract_numbers(text: Any) -> List[str]:
    """Returns normalized standalone numbers found in text ("1,180" -> "1180", "3.0x" -> "3")."""
    if text is None:
        return []
    if isinstance(text, (int, float)) and not isinstance(text, bool):
        return [f"{float(text):g}"]
    if not isinstance(text, str):
        return []
    return [_normalize_number(m.group(1), m.group(2)) for m in _NUMBER_RE.finditer(text)]


def _is_year(num: str) -> bool:
    return num.isdigit() and len(num) == 4 and 1900 <= int(num) <= 2099


def build_source_text(meta: Optional[Dict[str, Any]], extra: Iterable[str] = ()) -> str:
    """Concatenates the paper material the scriptwriter was given."""
    parts: List[str] = []
    if isinstance(meta, dict):
        for key in ("title", "paper_title", "topic", "abstract", "summary", "angle", "description"):
            val = meta.get(key)
            if isinstance(val, str):
                parts.append(val)
        for key in ("key_facts", "highlights"):
            val = meta.get(key)
            if isinstance(val, list):
                parts.extend(str(v) for v in val)
        for key in ("perk_metadata", "tech_news_metadata", "repo_metadata"):
            val = meta.get(key)
            if isinstance(val, dict):
                parts.extend(str(v) for v in val.values())
        # Topic-queue "angle" reaches the prompt via editorial_notes (see script_generator).
        notes = meta.get("editorial_notes")
        if isinstance(notes, dict) and isinstance(notes.get("suggested_everyday_analogy"), str):
            parts.append(notes["suggested_everyday_analogy"])
    parts.extend(s for s in extra if isinstance(s, str))
    return "\n".join(parts)


def ungrounded_numbers(value: Any, source_numbers: Set[str]) -> List[str]:
    """Numbers in `value` that are not present in the source and are not trivial/years."""
    return [
        n for n in extract_numbers(value)
        if n not in source_numbers and n not in TRIVIAL_NUMBERS and not _is_year(n)
    ]


def _contains_sentinel(text: Any, source_numbers: Set[str], source_text: str) -> List[str]:
    hits: List[str] = []
    if not isinstance(text, str):
        return hits
    for n in extract_numbers(text):
        if n in LEAKED_EXAMPLE_SENTINELS and n not in source_numbers:
            hits.append(n)
    for phrase in LEAKED_EXAMPLE_PHRASES:
        if phrase.lower() in text.lower() and phrase.lower() not in source_text.lower():
            hits.append(phrase)
    return hits


def _contestants_grounded(items: Any, source_numbers: Set[str], value_keys=("value", "display_val")) -> bool:
    if not isinstance(items, list) or not items:
        return False
    for c in items:
        if not isinstance(c, dict):
            return False
        for k in value_keys:
            if ungrounded_numbers(c.get(k), source_numbers):
                return False
    return True


# Lines from the old generic placeholder kernel / prompt example (never real code).
PLACEHOLDER_CODE_MARKERS = ("fused_forward_pass(tensor_in)", "execute_step(tensor_in)", "fused_kernel_op(input_tensor)")


def has_verified_code(spec: Dict[str, Any]) -> bool:
    """
    True only when spec["code_snippet"] came from a real repository (GitHub ingest sets
    repo_metadata). LLM-written "code" for papers is illustrative fiction presented as
    the paper's implementation, so it does not count.
    """
    if not isinstance(spec, dict) or not spec.get("repo_metadata"):
        return False
    code = spec.get("code_snippet")
    if not isinstance(code, dict) or code.get("provenance") == "placeholder":
        return False
    lines = code.get("lines") or code.get("code_lines") or []
    if not lines:
        return False
    joined = "\n".join(str(l) for l in lines)
    return not any(marker in joined for marker in PLACEHOLDER_CODE_MARKERS)


def apply_grounding_guard(spec: Dict[str, Any], source_text: str, scrub: bool = True) -> Dict[str, Any]:
    """
    Removes ungrounded quantitative claims from structured fields and records
    ungrounded narration numbers in spec["quality_flags"].

    scrub=False only records flags (used for tracks whose metadata we have not
    audited yet).
    """
    if not isinstance(spec, dict):
        return spec

    source_numbers = set(extract_numbers(source_text))
    flags = spec.get("quality_flags") if isinstance(spec.get("quality_flags"), dict) else {}
    scrubbed: List[str] = list(flags.get("scrubbed_fields", []))
    sentinels: List[Dict[str, Any]] = []

    # 1. Metadata stats
    meta = spec.get("metadata")
    if isinstance(meta, dict):
        for key in list(meta.keys()):
            if meta[key] is None:
                del meta[key]  # null placeholders must not reach `.get(key, default)` consumers
        for key in METRIC_METADATA_KEYS:
            if key in meta and ungrounded_numbers(meta[key], source_numbers):
                if scrub:
                    del meta[key]
                    for label in PAIRED_LABEL_KEYS.get(key, ()):
                        meta.pop(label, None)
                scrubbed.append(f"metadata.{key}")
        bench = meta.get("benchmarks")
        if isinstance(bench, list) and not _contestants_grounded(bench, source_numbers, ("score_a", "score_b")):
            if scrub:
                del meta["benchmarks"]
            scrubbed.append("metadata.benchmarks")

    # 2. Benchmark comparison table
    bc = spec.get("benchmark_comparison")
    if bc is not None:
        grounded = isinstance(bc, dict) and _contestants_grounded(bc.get("contestants"), source_numbers)
        if not grounded:
            if scrub:
                del spec["benchmark_comparison"]
            scrubbed.append("benchmark_comparison")
        elif ungrounded_numbers(bc.get("delta_badge"), source_numbers):
            if scrub:
                bc.pop("delta_badge", None)
            scrubbed.append("benchmark_comparison.delta_badge")

    # 3. Beat blueprints with numeric content + narration audit
    narration_flags: List[Dict[str, Any]] = []
    for beat in spec.get("beats", []) or []:
        if not isinstance(beat, dict):
            continue
        b_id = beat.get("beat_id")
        bp = beat.get("visual_blueprint")
        if isinstance(bp, dict) and isinstance(bp.get("params"), dict):
            params = bp["params"]
            if bp.get("layout") in NUMERIC_LAYOUTS:
                if "contestants" in params and not _contestants_grounded(params["contestants"], source_numbers):
                    if scrub:
                        del params["contestants"]
                    scrubbed.append(f"beats[{b_id}].visual_blueprint.params.contestants")
                if "models" in params:
                    # Radar scores are normalized 0-1 values the paper never states.
                    if scrub:
                        del params["models"]
                    scrubbed.append(f"beats[{b_id}].visual_blueprint.params.models")
            if ungrounded_numbers(params.get("delta_badge"), source_numbers):
                if scrub:
                    params.pop("delta_badge", None)
                scrubbed.append(f"beats[{b_id}].visual_blueprint.params.delta_badge")

        text = beat.get("text", "")
        missing = ungrounded_numbers(text, source_numbers)
        if missing:
            narration_flags.append({"beat_id": b_id, "numbers": missing, "text": text})
        for hit in _contains_sentinel(text, source_numbers, source_text):
            sentinels.append({"where": f"beats[{b_id}].text", "value": hit})

    # 4. Formulas carrying prompt-example values
    formulas = spec.get("math_formulas")
    if isinstance(formulas, list):
        kept = []
        for f in formulas:
            latex = f.get("latex", "") if isinstance(f, dict) else ""
            hits = _contains_sentinel(latex, source_numbers, source_text)
            if hits:
                sentinels.append({"where": f"math_formulas[beat {f.get('beat_id')}]", "value": hits[0]})
                if scrub:
                    continue
            kept.append(f)
        spec["math_formulas"] = kept

    flags["scrubbed_fields"] = sorted(set(scrubbed))
    flags["ungrounded_narration_numbers"] = narration_flags
    flags["leaked_example_values"] = sentinels
    flags["grounding_source_chars"] = len(source_text)
    spec["quality_flags"] = flags
    return spec
