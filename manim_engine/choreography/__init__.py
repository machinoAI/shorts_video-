"""
Word-synced beat choreography.

timeline.py  — pure-Python planner: decides WHEN each build step / focus / formula
               happens inside a beat, using the narration's word timings.
builders.py  — Manim side: turns a composition into ordered build steps and
               creates the reveal / focus animations.

Replaces the old per-beat recipe (fade in -> 2-4% scale pulse -> slow zoom
"breathing" until the beat ends), which made every beat look the same.
"""
