# image-ray

A learning-focused image processing pipeline that demonstrates parallel data pipelines on a single machine using [Ray](https://www.ray.io/). Images are processed in batches by splitting work into chunks and running them on Ray workers.

## Requirements

- Python 3.9+ (tested on 3.9+)
- Windows (or any OS supported by Ray)

## Setup

```bash
cd image-ray
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
pip install -e .  # Install package in editable mode (needed for Ray workers)
```

## Phase 1 – Single-image processing

**Ray sanity check:**

```bash
python -m image_ray.ray_check
```

**Single-image processing** (creates a test image if no `--input`):

```bash
python main.py
python main.py --input a.png --output b.jpg --resize 800x600 --format jpeg --quality 85 --filter grayscale
```

## Phase 2 – Parallel batch processing

Process a directory of images in parallel:

```bash
python main.py --batch --input-dir ./images --output-dir ./out --resize 800x600
# Default output directory is ./output if --output-dir is omitted
python main.py --batch --input-dir ./images --resize 400x300
python main.py --batch --input-dir ./images --output-dir ./out --chunks 4
```

## Phase 3 – Full operations and CLI

All operations (Pillow-only) are available in both single-image and batch mode.

| Option | Description |
|--------|-------------|
| `--resize WxH` | Target size (default: 200x150) |
| `--resize-keep-aspect` | Keep aspect ratio (thumbnail) |
| `--quality N` | JPEG/WebP quality 1–100 (default: 95) |
| `--format FORMAT` | Output format: jpeg, png, webp, gif, bmp |
| `--filter NAME` | Filter: blur, sharpen, grayscale, contour, detail, edge_enhance, smooth, smooth_more |

**Examples:**

```bash
# Single image: resize, convert to JPEG, compress, grayscale
python main.py -i photo.png -o photo_small.jpg --resize 400x300 --format jpeg --quality 80 --filter grayscale

# Batch: PNG folder -> JPEG output with resize and quality
python main.py --batch --input-dir ./photos --output-dir ./export --resize 1200x800 --format jpeg --quality 90

# Batch with filter
python main.py --batch --input-dir ./images --output-dir ./blurred --resize 800x600 --filter blur
```

**Batch default:** If `--output-dir` is omitted, output is written to `./output`.

## Phase 4 – Web UI

Minimal black-and-white web interface (Quantico font). Upload images, set options, run the same pipeline, download results as a zip.

```bash
# From project root (after pip install -r requirements.txt && pip install -e .)
python run_web.py
# or
python -m image_ray.web
```

Open **http://127.0.0.1:5000** in your browser. Upload images, choose resize/quality/format/filter, then click **Process**. The zip of processed images will download automatically.

## Project layout

```
image-ray/
  main.py              # CLI: single-image or batch mode
  run_web.py           # Run Phase 4 web UI
  requirements.txt
  README.md
  create_test_images.py
  src/
    image_ray/
      __init__.py
      image_ops.py     # Resize, quality, format conversion, filters (Pillow)
      ray_check.py     # Ray init + one remote task
      pipeline.py      # Chunking, Ray workers, aggregation
      web.py           # Phase 4 Flask app
      templates/
        index.html     # Single-page UI (Quantico, black/white theme)
```
