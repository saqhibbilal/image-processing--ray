"""
Helper script to create test images for batch processing demos.

Usage:
  python create_test_images.py --count 20 --output-dir ./test_images
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from image_ray import image_ops


def main():
    parser = argparse.ArgumentParser(description="Create test images for batch processing")
    parser.add_argument("--count", type=int, default=10, help="Number of test images to create")
    parser.add_argument("--output-dir", default="./test_images", help="Output directory")
    parser.add_argument("--width", type=int, default=800, help="Image width")
    parser.add_argument("--height", type=int, default=600, help="Image height")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Creating {args.count} test images in {output_dir}...")
    for i in range(args.count):
        path = output_dir / f"test_image_{i:03d}.png"
        image_ops.create_test_image(path, width=args.width, height=args.height)
        if (i + 1) % 5 == 0:
            print(f"  Created {i + 1}/{args.count}...")

    print(f"Done! Created {args.count} images in {output_dir}")
    print(f"\nTest batch processing with:")
    print(f"  python main.py --batch --input-dir {output_dir} --output-dir {output_dir}/output --resize 400x300")


if __name__ == "__main__":
    main()
