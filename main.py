"""
Phase 1 entrypoint: Ray check and single-image resize demo.

Usage:
  python main.py                    # Run Ray check, then create test image and resize it
  python main.py --input a.png --output b.png   # Resize your own image
  python main.py --ray-check-only   # Only run Ray sanity check
"""

import argparse
import sys
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from image_ray import image_ops
from image_ray import ray_check


def main():
    parser = argparse.ArgumentParser(description="Image-Ray Phase 1: Ray check + single-image resize")
    parser.add_argument("--input", "-i", help="Input image path (default: create a test image)")
    parser.add_argument("--output", "-o", help="Output image path (default: output/resized.png)")
    parser.add_argument("--resize", default="200x150", help="Target size WxH (default: 200x150)")
    parser.add_argument("--ray-check-only", action="store_true", help="Only run Ray sanity check, then exit")
    args = parser.parse_args()

    if args.ray_check_only:
        ray_check.main()
        return

    # Run Ray check first so we know the environment works
    print("Running Ray sanity check...")
    ray_check.main()
    print()

    # Resize demo
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
    w, h = args.resize.lower().split("x")
    ops = {"resize": (int(w), int(h)), "resize_keep_aspect": False}

    print(f"Resizing {path_in} -> {path_out} to {args.resize}")
    image_ops.process_image(path_in, path_out, ops)
    print(f"Done. Output: {path_out}")


if __name__ == "__main__":
    main()
