"""
Single-image processing using Pillow.
Used by the pipeline; supports resize (more ops in Phase 3).
"""

from pathlib import Path
from typing import Any, Dict, Union

from PIL import Image


def process_image(path_in: Union[str, Path], path_out: Union[str, Path], ops: Dict[str, Any]) -> None:
    """
    Load image from path_in, apply operations from ops, save to path_out.

    Args:
        path_in: Input image path.
        path_out: Output image path.
        ops: Dict of operations. Supported in Phase 1:
            - "resize": (width, height) or (width, height) with aspect ratio preserved
              via "resize_keep_aspect": True (default False for exact size).
    """
    path_in = Path(path_in)
    path_out = Path(path_out)
    path_out.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(path_in).convert("RGB")
    applied = False

    if "resize" in ops:
        size = ops["resize"]
        if isinstance(size, (list, tuple)) and len(size) >= 2:
            w, h = int(size[0]), int(size[1])
            if ops.get("resize_keep_aspect"):
                img.thumbnail((w, h), Image.Resampling.LANCZOS)
            else:
                img = img.resize((w, h), Image.Resampling.LANCZOS)
            applied = True

    if not applied:
        # No ops or unknown ops: save as-is (copy)
        pass

    img.save(path_out, quality=ops.get("quality", 95))


def create_test_image(path: Union[str, Path], width: int = 400, height: int = 300) -> Path:
    """Create a simple test image (gradient) for demos. Returns path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (width, height))
    px = img.load()
    for x in range(width):
        for y in range(height):
            px[x, y] = (x % 256, y % 256, (x + y) % 256)
    img.save(path)
    return path
