# Changelog — The Model Verse Shorts

All notable changes, architectural pivots, bug fixes, and feature additions to this repository are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] — Word-synced animation engine

### Changed — how beats animate (`ANIMATION_ENGINE=timeline`, default)
- Each beat used to fade in, pulse 2–4% and slowly zoom in/out until the beat ended, so every beat looked the same. Now diagrams **build step by step as the narration names each part** (word timings from the aligner), the key element is emphasised on the beat's **anchor word** (a signal flowing along the connectors + an outline), and the frame otherwise holds still. Set `ANIMATION_ENGINE=legacy` to get the old behaviour.
- New `manim_engine/choreography/`: `timeline.py` (pure-Python planner) and `builders.py` (build steps, reveal/focus animations, safe-area fitting).
- Every diagram type has semantic build steps: split flow, pipeline, memory grid, projection rays, barrier, tree, layer stack, funnel, catalog, side-by-side, paper figure, flow field (particles now travel along streamlines), neural network (signal propagates layer by layer), attention prism (matrix fills in), loss landscape (the ball actually rolls into the minimum), race bars (rows race in one at a time), code block (lines typed in).
- Clean transitions: a beat is cleared before the next starts (no overlapping diagrams); no camera breathing or snap zoom (which pushed the formula into the captions).
- Diagrams are scaled up to ~1.2–1.3× to fill the 9:16 safe area; titles 20pt / subtitles 13pt.
- VLM-critic layout patches (`layout_overrides`) are now applied by `ScriptDrivenScene` (previously only the legacy scene read them, so the repair loop had no effect). Keyframes for the critic are sampled at 85% of each beat, after the build.

### Fixed — placeholder and hard-coded diagram content
- New `pipeline/layout_params.py`: maps mis-named blueprint params onto each diagram's real label slots and fills gaps from the beat (SVO subject/action/object, highlighted terms). Previously ~48% of beats rendered the diagram's demo labels ("SEMANTIC STREAM", "GEOMETRIC STREAM", ...).
- Removed hard-coded content shown in every video: tree "Optimal 99.4% Choice", catalog "O(1) Hash Map / Index Lookup", funnel "Harmonized Latent Representation", side-by-side BitNet FP16/ternary matrices and 100%/10% load bars, attention-cell numbers, the diffusion formula default on flow fields, stock phrases in synthesized blueprints.
- Labels/titles are shortened at word boundaries (`trim_words`) instead of mid-word ("ATTENTION IS ALL Y").

### Added
- `scripts/preview_beats.py`: render selected beats quickly at low quality (optionally with local Kokoro narration via `--tts`, or `--engine legacy` for before/after). No API keys needed.
- Tests: `test_beat_timeline.py`, `test_layout_params.py`, `test_choreography_manim.py` (needs Manim).

---

## [Unreleased] — Quality quick wins (branch `quality/quick-wins`)

### Fixed — fabricated numbers and code on screen
- **Prompt example leakage**: removed concrete example values (98.2%, 41.5%, "+56.7% SYNTACTIC RECOVERY GAIN", 1,180 TFLOPS, "Dense Baseline", ...) from the scriptwriter prompt; added a "numbers rule" and placeholders. 50 of 267 saved specs contained the 98.2/41.5 pair.
- **New `pipeline/grounding.py`**: removes metric fields whose numbers are not in the paper material (title / abstract / queue angle) and flags ungrounded narration numbers in `spec["quality_flags"]`.
- **`enforce_script_schema`** no longer backfills `payoff_stat: 98.2%`, `scale_metric: 10x`, a 1,180 TFLOPS benchmark, or a fake code snippet.
- **`benchmark_extractor`**: deleted keyword-matched fallback tables and the fixed radar scores; `extract_verified()` returns only spec or LaTeX-table data, else `None`.
- **Visuals**: race bars / radar / code blocks are only used with verified data; `create_blueprint_composition` refuses to render primitive demo numbers or demo code. Thumbnail profiles no longer carry DeepSeek-specific stats or a default formula.
- **Code blocks**: only real repository code (GitHub ingest, `repo_metadata`) is shown; generic placeholder kernels are dropped.

### Changed — hook gate
- The scriptwriter's hook is kept whenever usable (no lecture opener, 6–32 words, no ungrounded numbers); the regex score is diagnostic only. Replacement templates use the paper's short method name (never the video title) and no longer splice metadata metrics into paper hooks.

### Added — publish gate (`pipeline/publish_gate.py`)
- Holds a video when the script came from the deterministic fallback, narration has ungrounded numbers, prompt-example values leaked, the hook needs review, or the vision critic failed. Held videos upload to YouTube as **private** and skip Instagram / X / LinkedIn (`PUBLISH_GATE_MODE=private|skip|off`).
- The VLM critic marks heuristic fallback scores as `unverified`; set `PUBLISH_GATE_REQUIRE_VLM=true` to hold when no vision model ran.
- Daemon report shows the gate decision; held queue items are archived as `held_for_review`.

---

## [5.2.0] - 2026-10-03

### 💻 GitHub Trending AI & Live Code Execution Trace Visualizer
- **GitHub Trending & Kernel Ingestion Engine (`pipeline/github_trending_fetcher.py`)**:
  - Automatically monitors viral open-source AI repositories (vLLM, SGLang, BitNet, llama.cpp, DeepSeek kernels) via GitHub Search API with fallback to curated high-impact execution kernels.
  - Curated kernels for SGLang (RadixAttention prefix tree cache), vLLM (PagedAttention discrete block allocation), BitNet (1-bit Ternary GEMM weights), DeepSeek (MLA compression), and llama.cpp (GGML quantized SIMD).
- **Chalkboard Code & AST Execution Visualizer (`manim_engine/primitives/code_execution_engine.py`)**:
  - Implemented `BlueprintChalkboardCodeBlock` with minimalist macOS window chrome, red/yellow/green traffic lights, filename pill, and language badge (`PYTHON`, `CUDA`, `C++`).
  - Tokenized syntax highlighting for keywords (`#C084FC`), functions (`#60A5FA`), strings (`#10B981`), comments (`#94A3B8`), and numbers (`#F59E0B`).
  - Active execution line glowing scan with indicator notch aligned to executing line.
  - Live hardware memory register status pill (e.g. `⚡ RADIX HIT: +2,048 TOKENS REUSED`).
  - High-contrast emerald bottom delta badge (`#10B981`) highlighting efficiency gains.
- **Pipeline Integration (`pipeline/visual_director.py`, `pipeline/daily_shorts_daemon.py`)**:
  - Automatically routes Beats 3 and 4 to `chalkboard_code_block` when code snippets are present.
  - Added `--source` flag to `daily_shorts_daemon.py` supporting `arxiv`, `github`, and `mixed` candidate discovery.
  - Guaranteed 9:16 vertical safe zone clearance ($> 1.0$ unit buffer above kinetic subtitles).
- **Testing & Verification**:
  - Added `test/test_github_trending_fetcher.py` and `test/test_code_execution_engine.py` (12 tests passing).
  - Headless keyframe visual verification completed (`test_chalkboard_code_block.png`).

---

## [5.1.0] - 2026-10-03

### 🏎️ Automated Multi-Model Showdown & Radar Comparison Engine
- **Benchmark Extractor (`pipeline/benchmark_extractor.py`)**:
  - Parses LaTeX benchmark tables from arXiv e-print bundles into normalized quantitative metrics.
  - Structured fallbacks for throughput (TFLOPS), speedup multipliers, latency, and accuracy.
- **Horizontal Benchmark Race Bars (`manim_engine/primitives/showdown_engine.py`)**:
  - Animated progress tracks with glowing heads and hero highlight rows (`#10B981`).
  - Side-by-side comparison of 3–4 models/kernels with victory delta badge.
- **Radar / Spider Pareto Frontier Plot (`BlueprintRadarParetoPlot`)**:
  - Concentric 5-axis radial radar plot evaluating multi-dimensional trade-offs (Throughput, VRAM Efficiency, Accuracy, Context Length, Cost).
  - Semi-transparent hero polygon fill with contrasting baseline overlays.
- **Visual Director Assignment**:
  - Beat 5 dynamically assigned to `horizontal_race_bars` or `radar_pareto_plot`.
- **Testing**: Added `test/test_showdown_engine.py` (6 unit tests, headless render verification).

---

## [5.0.0] - 2026-10-02

### 🌊 Continuous Micro-Motion Updaters & Zero-Frozen-Frame Architecture
- **Continuous Updaters**:
  - Replaced static diagram dead-frames (4–6s freezes) with continuous mathematical motion via Manim `add_updater` and `ValueTracker`.
  - Continuous wave phase-travel, streaming particle swarms, glowing halo pulses, and camera drift.
- **Physics Simulation Primitives (`manim_engine/primitives/physics_simulations.py`)**:
  - `BlueprintVectorFlowField`: Dynamic velocity streamlines and particle drift.
  - `BlueprintNeuralActivationWave`: Synaptic propagation waves across layered neural nodes.
  - `BlueprintAttentionPrismRefraction`: Optical beam splitting into Query, Key, and Value vectors.
  - `BlueprintOptimizationLandscape`: 2.5D loss landscape gradient descent trajectory rolling into minima.

---

## [4.5.0] - 2026-10-01

### 📈 Real-Time YouTube Retention Feedback Loop & Autonomous Upload Daemon
- **YouTube Retention Analytics (`pipeline/analytics_feedback.py`)**:
  - Direct integration with YouTube Data API v3 and OAuth2 token refresh.
  - Real-time video performance query calculating viewer retention curves, average view duration, and view velocity (views/hour).
  - Dynamic domain velocity multipliers (e.g. `hardware_efficiency: 1.44x`, `multimodal_diffusion: 1.29x`).
  - Automated pacing recommendations: optimal narration speed (1.12x TTS) and hook duration ($\le 7.2\text{s}$).
- **Autonomous Daily Shorts Daemon (`pipeline/daily_shorts_daemon.py`)**:
  - 5 research-backed pre-peak upload windows (01:00, 05:00, 09:00, 12:00, 16:00 UTC).
  - End-to-end headless execution from discovery to 1440p60 QHD rendering, thumbnail generation, and YouTube upload.

---

## [4.0.0] - 2026-09-29

### 📐 Composable Visual Blueprints & Authentic ArXiv Figure Extraction
- **Composable Visual Blueprints (`manim_engine/primitives/visual_compositions.py`)**:
  - Modular, full-screen 3Blue1Brown chalkboard layout registry replacing brittle SVG synthesizers.
  - `BlueprintPipelineStages`, `BlueprintSplitFlow`, `BlueprintCatalogRouting`, `BlueprintProjectionRays`, `BlueprintBarrierSeparation`, `BlueprintDecisionTree`, `BlueprintLayerStack`, `BlueprintConvergenceFunnel`.
- **Native ArXiv Vector Figure Extractor (`pipeline/arxiv_vector_extractor.py`)**:
  - Downloads arXiv LaTeX e-print bundles (`.tar.gz`) and extracts authentic publication figures (PDF, EPS, SVG).
  - Chalkboard path recoloring engine converting white backgrounds and black strokes into `#0A0D14` carbon aesthetics with `#38BDF8` cyan and `#34D399` emerald accents.

---

## [3.5.0] - 2026-09-28

### 🎨 Dynamic Beat Vector & SVG Synthesizer
- **Bespoke Beat Diagrams (`pipeline/svg_synthesizer.py`)**:
  - LLM-assisted vector synthesis generating script-specific SVGs for individual beats based on SVO actions and everyday analogies.
  - Deterministic procedural fallback algorithms guaranteeing zero rendering failures.
- **Auditory-Visual SFX Layering**:
  - Tactile Foley sound design integration (`public/sfx/`) with automated millisecond-level mixdown in `pipeline/audio_synthesizer.py`.

---

## [3.0.0] - 2026-09-27

### 🎙️ Script Pedagogy Critic & Autonomous Self-Refinement
- **Script Critic (`pipeline/script_critic.py`)**:
  - Automated Flesch-Kincaid grade level evaluation (target: Grade 6.0–8.0).
  - Anti-jargon dictionary banning heavy academic jargon ("orchestration", "competence-aware", "bootstrap").
  - Physical analogy enforcement ensuring intuitive metaphors (sculptor, library, clouds, mirror).
  - Autonomous closed-loop self-refinement rewriting beats until quality gates pass.

---

## [2.0.0] - 2026-09-26

### 🔬 Visual Engine 2.0 & Modular 3Blue1Brown Primitives
- **Modular 3b1b Primitives**:
  - Robotics & TAMP (`CoupledCanvas`, `ParametricKinematicArm`, `ASTMorphTree`, `SandboxIsolationPod`).
  - Deep Learning & SAEs (`SAEConstellation`, `TransformerAttentionGrid`, `SparseMoELattice`, `RoutingRibbon`).
  - Search & Metrics (`DynamicSearchTree`, `RadialScoreMeter`, `DualMetricGauge`).
- **Declarative Visual Scene Graph (VSG) (`pipeline/vsg_schema.py`)**:
  - Pydantic schema with SVO semantic triples and explicit LaTeX formula bindings.
- **Acoustic Forced Alignment (`pipeline/aligner.py`)**:
  - 200 Hz energy valley snapping with the **Frame-Ahead Rule** (-33ms to -66ms) for frame-accurate animation timing.

---

## [1.0.0] - 2026-09-24

### 🚀 Initial Autonomous Video Generation Engine
- Autonomous pipeline translating arXiv papers into YouTube Shorts.
- Kokoro-82M neural text-to-speech synthesis (`am_adam`).
- Manim Community Edition vector rendering at 1080x1920.
- Procedural audio mixing with background synthwave soundtracks.
