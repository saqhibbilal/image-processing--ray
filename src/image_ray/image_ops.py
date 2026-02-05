"""
Single-image processing using Pillow.
Supports resize, compress (quality), format conversion, and basic filters (Phase 3).
"""

from pathlib import Path
from typing import Any, Dict, Union

from PIL import Image, ImageFilter, ImageOps


# Output format (key) -> file extension
FORMAT_EXT = {
    "jpeg": ".jpg",
    "jpg": ".jpg",
    "png": ".png",
    "webp": ".webp",
    "gif": ".gif",
    "bmp": ".bmp",
}


def _format_to_ext(fmt: str) -> str:
    """Return extension including dot, e.g. '.jpg' for 'jpeg'."""
    if not fmt:
        return ""
    key = fmt.strip().lower()
    return FORMAT_EXT.get(key, "." + key)


# Filter name -> Pillow filter
FILTERS = {
    "blur": ImageFilter.BLUR,
    "sharpen": ImageFilter.SHARPEN,
    "contour": ImageFilter.CONTOUR,
    "detail": ImageFilter.DETAIL,
    "edge_enhance": ImageFilter.EDGE_ENHANCE,
    "smooth": ImageFilter.SMOOTH,
    "smooth_more": ImageFilter.SMOOTH_MORE,
}


def _normalize_format(fmt: str) -> str:
    """Return normalized format for save (e.g. 'jpeg' for 'jpg')."""
    fmt = (fmt or "").strip().lower()
    if fmt in ("jpg", "jpeg"):
        return "JPEG"
    if fmt in ("png", "webp", "gif", "bmp"):
        return fmt.upper()
    return fmt.upper() if fmt else ""


def process_image(path_in: Union[str, Path], path_out: Union[str, Path], ops: Dict[str, Any]) -> None:
    """
    Load image from path_in, apply operations from ops, save to path_out.

    Args:
        path_in: Input image path.
        path_out: Output image path (extension may be overridden by ops['format']).
        ops: Dict of operations:
            - "resize": (width, height); "resize_keep_aspect": True for thumbnail.
            - "quality": int 1-100 for JPEG/WebP.
            - "format": "jpeg"|"png"|"webp"|... to convert output format.
            - "filter": "blur"|"sharpen"|"grayscale"|"contour"|"detail"|"edge_enhance"|"smooth"|"smooth_more".
    """
    path_in = Path(path_in)
    path_out = Path(path_out)
    path_out.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(path_in).convert("RGB")

    # Resize
    if "resize" in ops:
        size = ops["resize"]
        if isinstance(size, (list, tuple)) and len(size) >= 2:
            w, h = int(size[0]), int(size[1])
            if ops.get("resize_keep_aspect"):
                img.thumbnail((w, h), Image.Resampling.LANCZOS)
            else:
                img = img.resize((w, h), Image.Resampling.LANCZOS)

    # Filter
    filter_name = (ops.get("filter") or "").strip().lower()
    if filter_name == "grayscale":
        img = ImageOps.grayscale(img)
        img = img.convert("RGB")  # keep 3 channels for consistent save
    elif filter_name in FILTERS:
        img = img.filter(FILTERS[filter_name])

    # Output format and path
    fmt_key = (ops.get("format") or "").strip().lower()
    out_format = _normalize_format(ops.get("format") or "")
    if out_format:
        path_out = path_out.with_suffix(_format_to_ext(fmt_key or "png"))
    else:
        out_format = "JPEG" if path_out.suffix.lower() in (".jpg", ".jpeg") else "PNG"

    # Save
    quality = ops.get("quality", 95)
    save_kw = {"format": out_format}
    if out_format in ("JPEG", "WEBP"):
        save_kw["quality"] = quality
    img.save(path_out, **save_kw)


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
