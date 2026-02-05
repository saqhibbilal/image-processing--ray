"""
Image-Ray: Parallel image processing pipeline with Ray.

Phase 1: Single-image processing
Phase 2: Batch processing (parallel pipeline)
Phase 3: Full operations (resize, quality, format, filter) and CLI.

Usage:
  # Single image
  python main.py --input a.png --output b.png --resize 800x600 --format jpeg --quality 85

  # Batch processing
  python main.py --batch --input-dir ./images --output-dir ./output --resize 800x600 --format jpeg --filter grayscale

  # Default batch output is ./output if --output-dir omitted
  python main.py --batch --input-dir ./images --resize 400x300
"""

import argparse
import sys
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from image_ray import image_ops
from image_ray import pipeline
from image_ray import ray_check

FILTER_CHOICES = [
    "blur", "sharpen", "grayscale", "contour", "detail", "edge_enhance", "smooth", "smooth_more"
]


def parse_resize(resize_str: str) -> tuple:
    """Parse resize string like '800x600' into (width, height)."""
    try:
        w, h = resize_str.lower().split("x")
        return (int(w), int(h))
    except ValueError:
        print("Error: --resize must be in format WxH (e.g. 800x600)")
        sys.exit(1)


def build_ops(args: argparse.Namespace) -> dict:
    """Build ops dict from CLI args for image_ops.process_image."""
    ops = {
        "resize": parse_resize(args.resize),
        "resize_keep_aspect": getattr(args, "resize_keep_aspect", False),
        "quality": args.quality,
    }
    if args.format:
        ops["format"] = args.format
    if args.filter:
        ops["filter"] = args.filter
    return ops


def main():
    parser = argparse.ArgumentParser(description="Image-Ray: Parallel image processing with Ray")
    parser.add_argument("--input", "-i", help="Input image path (single-image mode)")
    parser.add_argument("--output", "-o", help="Output image path (single-image mode)")
    parser.add_argument("--input-dir", help="Input directory (batch mode)")
    parser.add_argument("--output-dir", help="Output directory (batch mode; default: ./output)")
    parser.add_argument("--batch", action="store_true", help="Enable batch processing mode")
    parser.add_argument("--resize", default="200x150", help="Target size WxH (default: 200x150)")
    parser.add_argument("--resize-keep-aspect", action="store_true", help="Keep aspect ratio when resizing (thumbnail)")
    parser.add_argument("--quality", type=int, default=95, help="JPEG/WebP quality 1-100 (default: 95)")
    parser.add_argument("--format", choices=["jpeg", "jpg", "png", "webp", "gif", "bmp"], help="Output format (conversion)")
    parser.add_argument("--filter", choices=FILTER_CHOICES, help="Apply filter: " + ", ".join(FILTER_CHOICES))
    parser.add_argument("--chunks", type=int, help="Number of chunks (default: CPU cores)")
    parser.add_argument("--ray-check-only", action="store_true", help="Only run Ray sanity check, then exit")
    args = parser.parse_args()

    if args.ray_check_only:
        ray_check.main()
        return

    ops = build_ops(args)

    # Batch mode (Phase 2)
    if args.batch or args.input_dir:
        if not args.input_dir:
            print("Error: --batch mode requires --input-dir")
            sys.exit(1)

        input_dir = Path(args.input_dir)
        if not input_dir.is_dir():
            print(f"Error: input directory not found: {input_dir}")
            sys.exit(1)

        output_dir = Path(args.output_dir) if args.output_dir else Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)

        print("=" * 60)
        print("Phase 3: Parallel Batch Pipeline (resize, quality, format, filter)")
        print("=" * 60)
        print()

        result = pipeline.run_pipeline(
            input_dir=input_dir,
            ops=ops,
            output_dir=output_dir,
            num_chunks=args.chunks
        )

        print()
        print("=" * 60)
        print("Pipeline Results:")
        print(f"  Processed: {result['total_processed']} images")
        print(f"  Failed: {result['total_failed']} images")
        print(f"  Duration: {result['duration_seconds']:.2f} seconds")
        if result['failed_paths']:
            print(f"\nFailed images:")
            for path, error in result['failed_paths']:
                print(f"  {path}: {error}")
        print("=" * 60)
        return

    # Single-image mode (Phase 1)
    print("=" * 60)
    print("Phase 3: Single-Image (resize, quality, format, filter)")
    print("=" * 60)
    print()

    root = Path(__file__).resolve().parent
    output_dir = root / "output"
    output_dir.mkdir(exist_ok=True)

    if args.input:
        path_in = Path(args.input)
        if not path_in.is_file():
            print(f"Error: input file not found: {path_in}")
            sys.exit(1)
    else:
        path_in = output_dir / "test_input.png"
        print(f"Creating test image at {path_in}")
        image_ops.create_test_image(path_in, width=400, height=300)

    path_out = Path(args.output) if args.output else output_dir / "resized.png"
    if args.format:
        ext = image_ops._format_to_ext(args.format)
        path_out = path_out.with_suffix(ext) if ext else path_out

    print(f"Processing {path_in} -> {path_out} (resize={args.resize}, quality={ops.get('quality')}, format={ops.get('format')}, filter={ops.get('filter')})")
    image_ops.process_image(path_in, path_out, ops)
    print(f"Done. Output: {path_out}")


if __name__ == "__main__":
    main()
