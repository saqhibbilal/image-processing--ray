"""
Image-Ray: Parallel image processing pipeline with Ray.

Phase 1: Single-image processing
Phase 2: Batch processing (parallel pipeline)

Usage:
  # Single image (Phase 1)
  python main.py                    # Create test image and resize it
  python main.py --input a.png --output b.png   # Resize your own image
  
  # Batch processing (Phase 2)
  python main.py --batch --input-dir ./images --output-dir ./output --resize 800x600
  
  # Other options
  python main.py --ray-check-only   # Only run Ray sanity check
"""

import argparse
import sys
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from image_ray import image_ops
from image_ray import pipeline
from image_ray import ray_check


def parse_resize(resize_str: str) -> tuple:
    """Parse resize string like '800x600' into (width, height)."""
    try:
        w, h = resize_str.lower().split("x")
        return (int(w), int(h))
    except ValueError:
        print(f"Error: --resize must be in format WxH (e.g. 800x600)")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Image-Ray: Parallel image processing with Ray")
    parser.add_argument("--input", "-i", help="Input image path (single-image mode)")
    parser.add_argument("--output", "-o", help="Output image path (single-image mode)")
    parser.add_argument("--input-dir", help="Input directory (batch mode)")
    parser.add_argument("--output-dir", help="Output directory (batch mode, optional)")
    parser.add_argument("--batch", action="store_true", help="Enable batch processing mode")
    parser.add_argument("--resize", default="200x150", help="Target size WxH (default: 200x150)")
    parser.add_argument("--chunks", type=int, help="Number of chunks (default: CPU cores)")
    parser.add_argument("--ray-check-only", action="store_true", help="Only run Ray sanity check, then exit")
    args = parser.parse_args()

    if args.ray_check_only:
        ray_check.main()
        return

    # Parse resize
    resize_tuple = parse_resize(args.resize)
    ops = {"resize": resize_tuple, "resize_keep_aspect": False}

    # Batch mode (Phase 2)
    if args.batch or args.input_dir:
        if not args.input_dir:
            print("Error: --batch mode requires --input-dir")
            sys.exit(1)

        input_dir = Path(args.input_dir)
        if not input_dir.is_dir():
            print(f"Error: input directory not found: {input_dir}")
            sys.exit(1)

        output_dir = Path(args.output_dir) if args.output_dir else None

        print("=" * 60)
        print("Phase 2: Parallel Batch Processing Pipeline")
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
    print("Phase 1: Single-Image Processing")
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

    print(f"Resizing {path_in} -> {path_out} to {args.resize}")
    image_ops.process_image(path_in, path_out, ops)
    print(f"Done. Output: {path_out}")


if __name__ == "__main__":
    main()
