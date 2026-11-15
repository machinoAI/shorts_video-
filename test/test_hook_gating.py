"""Tests for the Beat 1 hook gate (pipeline/hook_optimizer.optimize_script_hook)."""

from pipeline.hook_optimizer import (
    generate_hook_candidates,
    optimize_script_hook,
    resolve_subject_name,
    score_hook,
)

SCALING_META = {
    "title": "Scaling Laws for Neural Language Models",
    "abstract": (
        "We study empirical scaling laws for language model performance on the cross-entropy loss. "
        "The loss scales as a power-law with model size, dataset size, and the amount of compute used "
        "for training, with some trends spanning more than seven orders of magnitude."
    ),
}


def _spec(hook, title="Predicting the Billion-Dollar Graph", **extra):
    spec = {
        "id": "scaling_laws_prediction",
        "title": title,
        "category": "benchmark_news",
        "beats": [
            {"beat_id": 1, "text": hook},
            {"beat_id": 2, "text": "Researchers guess compute allocation without seeing the loss curve."},
        ],
    }
    spec.update(extra)
    return spec


def test_keeps_good_scriptwriter_hook_even_with_low_regex_score():
    hook = ("Training a massive language model is essentially betting millions on a power-law "
            "that remains invisible until completion.")
    assert score_hook(hook)["verdict"] < 50  # the old gate replaced this hook

    out = optimize_script_hook(_spec(hook), arxiv_meta=SCALING_META)
    assert out["beats"][0]["text"] == hook
    assert out["hook_gating"]["kept_bespoke"] is True


LEAKED_HOOK = "Why are leading AI teams switching to Predicting the Billion-Dollar Graph after this 98.2% benchmark result?"


def test_ungrounded_hook_is_replaced_using_paper_name_not_video_title():
    meta = dict(SCALING_META, title="Chinchilla: Training Compute-Optimal Large Language Models")
    out = optimize_script_hook(_spec(LEAKED_HOOK, metadata={"payoff_stat": "98.2%"}), arxiv_meta=meta)

    new_hook = out["beats"][0]["text"]
    assert "98.2" not in new_hook
    assert "Billion-Dollar Graph" not in new_hook
    assert out["hook_gating"]["kept_bespoke"] is False
    assert any(r.startswith("ungrounded_numbers") for r in out["hook_gating"]["rejection_reasons"])


def test_ungrounded_hook_without_replacement_is_flagged_for_review():
    # No short paper name and no usable abstract sentence -> nothing honest to swap in.
    out = optimize_script_hook(_spec(LEAKED_HOOK, metadata={"payoff_stat": "98.2%"}), arxiv_meta=SCALING_META)
    assert out["hook_gating"]["needs_review"] is True
    assert any(r.startswith("ungrounded_numbers") for r in out["hook_gating"]["rejection_reasons"])


def test_paper_hooks_do_not_splice_metadata_metrics():
    meta = {
        "title": "Denoising Diffusion Probabilistic Models",
        "abstract": "We present high quality image synthesis results using diffusion probabilistic models. "
                    "On CIFAR10 we obtain an FID score of 3.17.",
    }
    spec = _spec("In this paper we propose diffusion models for images.",
                 title="Toppling GANs: Diffusion Probabilistic Models",
                 metadata={"payoff_stat": "3.17"})
    spec["category"] = "multimodal_diffusion"
    out = optimize_script_hook(spec, arxiv_meta=meta)
    new_hook = out["beats"][0]["text"]
    assert "speedup" not in new_hook.lower()
    assert "Toppling GANs" not in new_hook
    assert not new_hook.lower().startswith("in this paper")


def test_resolve_subject_name_prefers_short_real_names():
    queue_meta = {
        "title": "Word2Vec: Semantic Vector Spaces: Part 4 - Crushing Word Analogy Benchmarks",
        "paper_title": "Efficient Estimation of Word Representations in Vector Space",
    }
    assert resolve_subject_name({"title": "Catchy Video Title"}, queue_meta) == "Word2Vec"
    assert resolve_subject_name({"title": "X"}, {"title": "FlashAttention: Fast and Memory-Efficient Exact Attention"}) == "FlashAttention"
    assert resolve_subject_name({"title": "X"}, SCALING_META) is None
    assert resolve_subject_name({"title": "X", "metadata": {"model_a": "RAPTOR"}}, SCALING_META) == "RAPTOR"


def test_no_name_templates_without_subject():
    cands = generate_hook_candidates(topic="Predicting the Billion-Dollar Graph", arxiv_meta=SCALING_META,
                                     category="benchmark_news", subject_name=None)
    assert all("Billion-Dollar" not in c for c in cands)
    assert all("  " not in c for c in cands)


def test_developer_perk_metric_templates_still_allowed():
    cands = generate_hook_candidates(
        topic="Anthropic Startup Program",
        metadata={"payoff_stat": "$25,000"},
        category="developer_perks",
    )
    assert any("$25,000" in c for c in cands)
