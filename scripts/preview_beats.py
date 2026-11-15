#!/usr/bin/env python3
"""
Quick local preview of the animation for selected beats — no upload and no LLM calls.

Examples
  # Re-stage an existing script with the current visual director and render beats 1-3 at low quality
  python scripts/preview_beats.py --spec pipeline/templates/architecture_breakdown_attention_is_all_you_need_pt1.json --beats 1-3

  # Same beats with the old choreography, for a before/after comparison
  python scripts/preview_beats.py --spec ... --beats 1-3 --engine legacy

  # Synthesize narration with the local Kokoro voice first (real word timings + audio in the preview)
  python scripts/preview_beats.py --spec ... --beats 2 --tts

Output: an MP4 path is printed at the end (with audio when --tts is used).
"""

import argparse
import copy
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

SCENE_FILE = "manim_engine/scenes/script_driven_scene.py"
SCENE_CLASS = "ScriptDrivenScene"


def parse_beats(raw: str):
    beats = set()
    for part in raw.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            beats.update(range(int(lo), int(hi) + 1))
        elif part:
            beats.add(int(part))
    return sorted(beats)


def enrich_with_tts(spec):
    """Local Kokoro narration (no API key) -> beat start/end + word timings, like auto_produce."""
    from pipeline.audio_synthesizer import synthesize_audio_for_spec
    res = synthesize_audio_for_spec(spec, provider="kokoro", enable_music=False)
    for b in spec.get("beats", []):
        for td in res.get("timing_data", []):
            if td["beat_id"] == b.get("beat_id"):
                b["audio_duration"] = td["duration"]
                b["slot_duration"] = td["slot_duration"]
                b["start"] = td["start"]
                b["end"] = td["end"]
                b["word_timings"] = td.get("word_timings", [])
    return res.get("master_audio")


def ensure_timings(spec):
    """Without audio, lay beats back to back using their stored or default durations."""
    t = 0.0
    for b in spec.get("beats", []):
        dur = float(b.get("slot_duration") or (float(b.get("audio_duration", 0)) + 0.35) or 6.5)
        if dur <= 0.5:
            dur = 6.5
        b.setdefault("start", round(t, 2))
        b.setdefault("slot_duration", round(dur, 2))
        t = float(b["start"]) + float(b["slot_duration"])


def main():
    ap = argparse.ArgumentParser(description="Render a quick preview of selected beats")
    ap.add_argument("--spec", required=True, help="Path to a script spec JSON (pipeline/templates/*.json)")
    ap.add_argument("--beats", default="1-5", help="Beats to render, e.g. '2' or '1,3' or '1-4'")
    ap.add_argument("--quality", default="l", choices=["l", "m", "h"], help="Manim quality (l = fast)")
    ap.add_argument("--engine", default="timeline", choices=["timeline", "legacy"], help="Choreography engine")
    ap.add_argument("--tts", action="store_true", help="Synthesize local Kokoro narration for real timings + audio")
    ap.add_argument("--no-restage", action="store_true", help="Skip re-running the visual director on the spec")
    args = ap.parse_args()

    spec_path = Path(args.spec).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    beats = parse_beats(args.beats)

    out_dir = PROJECT_ROOT / "media" / "previews"
    out_dir.mkdir(parents=True, exist_ok=True)
    work = copy.deepcopy(spec)

    if not args.no_restage:
        from pipeline.visual_director import VisualDirector
        for b in work.get("beats", []):
            b.pop("motif_params", None)  # let the current director rebuild labels/layouts
        work = VisualDirector().prepare_storyboard_for_spec(work)

    master_audio = enrich_with_tts(work) if args.tts else None
    ensure_timings(work)

    preview_spec = out_dir / f"{work.get('id', 'spec')}_preview_spec.json"
    preview_spec.write_text(json.dumps(work, indent=2), encoding="utf-8")

    os.environ["PREVIEW_BEATS"] = ",".join(str(b) for b in beats)
    os.environ["ANIMATION_ENGINE"] = args.engine
    from pipeline.run_pipeline import render_scene
    raw_video = render_scene(SCENE_FILE, SCENE_CLASS, quality=f"-q{args.quality}", spec_path=str(preview_spec))

    final = raw_video
    if master_audio and os.path.exists(master_audio):
        sel = [b for b in work["beats"] if b.get("beat_id") in beats]
        offset = min(float(b["start"]) for b in sel)
        end = max(float(b["start"]) + float(b.get("slot_duration", 6.0)) for b in sel)
        final = str(out_dir / f"{work.get('id', 'spec')}_beats_{'_'.join(map(str, beats))}_{args.engine}.mp4")
        ffmpeg = os.environ.get("FFMPEG_BIN", "ffmpeg")
        subprocess.run([ffmpeg, "-y", "-i", raw_video, "-ss", f"{offset:.3f}", "-t", f"{end - offset:.3f}",
                        "-i", master_audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", final],
                       check=False, capture_output=True)
        if not os.path.exists(final):
            final = raw_video

    print(f"\n✅ Preview ready: {final}")


if __name__ == "__main__":
    main()
