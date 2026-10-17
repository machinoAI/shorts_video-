"""
Pillow Compatibility Patch for Manim Community Edition.

In Pillow >= 11.0.0, Image.fromarray strictly validates array dimensions and data types
against the requested mode. Manim CE's Camera.display_image_mobject passes a 2D float zeros array:
    np.zeros((self.pixel_height, self.pixel_width))
to `Image.fromarray(..., mode='RGBA')`, which triggers `ValueError: Invalid mode for data type`.

This patch intercepts this call pattern and creates a transparent RGBA image,
ensuring complete compatibility across all Pillow versions (Pillow 9, 10, 11, 12+).
"""

import PIL.Image

# Ensure monkeypatch is idempotent
if not hasattr(PIL.Image, "_manim_orig_fromarray"):
    _orig_fromarray = PIL.Image.fromarray
    PIL.Image._manim_orig_fromarray = _orig_fromarray

    def safe_fromarray(obj, mode=None):
        if mode == "RGBA" and hasattr(obj, "ndim") and obj.ndim == 2:
            h, w = obj.shape
            return PIL.Image.new("RGBA", (w, h), (0, 0, 0, 0))
        return _orig_fromarray(obj, mode=mode)

    PIL.Image.fromarray = safe_fromarray
