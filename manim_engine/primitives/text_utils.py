"""Manim-free text helpers (importable from the pipeline and tests without Manim)."""

_TRAILING_FILLER = {"a", "an", "the", "of", "for", "to", "and", "or", "in", "on", "with", "by", "is", "all", "&", "-", "—", ":", "/"}


def trim_words(text: str, max_chars: int) -> str:
    """
    Shortens a label at a word boundary instead of mid-word.
    "ATTENTION IS ALL YOU NEED ARCHITECTURE"[:18] gave "ATTENTION IS ALL Y";
    trim_words(..., 18) gives "ATTENTION".
    """
    s = " ".join(str(text or "").split())
    if len(s) <= max_chars:
        return s
    words = s.split(" ")
    out = ""
    for w in words:
        candidate = f"{out} {w}".strip()
        if len(candidate) > max_chars:
            break
        out = candidate
    if not out:  # a single very long word
        return s[:max_chars]
    parts = out.split(" ")
    while len(parts) > 1 and parts[-1].lower().strip(",.:;") in _TRAILING_FILLER:
        parts.pop()
    return " ".join(parts).rstrip(",:;-—/")
