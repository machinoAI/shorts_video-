"""
Publish gate: decides whether a produced short may go out publicly.

Before this gate, every produced video was uploaded publicly and cross-posted no
matter what the checks said: the script critic only warned, the vision critic
reported ~9/10 even when no vision model ran, and when every LLM failed a canned
fallback script was published.

Decision is "publish" or "hold". A held video is (by default) uploaded to YouTube
as PRIVATE so it can be reviewed in YouTube Studio and flipped to public by hand,
and it is NOT cross-posted to Instagram / X / LinkedIn (they have no private mode).

Environment:
  PUBLISH_GATE_MODE        private (default) | skip (no upload at all) | off (gate disabled)
  PUBLISH_GATE_REQUIRE_VLM true to also hold when no vision model actually audited frames
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

VALID_MODES = ("private", "skip", "off")


def evaluate_publish_gate(
    spec: Dict[str, Any],
    vlm_report: Optional[Dict[str, Any]] = None,
    script_report: Any = None,
) -> Dict[str, Any]:
    """Returns {"decision": "publish"|"hold", "reasons": [...], "warnings": [...]}."""
    reasons: List[str] = []
    warnings: List[str] = []

    # 1. Canned script: every LLM provider failed.
    if spec.get("script_provider") == "deterministic_fallback":
        reasons.append("Script came from the deterministic fallback (all LLM providers failed).")

    # 2. Grounding flags (pipeline/grounding.py)
    flags = spec.get("quality_flags") or {}
    leaked = flags.get("leaked_example_values") or []
    if leaked:
        values = sorted({str(x.get("value")) for x in leaked})
        reasons.append(f"Prompt-example values found in the script: {', '.join(values)}.")
    for item in flags.get("ungrounded_narration_numbers") or []:
        reasons.append(
            f"Beat {item.get('beat_id')} narration states numbers not found in the paper material: "
            f"{', '.join(item.get('numbers', []))}."
        )

    # 3. Hook gate could not find a usable hook.
    hook = spec.get("hook_gating") or {}
    if hook.get("needs_review"):
        why = ", ".join(hook.get("rejection_reasons", [])) or "unusable hook"
        reasons.append(f"Opening hook needs review ({why}).")

    # 4. Vision critic
    require_vlm = os.getenv("PUBLISH_GATE_REQUIRE_VLM", "false").lower() == "true"
    if vlm_report is None:
        (reasons if require_vlm else warnings).append("Vision critic did not run.")
    else:
        if not vlm_report.get("vision_verified", True):
            (reasons if require_vlm else warnings).append(
                "No vision model audited the keyframes (scores are heuristic placeholders)."
            )
        elif not vlm_report.get("passed_quality_gate", False):
            reasons.append(
                f"Vision critic failed the video after repair (average {vlm_report.get('average_score', 0):.1f}/10)."
            )
        for v in vlm_report.get("diversity_violations") or []:
            warnings.append(f"Visual diversity: {v}")

    # 5. Script readability critic (heuristic) -> warning only
    if script_report is not None and getattr(script_report, "passed", True) is False:
        warnings.append(f"Script critic: {getattr(script_report, 'summary_verdict', 'did not pass')}")

    return {
        "decision": "hold" if reasons else "publish",
        "reasons": reasons,
        "warnings": warnings,
    }


def resolve_gate_mode() -> str:
    mode = os.getenv("PUBLISH_GATE_MODE", "private").lower().strip()
    return mode if mode in VALID_MODES else "private"


def apply_gate_to_publishing(gate: Dict[str, Any], privacy: str) -> Dict[str, Any]:
    """
    Translates a gate decision into publishing actions.
    Returns {"youtube_upload": bool, "privacy": str, "cross_post": bool, "mode": str}.
    """
    mode = resolve_gate_mode()
    if gate.get("decision") != "hold" or mode == "off":
        return {"youtube_upload": True, "privacy": privacy, "cross_post": True, "mode": mode}
    if mode == "skip":
        return {"youtube_upload": False, "privacy": privacy, "cross_post": False, "mode": mode}
    return {"youtube_upload": True, "privacy": "private", "cross_post": False, "mode": mode}


def save_gate_report(gate: Dict[str, Any], video_path: str) -> Optional[str]:
    """Writes <video>.publish_gate.json next to the video (read by the daily daemon)."""
    try:
        out = Path(video_path).with_suffix(".publish_gate.json")
        out.write_text(json.dumps(gate, indent=2), encoding="utf-8")
        return str(out)
    except Exception:
        return None


def load_gate_report(video_path: str) -> Optional[Dict[str, Any]]:
    try:
        p = Path(video_path).with_suffix(".publish_gate.json")
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def print_gate(gate: Dict[str, Any], action: Dict[str, Any]) -> None:
    if gate["decision"] == "publish":
        print("   ✅ Publish gate: PASSED")
    else:
        print("   ⛔ Publish gate: HOLD")
        for r in gate["reasons"]:
            print(f"      • {r}")
        if action["mode"] == "off":
            print("      (PUBLISH_GATE_MODE=off — publishing anyway)")
        elif action["mode"] == "skip":
            print("      → Skipping all uploads (PUBLISH_GATE_MODE=skip).")
        else:
            print("      → Uploading to YouTube as PRIVATE for review; cross-posting skipped.")
    for w in gate.get("warnings", []):
        print(f"   ⚠️ {w}")
