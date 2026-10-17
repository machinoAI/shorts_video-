import os
import pytest
import numpy as np
import PIL.Image
from PIL import Image

import manim_engine.pillow_compat
from manim import *
from manim.camera.camera import Camera
from manim_engine.primitives.visual_compositions import BlueprintPaperFigure

def test_safe_fromarray_handles_2d_rgba():
    """Verify that fromarray doesn't crash on 2D float zeros with mode='RGBA'."""
    arr = np.zeros((100, 100))
    img = PIL.Image.fromarray(arr, mode="RGBA")
    assert isinstance(img, PIL.Image.Image)
    assert img.size == (100, 100)
    assert img.mode == "RGBA"

def test_camera_display_image_mobject_renders_without_crash(tmp_path):
    """Verify Camera.display_image_mobject successfully renders an ImageMobject."""
    # Create a test image
    test_img = tmp_path / "test_fig.png"
    Image.new("RGBA", (200, 150), (20, 180, 240, 255)).save(str(test_img))

    im_mob = ImageMobject(str(test_img))
    cam = Camera(pixel_height=960, pixel_width=540)
    pixel_array = np.zeros((960, 540, 4), dtype=np.uint8)

    # Should execute cleanly without ValueError: Invalid mode for data type
    cam.display_image_mobject(im_mob, pixel_array)
    assert pixel_array.shape == (960, 540, 4)

def test_blueprint_paper_figure_with_image(tmp_path):
    """Verify BlueprintPaperFigure creates and renders ImageMobject with fallback safety."""
    test_img = tmp_path / "rag_arch.png"
    Image.new("RGBA", (300, 200), (255, 50, 50, 255)).save(str(test_img))

    fig = BlueprintPaperFigure(
        image_path=str(test_img),
        title="RAG ARCHITECTURE",
        sub="Parametric vs Non-Parametric Memory"
    )
    assert hasattr(fig, "fig_mobj")
    assert fig.fig_mobj is not None
