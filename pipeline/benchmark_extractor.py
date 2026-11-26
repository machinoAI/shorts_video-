"""
The Model Verse — Benchmark & Showdown Table Extractor
Extracts quantitative performance tables (throughput, accuracy, latency, memory, TFLOPS)
from arXiv LaTeX source bundles and metadata, formatting them for high-dopamine Manim
Horizontal Race Bars and Radar/Spider Pareto Plots.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class BenchmarkContestant:
    name: str
    value: float
    raw_str: str
    is_hero: bool = False
    color: str = "#38BDF8"  # Default Cyan


@dataclass
class BenchmarkComparison:
    title: str
    metric_name: str
    unit: str
    higher_is_better: bool = True
    contestants: List[BenchmarkContestant] = field(default_factory=list)
    delta_badge: str = ""
    radar_axes: List[str] = field(default_factory=list)
    radar_models: List[Dict[str, Any]] = field(default_factory=list)


class BenchmarkExtractor:
    """
    Parses LaTeX tables from arXiv source tarballs or synthesizes benchmark
    data from paper metadata, structured for race bars and radar plots.
    """

    BENCHMARK_KEYWORDS = [
        "tflops", "gflops", "flops", "throughput", "latency", "speedup",
        "speed", "tok/s", "tokens/s", "pass@1", "aime", "math", "gsm8k",
        "mmlu", "humaneval", "bleu", "vram", "memory", "accuracy", "%", "ms"
    ]

    MODEL_KEYWORDS = [
        "ours", "deepseek", "flashattention", "gpt", "claude", "llama",
        "gemini", "mistral", "qwen", "cudnn", "triton", "baseline",
        "standard", "pytorch", "vllm", "sglang", "transformer"
    ]

    def __init__(self):
        pass

    def clean_latex_text(self, text: str) -> str:
        """Strips LaTeX formatting commands, bold/italic markup, and citations."""
        text = re.sub(r"\\textbf\{([^}]+)\}", r"\1", text)
        text = re.sub(r"\\textit\{([^}]+)\}", r"\1", text)
        text = re.sub(r"\\underline\{([^}]+)\}", r"\1", text)
        text = re.sub(r"\\emph\{([^}]+)\}", r"\1", text)
        text = re.sub(r"\\cite\{[^}]+\}", "", text)
        text = re.sub(r"\\ref\{[^}]+\}", "", text)
        text = re.sub(r"\\text(?:subscript|superscript)\{[^}]+\}", "", text)
        text = re.sub(r"\$([^\$]+)\$", r"\1", text)  # inline math
        text = re.sub(r"\\pm\s*[\d\.]+", "", text)   # error margins \pm 0.2
        text = re.sub(r"\\%", "%", text)
        text = re.sub(r"\\times", "x", text)
        text = text.replace("~", " ").replace("{", "").replace("}", "")
        return text.strip()

    def parse_latex_table(self, table_str: str) -> Optional[BenchmarkComparison]:
        """
        Parses a single LaTeX tabular/table environment into structured columns and rows.
        Identifies candidate methods and numerical metrics.
        """
        lines = [l.strip() for l in table_str.splitlines() if l.strip()]
        cleaned_rows: List[List[str]] = []

        for line in lines:
            if line.startswith(("%", "\\toprule", "\\midrule", "\\bottomrule", "\\hline", "\\caption", "\\label")):
                continue
            if line.startswith(("\\begin", "\\end")):
                continue
            
            # Remove trailing \\ or \cr
            line = re.sub(r"\\\\.*$", "", line).strip()
            if not line:
                continue

            cols = [self.clean_latex_text(c) for c in line.split("&")]
            if len(cols) >= 2:
                cleaned_rows.append(cols)

        if len(cleaned_rows) < 2:
            return None

        # Row 0 or 1 is likely header
        headers = cleaned_rows[0]
        data_rows = cleaned_rows[1:]

        # Find which column has numbers and which column has model names
        num_col_idx = -1
        name_col_idx = 0

        # Scan for best numerical metric column
        best_metric_name = "Performance"
        unit = ""
        higher_is_better = True

        for col_idx in range(1, len(headers)):
            col_header = headers[col_idx].lower() if col_idx < len(headers) else ""
            # Count valid numbers in this column
            num_matches = 0
            for row in data_rows:
                if col_idx < len(row):
                    val_str = re.sub(r"[^\d\.]", "", row[col_idx])
                    try:
                        float(val_str)
                        num_matches += 1
                    except ValueError:
                        pass
            if num_matches >= max(2, len(data_rows) // 2):
                num_col_idx = col_idx
                best_metric_name = headers[col_idx].strip() or "Throughput"
                break

        if num_col_idx == -1:
            return None

        # Determine unit and direction
        h_lower = best_metric_name.lower()
        if "tflops" in h_lower:
            unit = "TFLOPS"
        elif "latency" in h_lower or "ms" in h_lower:
            unit = "ms"
            higher_is_better = False
        elif "%" in h_lower or "acc" in h_lower or "pass" in h_lower:
            unit = "%"
        elif "tok" in h_lower or "speed" in h_lower:
            unit = "tokens/s"
        elif "speedup" in h_lower or "x" in h_lower:
            unit = "x"

        contestants: List[BenchmarkContestant] = []
        palette = ["#10B981", "#38BDF8", "#F59E0B", "#A855F7", "#EF4444"]

        for idx, row in enumerate(data_rows):
            if len(row) <= max(name_col_idx, num_col_idx):
                continue
            name = row[name_col_idx].strip()
            raw_val = row[num_col_idx].strip()
            num_match = re.search(r"[-+]?\d*\.?\d+", raw_val)
            if not num_match:
                continue
            try:
                val = float(num_match.group(0))
            except ValueError:
                continue

            # Identify if hero (e.g. contains "ours", or is first, or highest)
            is_hero = idx == 0 or any(k in name.lower() for k in ["ours", "flashattention-3", "deepseek-r1"])
            contestants.append(BenchmarkContestant(
                name=name[:24],
                value=val,
                raw_str=f"{val:,.1f} {unit}".strip(),
                is_hero=is_hero,
                color=palette[idx % len(palette)]
            ))

        if len(contestants) < 2:
            return None

        # Sort contestants
        contestants.sort(key=lambda c: c.value, reverse=higher_is_better)
        # Cap to top 4 contestants for clean 9:16 layout
        contestants = contestants[:4]

        # Ensure hero is marked
        hero_present = any(c.is_hero for c in contestants)
        if not hero_present:
            contestants[0].is_hero = True
            contestants[0].color = "#10B981"

        winner = contestants[0]
        runner_up = contestants[1]
        if higher_is_better and runner_up.value > 0:
            diff_pct = ((winner.value - runner_up.value) / runner_up.value) * 100
            delta_badge = f"⚡ +{diff_pct:.1f}% OVER {runner_up.name.upper()[:16]}"
        elif not higher_is_better and winner.value > 0:
            speedup = runner_up.value / winner.value
            delta_badge = f"⚡ {speedup:.2f}x FASTER THAN {runner_up.name.upper()[:16]}"
        else:
            delta_badge = f"⚡ SOTA LEAD BY {winner.name.upper()[:16]}"

        return BenchmarkComparison(
            title=f"BENCHMARK SHOWDOWN: {best_metric_name.upper()[:24]}",
            metric_name=best_metric_name,
            unit=unit,
            higher_is_better=higher_is_better,
            contestants=contestants,
            delta_badge=delta_badge
        )

    def extract_from_latex_source(self, source_dir: Path) -> Optional[BenchmarkComparison]:
        """Scans all .tex files in an extracted arXiv source directory for benchmark tables."""
        if not source_dir.exists():
            return None

        tex_files = list(source_dir.glob("*.tex")) + list(source_dir.glob("**/*.tex"))
        candidates: List[BenchmarkComparison] = []

        for tex_path in tex_files:
            try:
                content = tex_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # Find table environments
            table_matches = re.findall(r"\\begin\{(?:tabular|table|tabularx)\*?\}.*?\\end\{(?:tabular|table|tabularx)\*?\}", content, re.DOTALL)
            for tbl in table_matches:
                # Check for benchmark relevance
                tbl_lower = tbl.lower()
                if any(kw in tbl_lower for kw in self.BENCHMARK_KEYWORDS) and any(m in tbl_lower for m in self.MODEL_KEYWORDS):
                    parsed = self.parse_latex_table(tbl)
                    if parsed and len(parsed.contestants) >= 2:
                        candidates.append(parsed)

        if candidates:
            # Pick the candidate with highest contestant count or most relevant metric
            candidates.sort(key=lambda c: len(c.contestants), reverse=True)
            return candidates[0]

        return None

    def build_pareto_radar_data(
        self,
        contestants: List[BenchmarkContestant],
        axes: Optional[List[str]] = None
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Returns radar axes and radar models.

        A radar plot needs several metrics per model. Our sources (the spec's
        benchmark table or one parsed LaTeX table) only carry ONE metric, so there is
        no honest way to fill the other axes. We therefore return no radar models;
        callers fall back to race bars. (Previously this returned the same
        hard-coded 0.94/0.90/... profile for every paper.)
        """
        return list(axes or []), []

    def extract_verified(
        self,
        spec: Dict[str, Any],
        arxiv_id: Optional[str] = None
    ) -> Optional[BenchmarkComparison]:
        """
        Returns a benchmark comparison backed by real data, or None.

        Sources, in order:
          1. spec["benchmark_comparison"] (already filtered by pipeline.grounding so its
             numbers appear in the paper material the script was written from).
          2. A results table parsed from the paper's LaTeX source in public/arxiv_cache.

        There is deliberately no synthetic fallback: when neither source has numbers,
        callers must choose a non-numeric visual instead of inventing contestants.
        """
        # 1. Spec benchmark table
        b_data = spec.get("benchmark_comparison")
        if isinstance(b_data, dict):
            contestants: List[BenchmarkContestant] = []
            for c in b_data.get("contestants", []) or []:
                if not isinstance(c, dict):
                    continue
                try:
                    value = float(c.get("value"))
                except (TypeError, ValueError):
                    continue  # never default a missing value to an arbitrary bar length
                contestants.append(BenchmarkContestant(
                    name=str(c.get("name", "Model")),
                    value=value,
                    raw_str=c.get("display_val") or f"{c.get('value')} {b_data.get('unit', '')}".strip(),
                    is_hero=bool(c.get("is_hero", False)),
                    color=c.get("color", "#38BDF8")
                ))
            if len(contestants) >= 2:
                axes, radar_models = self.build_pareto_radar_data(contestants, b_data.get("radar_axes"))
                return BenchmarkComparison(
                    title=b_data.get("title") or f"BENCHMARK SHOWDOWN: {str(b_data.get('metric_name', 'RESULTS')).upper()[:24]}",
                    metric_name=b_data.get("metric_name", "Performance"),
                    unit=b_data.get("unit", ""),
                    higher_is_better=b_data.get("higher_is_better", True),
                    contestants=contestants,
                    delta_badge=b_data.get("delta_badge") or "",
                    radar_axes=axes,
                    radar_models=radar_models
                )

        # 2. LaTeX results table from the paper source
        clean_id = str(arxiv_id or spec.get("arxiv_id") or "").replace("arxiv_", "").strip()
        if clean_id:
            source_dir = PROJECT_ROOT / "public" / "arxiv_cache" / clean_id / "source"
            if source_dir.exists():
                parsed = self.extract_from_latex_source(source_dir)
                if parsed and len(parsed.contestants) >= 2:
                    axes, radar_models = self.build_pareto_radar_data(parsed.contestants)
                    parsed.radar_axes = axes
                    parsed.radar_models = radar_models
                    return parsed

        return None

    def extract_or_fallback(
        self,
        spec: Dict[str, Any],
        arxiv_id: Optional[str] = None
    ) -> Optional[BenchmarkComparison]:
        """
        Backwards-compatible name for extract_verified().

        NOTE: this no longer synthesizes a fallback. The old keyword-matched
        fallbacks (e.g. FlashAttention-3 H100 numbers for any title containing
        "flashattention", or a generic 94.2% vs 78.5% table) put fabricated numbers
        on screen, so callers now receive None when no verified data exists.
        """
        return self.extract_verified(spec, arxiv_id)
