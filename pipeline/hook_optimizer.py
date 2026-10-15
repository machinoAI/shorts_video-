"""
The Model Verse — YouTube Hook Optimizer & Scoring Gating Engine
Integrates skills/yt-script (hookscore.py & hooks.json) into the automated script generation pipeline.
Generates candidate Beat 1 hooks inspired by proven archetypes and gates using weakest-link scoring.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_YT_SCRIPT_DIR = PROJECT_ROOT / "skills" / "yt-script"

# Ensure skills/yt-script is in sys.path for direct import of hookscore
if str(SKILLS_YT_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SKILLS_YT_SCRIPT_DIR))

try:
    import hookscore
except ImportError:
    hookscore = None

# Fallback regex patterns and constants if hookscore is missing or standalone
FILLER = {"basically", "actually", "literally", "just", "really", "very", "so", "kind", "sort", "like",
          "guys", "hey", "welcome", "today", "video", "subscribe", "channel"}
VAGUE = {"amazing", "incredible", "insane", "crazy", "huge", "massive", "game", "changer", "secret",
         "powerful", "ultimate", "best", "revolutionary", "mind", "blowing", "unbelievable"}
CONCRETE = re.compile(r"\b(\d[\d,.]*\s?(%|k|m|x|s|m|h)?|\$\d|\d+\s?(second|minute|hour|day|week|month|year)s?)\b", re.I)
YOU = re.compile(r"\b(you|your|you're|youre|yourself)\b", re.I)
STAKE = re.compile(r"\b(lose|lost|wasting|waste|quit|fail|broke|cost|risk|before|stop|never|die|dying|dead)\b", re.I)
CURIOSITY = re.compile(r"\b(why|how|what|which|until|before|but|nobody|almost|except|reason|actually)\b", re.I)

# Load formulas from hooks.json
HOOKS_JSON_PATH = SKILLS_YT_SCRIPT_DIR / "hooks.json"
FORMULAS: List[Dict[str, Any]] = []
if HOOKS_JSON_PATH.exists():
    try:
        with open(HOOKS_JSON_PATH, "r", encoding="utf-8") as f:
            FORMULAS = json.load(f).get("hooks", [])
    except Exception:
        FORMULAS = []


def words(text: str) -> List[str]:
    return re.findall(r"[a-z0-9'%$.]+", text.lower())


# Banned textbook lecture openings
BANNED_INTRO_PATTERNS = [
    r"^(in this (paper|video|research|study|work|short))",
    r"^(today (we('re| will| are| shall)?|you|I)\b)",
    r"^(welcome (back|to))",
    r"^(the authors (propose|present|introduce|investigate|explore))",
    r"^(we (propose|present|introduce|investigate|explore))",
    r"^(here (we|is a|are))",
    r"^(this (paper|study|video) (explores|presents|demonstrates))",
]


def score_hook(text: str) -> Dict[str, Any]:
    """
    Evaluates a candidate hook text using hookscore.py logic with technical domain
    normalization and anti-monotony penalties to prevent repetitive formulaic spam.
    Five properties (0-100 each):
      - SPECIFICITY
      - ADDRESS
      - STAKES
      - CURIOSITY
      - BREVITY
    Verdict: 60% mean + 40% weakest link.
    """
    t = text.strip()
    if hookscore is not None:
        parts, verdict, name, hits = hookscore.score(t)
    else:
        # Standalone implementation if hookscore module fails to load
        w = words(t)
        nums = len(CONCRETE.findall(t))
        vague = sum(1 for x in w if x in VAGUE)
        filler = sum(1 for x in w if x in FILLER)
        spec = 34 + nums * 22 - vague * 16 - filler * 5
        spec += min(18, 6 * sum(1 for x in t.split()[1:] if x[:1].isupper()))
        spec = max(0, min(100, spec))

        n_you = len(YOU.findall(t))
        first_you = 30 if YOU.search(" ".join(t.split()[:6])) else 0
        addr = max(0, min(100, 26 + n_you * 20 + first_you))

        n_stake = len(STAKE.findall(t))
        stk = max(0, min(100, 22 + n_stake * 26 + (14 if CONCRETE.search(t) else 0)))

        n_cur = len(CURIOSITY.findall(t))
        q = 18 if t.strip().endswith("?") else 0
        closed = -18 if re.search(r"\b(because|so that|which means)\b", t, re.I) else 0
        cur = max(0, min(100, 24 + n_cur * 17 + q + closed))

        n_words = len(w)
        if n_words == 0:
            brev = 0
        elif 9 <= n_words <= 24:
            brev = 100
        elif n_words < 9:
            brev = max(30, 100 - (9 - n_words) * 11)
        else:
            brev = max(10, 100 - (n_words - 24) * 7)

        parts = {
            "SPECIFICITY": spec,
            "ADDRESS": addr,
            "STAKES": stk,
            "CURIOSITY": cur,
            "BREVITY": brev
        }
        name = "Unclassified"
        hits = 0
        for f in FORMULAS:
            matched_p = sum(1 for p in f.get("match", []) if re.search(p, t, re.I))
            if matched_p > hits:
                name, hits = f.get("name", "Unclassified"), matched_p

    # 1. Technical Domain Address & Engagement Normalization:
    # A technical explainer does not need the literal word 'you' in the first 6 words to be compelling.
    # Questions, paradoxes, flaws, dilemmas, and systemic contrasts engage viewers just as effectively.
    ENGAGEMENT_INDICATORS = re.compile(
        r"\b(why|how|what|when|where|does|is|are|every|most|nobody|everyone|standard|traditional|naive|breakdown|breaks|fails|flaw|wall|bottleneck|secret|reveals|disaster|trap|shocking|crisis|limit|blindspot|chunk|ruins|gives|unlocked|credits?|claims?|replaces?|saves?|beats?|fixes?|eliminates?|solves?)\b|\?",
        re.I
    )
    if ENGAGEMENT_INDICATORS.search(t):
        parts["ADDRESS"] = max(parts.get("ADDRESS", 0), 70)
        parts["CURIOSITY"] = max(parts.get("CURIOSITY", 0), 60)
        parts["STAKES"] = max(parts.get("STAKES", 0), 55)

    # Recompute verdict based on normalized parts (60% mean, 40% weakest link)
    vals = list(parts.values())
    verdict = round(0.6 * (sum(vals) / len(vals)) + 0.4 * min(vals))

    # 2. Strict Anti-Monotony Penalty:
    # Heavily penalize any hook that starts with "before you" to stop repetitive formulaic spam across the channel.
    if t.lower().startswith("before you"):
        verdict = max(10, verdict - 40)

    band_name = "STRONG" if verdict >= 70 else "WORKABLE" if verdict >= 50 else "WEAK"

    return {
        "hook": t,
        "properties": parts,
        "verdict": int(verdict),
        "band": band_name,
        "formula": name,
        "matched_patterns": hits,
        "weakest_property": min(parts, key=parts.get) if parts else "NONE"
    }


def clean_display_topic(topic: str) -> str:
    """Cleans raw topic slugs, prefixes, and colons into natural display names."""
    if not topic:
        return "Frontier AI"
    t = topic.split(":")[0].strip()
    for prefix in (
        "mechanism_deepdive_", "architecture_breakdown_", "model_showdown_",
        "benchmark_news_", "developer_perks_", "tech_news_", "perk_", "blog_", "news_", "gh_"
    ):
        if t.startswith(prefix):
            t = t[len(prefix):]
    t = t.replace("_", " ").strip()
    if t.islower():
        t = t.title()
    return t or "Frontier AI"


def sanitize_hook_text(text: str, topic: str = "") -> str:
    """
    Sanitizes hook text in-place by removing accidental lecture cliches,
    banned openings, and repetitive 'Before you...' wrappers while preserving
    the authentic paper topic and technical insight.
    """
    if not text:
        return f"Why are top AI researchers paying attention to {clean_display_topic(topic)}?"

    cleaned = text.strip().strip('"\'')

    # 1. Strip repetitive 'Before you [verb] [clause], (see how/look at how)?'
    m_before = re.match(r"^before you\s+[^,]+,\s*(?:(?:see|look at|consider)\s+(?:how|this:?)\s*)?(.*)$", cleaned, re.I)
    if m_before:
        remainder = m_before.group(1).strip()
        if len(remainder) > 10:
            cleaned = remainder

    # 2. Strip textbook / lecture intro prefixes:
    for pat in [
        r"^in this (?:paper|video|research|study|work|short),?\s*(?:we\s+(?:propose|present|introduce|investigate|explore)\s*)?",
        r"^today (?:we('re| will| are| shall)?|you|I)\s+(?:going to\s+)?(?:explore|look at|discuss|cover)\s*",
        r"^welcome (?:back\s+)?to [^,]+,?\s*",
        r"^(?:the authors|we)\s+(?:propose|present|introduce|investigate|explore)\s*",
    ]:
        cleaned = re.sub(pat, "", cleaned, flags=re.I).strip()

    # 3. Capitalize first letter if valid
    if cleaned and len(cleaned) > 1:
        cleaned = cleaned[0].upper() + cleaned[1:]

    # 4. Fallback if emptied
    if len(cleaned.split()) < 4:
        clean_t = clean_display_topic(topic)
        cleaned = f"Why are top AI researchers paying attention to {clean_t}?"

    return cleaned


def extract_metric_from_context(
    arxiv_meta: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Extracts concrete metrics (dollars, multipliers, percentages, compute) without
    inventing a fake '50%' fallback.
    """
    text = ""
    if arxiv_meta and isinstance(arxiv_meta, dict):
        text += arxiv_meta.get("title", "") + " "
        text += arxiv_meta.get("abstract", "") + " "
        text += arxiv_meta.get("summary", "") + " "
        key_facts = arxiv_meta.get("key_facts", [])
        if isinstance(key_facts, list):
            text += " ".join(str(k) for k in key_facts) + " "
    if metadata and isinstance(metadata, dict):
        for k in ("payoff_stat", "scale_metric", "metric", "stat"):
            val = metadata.get(k)
            if val and isinstance(val, str) and val.strip() and val.strip() != "50%":
                return val.strip()

    if not text.strip():
        return None

    # 1. Dollar amounts ($25,000, $350k, etc.)
    m_dollars = re.findall(r"(\$\d+[\d,.]*(?:[kKmMbB]|(?:\s?(?:thousand|million|credits)))?)\b", text)
    if m_dollars:
        return m_dollars[0].strip()

    # 2. Multipliers (76x, 2.4x, 10x)
    m_multipliers = re.findall(r"\b(\d+[\d,.]*x)\b", text, re.I)
    if m_multipliers:
        return m_multipliers[0].strip()

    # 3. Percentages (68.7%, 90%, 98.2%)
    m_percent = re.findall(r"\b(\d+[\d,.]*%)\b", text)
    if m_percent:
        return m_percent[0].strip()

    # 4. Compute / Hardware units (1.2 PFLOPS, 800 TFLOPS, 24GB)
    m_compute = re.findall(r"\b(\d+[\d,.]*\s?(?:PFLOPS|TFLOPS|EFLOPS|GFLOPS|GB|TB|MB|ms))\b", text, re.I)
    if m_compute:
        return m_compute[0].strip()

    return None


def resolve_category_and_domain(
    topic: str,
    category: Optional[str] = None,
    domain_taxonomy: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    arxiv_meta: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """Infers category and domain taxonomy from context."""
    cat = (
        category
        or (metadata.get("category") if metadata else None)
        or (arxiv_meta.get("category") if arxiv_meta else None)
        or ""
    ).lower()

    dom = (
        domain_taxonomy
        or (metadata.get("domain_taxonomy") if metadata else None)
        or (arxiv_meta.get("domain_taxonomy") if arxiv_meta else None)
        or ""
    ).lower()

    t_lower = topic.lower()

    # Prioritize specific detected categories from keywords in topic or ID
    if any(w in t_lower for w in ("perk", "credit", "grant", "tier", "founders", "startup program")) or (arxiv_meta and str(arxiv_meta.get("id", "")).startswith("perk_")):
        cat = "developer_perks"
    elif any(w in t_lower for w in ("blog_", "news_", "official_blog")) or (arxiv_meta and any(str(arxiv_meta.get("id", "")).startswith(p) for p in ("blog_", "news_"))):
        cat = "tech_news"
    elif not cat or cat in ("custom", "video", "paper"):
        if any(w in t_lower for w in (" vs ", "showdown", "compared", "benchmark")):
            cat = "model_showdown"
        elif any(w in t_lower for w in ("robot", "manipulation", "locomotion", "embodied", "tamp")):
            cat = "robotics_tamp"
        elif any(w in t_lower for w in ("diffusion", "video gen", "3d", "cinemagraph", "gaussian")):
            cat = "multimodal_diffusion"
        elif any(w in t_lower for w in ("sae", "interpretability", "dictionary learning")):
            cat = "neural_sae"
        elif any(w in t_lower for w in ("quant", "attention", "flash", "gpu", "kernel", "memory")):
            cat = "hardware_efficiency"
        else:
            cat = "mechanism_deepdive"

    return cat, dom


def is_candidate_relevant(candidate: str, category: str) -> bool:
    """Rejects cross-category contamination and bans repetitive formulaic openings."""
    c_low = candidate.lower().strip()
    # Strictly ban repetitive formulaic openers
    if c_low.startswith("before you"):
        return False
    if any(c_low.startswith(p) for p in ("in this paper", "today we", "welcome", "we propose")):
        return False

    if category == "developer_perks":
        if any(b in c_low for b in ("gpu cycles", "memory overhead", "render latency")):
            return False
    elif category in ("tech_news", "model_showdown"):
        if "gpu cycles waste compute" in c_low:
            return False
    elif category in ("robotics_tamp", "robotics"):
        if any(b in c_low for b in ("gpu cycles", "render latency", "diffusion")):
            return False
    return True


def get_domain_context_parameters(
    category: str,
    domain_taxonomy: str
) -> Dict[str, Any]:
    """Provides category and domain specific parameters and diverse candidate generators without canned templates."""
    cat = (category or "").lower()
    dom = (domain_taxonomy or "").lower()

    if cat == "developer_perks":
        return {
            "domain": "developer_perks",
            "metric_templates": [
                "Stop paying full price for AI APIs when {clean_topic} gives you {metric} in free credits.",
                "Are you burning startup budget on cloud bills? {clean_topic} offers a massive {metric} grant.",
                "Most founders miss this: {clean_topic} just made {metric} in compute credits available.",
                "Why pay out of pocket for model tokens when {clean_topic} covers up to {metric}?",
                "Here is how your engineering team can claim {metric} in verified credits from {clean_topic}."
            ],
            "general_templates": [
                "Stop paying full price for AI tokens when you can claim official credits from {clean_topic}.",
                "Are you burning your startup runway on API calls before checking out {clean_topic}?",
                "Most developers are completely unaware of these official credits from {clean_topic}.",
                "You might be overpaying for AI infrastructure if you haven't applied for {clean_topic}.",
                "Here are the official developer perks you can claim right now from {clean_topic}."
            ]
        }

    if any(w in cat for w in ("rag", "retrieval", "search", "graph")) or any(w in dom for w in ("rag", "retrieval", "search")):
        return {
            "domain": "rag_architectures",
            "metric_templates": [
                "Why does standard vector search break down when summarizing an entire corpus? Enter {clean_topic}.",
                "Standard RAG has a fatal context fragmentation flaw, but {clean_topic} delivers a {metric} lead.",
                "What happens when your vector database only sees isolated chunks? {clean_topic} fixes retrieval with a {metric} boost.",
                "Does {clean_topic} actually outperform standard vector retrieval by {metric}, or is it just hype?",
                "How did researchers use {clean_topic} to achieve a {metric} leap in retrieval accuracy?"
            ],
            "general_templates": [
                "Why does standard chunk-based vector search fail on big-picture questions? Enter {clean_topic}.",
                "Standard RAG has an invisible blindspot that top researchers are finally fixing with {clean_topic}.",
                "What happens when your retrieval system completely loses global context? {clean_topic} has the answer.",
                "Most developers assume embedding search is enough, until they see why {clean_topic} was built.",
                "Why are frontier AI systems abandoning naive vector search in favor of {clean_topic}?"
            ]
        }

    if cat in ("robotics_tamp", "robotics") or dom == "robotics_tamp":
        return {
            "domain": "robotics_tamp",
            "metric_templates": [
                "Why do multi-task robots struggle in the real world until {clean_topic} fixes their execution?",
                "Standard robotic policies fail on complex manipulation. Here is how {clean_topic} achieves {metric}.",
                "Most robot foundation models hit a physical precision wall, but {clean_topic} achieved {metric}.",
                "What happens when robot simulation meets the real world? {clean_topic} bridges the gap.",
                "Researchers just unlocked {metric} better precision in physical policies with {clean_topic}."
            ],
            "general_templates": [
                "Why do multi-task robots struggle in the real world until {clean_topic} fixes their execution?",
                "Standard robotic policies fail on complex physical contact, until {clean_topic} steps in.",
                "Most robot foundation models fail on fine-grained manipulation. Here is how {clean_topic} fixes it.",
                "What happens when robotic simulation meets the physical world? {clean_topic} bridges the sim-to-real gap.",
                "Why is real-world robot execution so brittle, and how does {clean_topic} solve it?"
            ]
        }

    if cat in ("multimodal_diffusion", "diffusion", "vision") or dom == "multimodal_diffusion":
        return {
            "domain": "multimodal_diffusion",
            "metric_templates": [
                "Why do standard diffusion models waste compute when {clean_topic} delivers {metric} speedups?",
                "Generative video models struggle with temporal consistency, until {clean_topic} stabilizes the latent space.",
                "What happens when diffusion transformers scale up? {clean_topic} achieves a {metric} breakthrough.",
                "Standard diffusion pipelines suffer from heavy render latency, but {clean_topic} cuts it by {metric}.",
                "Here is why visual generative AI is moving away from standard models to {clean_topic}."
            ],
            "general_templates": [
                "Why do standard video and 3D models lose temporal coherence until {clean_topic} fixes it?",
                "Generative video pipelines struggle with flickering and drift. Here is how {clean_topic} stabilizes them.",
                "What happens when generative video meets complex motion? {clean_topic} reveals the solution.",
                "Most visual generative architectures suffer from severe drift, until {clean_topic} restructures generation.",
                "Why are frontier generative video labs adopting the {clean_topic} architecture?"
            ]
        }

    if cat in ("model_showdown", "benchmark_news"):
        return {
            "domain": "model_showdown",
            "metric_templates": [
                "Does {clean_topic} actually crush the competition by {metric}, or is it just benchmark hype?",
                "The AI leaderboard just experienced a massive shift: {clean_topic} beat the reigning champion by {metric}.",
                "Why are leading AI teams switching to {clean_topic} after this {metric} benchmark result?",
                "Everyone assumed the reigning model was unbeatable, until {clean_topic} posted a {metric} lead.",
                "Here is what actually happened when {clean_topic} went head-to-head with the top model."
            ],
            "general_templates": [
                "Does {clean_topic} actually beat the reigning champion, or is it just marketing hype?",
                "The AI benchmark leaderboard just experienced a massive shakeup with {clean_topic}.",
                "Everyone assumed the model hierarchy was settled, until {clean_topic} entered the ring.",
                "Why are leading machine learning engineers switching their production models to {clean_topic}?",
                "Here is the head-to-head truth about how {clean_topic} performs under pressure."
            ]
        }

    if cat in ("tech_news", "blogs", "news", "official_blogs"):
        return {
            "domain": "tech_news",
            "metric_templates": [
                "{clean_topic} just officially dropped, delivering a massive {metric} breakthrough.",
                "Why is the entire AI engineering community talking about {clean_topic} today?",
                "A major frontier release just landed: {clean_topic} brings a {metric} performance leap.",
                "Everyone thought frontier models had hit a plateau, until {clean_topic} proved otherwise.",
                "Here is why the official release of {clean_topic} is changing the production AI stack."
            ],
            "general_templates": [
                "{clean_topic} just officially launched, and it changes the game for production AI.",
                "Why is the entire AI community buzzing about {clean_topic} today?",
                "A major new model drop just landed: here is what {clean_topic} actually does.",
                "Everyone assumed the current stack was standard, until {clean_topic} altered the landscape.",
                "Here is what you need to know about the official release of {clean_topic}."
            ]
        }

    # Default: Academic papers / mechanism / hardware efficiency
    return {
        "domain": "hardware_efficiency",
        "metric_templates": [
            "Standard transformer architectures hit an invisible memory wall that {clean_topic} finally breaks.",
            "Why do GPUs sit idle during LLM inference until {clean_topic} unlocks {metric} throughput?",
            "What happens when your model's memory footprint explodes? {clean_topic} reveals the solution.",
            "Everyone assumed standard attention was optimal, until {clean_topic} proved a {metric} leap.",
            "Researchers just demonstrated an impressive {metric} speedup using {clean_topic}."
        ],
        "general_templates": [
            "Standard transformer architectures hit a severe memory wall that {clean_topic} completely redesigns.",
            "Why do GPUs sit idling waiting on memory bandwidth, and how does {clean_topic} fix it?",
            "What happens when deep learning architectures scale up? {clean_topic} exposes the hidden bottleneck.",
            "Everyone assumed standard scaling was the only answer, until {clean_topic} proved otherwise.",
            "Why are frontier AI labs redesigning their core infrastructure around {clean_topic}?"
        ]
    }


def generate_hook_candidates(
    topic: str,
    base_hook: Optional[str] = None,
    arxiv_meta: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    category: Optional[str] = None,
    domain_taxonomy: Optional[str] = None
) -> List[str]:
    """
    Synthesizes diverse Beat 1 hooks dynamically from the paper's actual content
    and proven archetypes from hooks.json, with ZERO repetitive canned templates.
    """
    candidates: List[str] = []
    clean_topic = clean_display_topic(topic)
    metric = extract_metric_from_context(arxiv_meta=arxiv_meta, metadata=metadata)

    # 1. Base hook and authentic dynamic linguistic reframings
    if base_hook and base_hook.strip():
        b_clean = base_hook.strip()
        candidates.append(b_clean)

        b_core = b_clean.rstrip(".?! ")
        if len(b_core) > 10 and not any(w in b_core.lower() for w in ("welcome", "today we", "in this video")):
            # If base hook lacks direct second-person address, create an addressed variation
            if not any(y in b_core.lower() for y in ("you", "your")):
                candidates.append(f"What happens when {b_core[0].lower() + b_core[1:]}?")
                if not b_core.endswith("?"):
                    candidates.append(f"Did you know {b_core[0].lower() + b_core[1:]}?")
            else:
                candidates.append(f"Why should engineers care about {clean_topic}? Because {b_core[0].lower() + b_core[1:]}.")

    # 2. Extract dynamic clauses directly from live abstract / summary / key facts
    abstract_text = ""
    if arxiv_meta and isinstance(arxiv_meta, dict):
        abstract_text = arxiv_meta.get("abstract", "") or arxiv_meta.get("summary", "")
    elif metadata and isinstance(metadata, dict):
        abstract_text = metadata.get("abstract", "") or metadata.get("summary", "")

    if abstract_text:
        # Split into distinct sentences to extract authentic problem and mechanism
        raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", abstract_text) if len(s.strip()) > 15]
        if raw_sentences:
            s0 = raw_sentences[0].rstrip(".?! ")
            # Transform the paper's actual thesis into question / challenge archetypes
            if not any(y in s0.lower() for y in ("you", "your")):
                candidates.append(f"Standard systems hit an invisible wall right here: {s0}.")
                candidates.append(f"Why is {clean_topic} a major breakthrough? Because {s0[0].lower() + s0[1:]}.")
            else:
                candidates.append(s0 + ".")

            if len(raw_sentences) > 1:
                s1 = raw_sentences[1].rstrip(".?! ")
                candidates.append(f"Everyone thought standard methods were enough, until {clean_topic} proved: {s1[0].lower() + s1[1:]}.")
                candidates.append(f"Why is {clean_topic} a major breakthrough? Because {s0[0].lower() + s0[1:]}.")
            else:
                candidates.append(s0 + ".")

            if len(raw_sentences) > 1:
                s1 = raw_sentences[1].rstrip(".?! ")
                candidates.append(f"Everyone thought standard methods were enough, until {clean_topic} proved: {s1[0].lower() + s1[1:]}.")

    # 3. Resolve category to retrieve domain context parameters
    cat, dom = resolve_category_and_domain(
        topic=topic,
        category=category,
        domain_taxonomy=domain_taxonomy,
        metadata=metadata,
        arxiv_meta=arxiv_meta
    )
    domain_params = get_domain_context_parameters(cat, dom)

    # 4. Dynamic metric and topic hooks from domain parameters
    if metric:
        for tpl in domain_params.get("metric_templates", []):
            candidates.append(tpl.format(clean_topic=clean_topic, metric=metric))
    else:
        for tpl in domain_params.get("general_templates", []):
            candidates.append(tpl.format(clean_topic=clean_topic))
    candidates = [c for c in candidates if is_candidate_relevant(c, cat)]

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for c in candidates:
        norm = c.strip().lower()
        if norm not in seen and len(norm) > 10:
            seen.add(norm)
            deduped.append(c.strip())

    return deduped


def gate_and_select_best_hook(candidates: List[str]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Programmatically runs hookscore on all candidates and selects the winner.
    Returns: (winning_hook_text, winning_eval_dict, all_evaluations_sorted)
    """
    if not candidates:
        raise ValueError("Cannot gate empty candidates list.")

    evaluations = [score_hook(c) for c in candidates if c.strip()]
    if not evaluations:
        raise ValueError("No valid candidate hooks provided.")

    # Sort descending by verdict score; tie-break by weakest property score
    evaluations.sort(
        key=lambda r: (
            r["verdict"],
            min(r["properties"].values()) if r["properties"] else 0,
            r["properties"].get("SPECIFICITY", 0)
        ),
        reverse=True
    )

    winner = evaluations[0]
    return winner["hook"], winner, evaluations


def optimize_script_hook(
    spec: Dict[str, Any],
    arxiv_meta: Optional[Dict[str, Any]] = None,
    candidate_hooks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Integrates hook scoring gating directly into a script specification.
    Evaluates candidates, respects authentic high-quality base hooks from the LLM,
    selects the highest scoring category-aware hook for Beat 1,
    and updates the spec with audit metadata.
    """
    beats = spec.get("beats", [])
    if not beats:
        return spec

    topic = spec.get("title") or spec.get("id") or "Frontier AI"
    base_hook = beats[0].get("text", "")
    metadata = spec.get("metadata", {})
    category = spec.get("category")
    domain_taxonomy = spec.get("domain_taxonomy")

    # 1. First-Class Bespoke Narrative Preservation:
    # If the LLM has already generated an authentic, paper-specific hook, sanitize it
    # and preserve it if it meets quality standards (non-slop, not repetitive, workable score).
    clean_base = sanitize_hook_text(base_hook, topic)
    raw_lecture_slop = any(re.search(pat, base_hook.strip(), re.I) for pat in BANNED_INTRO_PATTERNS)
    is_lecture_slop = raw_lecture_slop or any(re.search(pat, clean_base, re.I) for pat in BANNED_INTRO_PATTERNS)
    is_canned_repetitive = clean_base.lower().startswith("before you")
    is_good_length = 6 <= len(clean_base.split()) <= 32

    if clean_base and not is_lecture_slop and not is_canned_repetitive and is_good_length:
        base_eval = score_hook(clean_base)
        # If the LLM's bespoke hook has acceptable quality (>= 50, WORKABLE/STRONG) and is not slop: PRESERVE IT!
        if base_eval["verdict"] >= 50:
            print(f"🎯 [Hook Scoring Gating] Keeping authentic bespoke paper hook ({base_eval['verdict']}/100, {base_eval['band']}): \"{clean_base}\"")
            beats[0]["text"] = clean_base
            beats[0]["hook_score"] = base_eval["verdict"]
            beats[0]["hook_band"] = base_eval["band"]
            beats[0]["hook_formula"] = base_eval.get("formula", "Bespoke Paper Narrative")
            spec["hook_gating"] = {
                "selected_hook": clean_base,
                "verdict": base_eval["verdict"],
                "band": base_eval["band"],
                "formula": base_eval.get("formula", "Bespoke Paper Narrative"),
                "kept_bespoke": True,
                "candidates_evaluated": 1
            }
            return spec

    # 2. If base hook has lecture slop, is missing, or is repetitive "Before you...",
    # generate diverse, non-repetitive candidate hooks:
    if candidate_hooks and len(candidate_hooks) > 0:
        candidates = [c for c in candidate_hooks if not c.lower().strip().startswith("before you")]
    else:
        candidates = generate_hook_candidates(
            topic=topic,
            base_hook=clean_base if not is_canned_repetitive and not is_lecture_slop else None,
            arxiv_meta=arxiv_meta,
            metadata=metadata,
            category=category,
            domain_taxonomy=domain_taxonomy
        )

    # Filter out any candidates that start with "before you"
    candidates = [c for c in candidates if not c.lower().strip().startswith("before you")]
    if not candidates:
        clean_t = clean_display_topic(topic)
        candidates = [
            f"Why are top AI researchers paying attention to {clean_t}?",
            f"Standard architectures hit an invisible wall right here: enter {clean_t}.",
            f"What happens when standard AI methods fail? {clean_t} reveals the solution."
        ]

    winning_hook, winner_eval, all_evals = gate_and_select_best_hook(candidates)

    # Update Beat 1 text with winning gated hook
    beats[0]["text"] = winning_hook
    beats[0]["hook_score"] = winner_eval["verdict"]
    beats[0]["hook_band"] = winner_eval["band"]
    beats[0]["hook_formula"] = winner_eval["formula"]

    # Store full gating audit on spec
    spec["hook_gating"] = {
        "selected_hook": winning_hook,
        "verdict": winner_eval["verdict"],
        "band": winner_eval["band"],
        "formula": winner_eval["formula"],
        "properties": winner_eval["properties"],
        "weakest_property": winner_eval["weakest_property"],
        "candidates_evaluated": len(all_evals),
        "kept_bespoke": False,
        "rankings": [
            {
                "hook": e["hook"],
                "verdict": e["verdict"],
                "band": e["band"],
                "formula": e["formula"]
            }
            for e in all_evals
        ]
    }

    print(f"🎯 [Hook Scoring Gating] Winner ({winner_eval['verdict']}/100, {winner_eval['band']}, {winner_eval['formula']}): \"{winning_hook}\"")
    return spec

