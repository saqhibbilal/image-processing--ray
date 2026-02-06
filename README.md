# image-ray

Image-Ray is a parallel image processing pipeline built to demonstrate how batch workloads can be scaled efficiently on a single machine using [Ray](https://www.ray.io/). The project tackles a common problem in media processing: transforming large batches of images through operations like resizing, format conversion, compression, and filtering. Instead of processing images sequentially, Ray orchestrates multiple worker processes that handle chunks of images concurrently, allowing all available CPU cores to work in parallel. This approach mirrors patterns used in production systems for media platforms, machine learning preprocessing pipelines, and content moderation, where speed and reliability matter when dealing with hundreds or thousands of images.

The system provides two interfaces: a command-line tool for scripting and automation, and a minimal web interface for interactive use. Both interfaces share the same underlying pipeline, which discovers images in a directory, splits them into chunks based on the number of CPU cores, and distributes work across Ray workers. Each worker processes its assigned chunk independently, applying the same set of operations—resize dimensions, quality settings, output format conversion, and optional filters like grayscale or blur. Results are aggregated and written to an output directory, with detailed metrics showing how many images were processed, how many parallel chunks were used, and total execution time. The web UI goes further by displaying side-by-side comparisons of input and output images, making it easy to verify transformations before downloading results.

Performance scales with available hardware. On a typical multi-core machine, processing 40 images might complete in just over a second using 4 parallel chunks, while a sequential approach could take several times longer. The pipeline handles failures gracefully, reporting which images failed and why, so partial batches don't stop the entire job. All processing uses Pillow for image operations, keeping dependencies lightweight and avoiding GPU requirements. The project is designed as a learning tool, emphasizing clear code structure and observable parallel execution patterns rather than production deployment features, making it straightforward to understand how distributed computing concepts apply to CPU-bound workloads.

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

Process a directory of images in parallel. The pipeline automatically splits work into chunks and processes them concurrently:

![Batch Processing Results](Screenshot%202026-02-06%20020823.jpg)

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

Minimal black-and-white web interface (Quantico font) for interactive image processing. Upload multiple images, configure processing options, and see results with side-by-side input/output comparisons.

![Web UI Upload Form](Screenshot%202026-02-06%20021718.jpg)

The interface shows batching information—how many images were processed, how many parallel chunks were used, and execution time—along with thumbnail previews of both input and output images for easy comparison.

![Web UI Results with Batching Info](Screenshot%202026-02-06%20023400.jpg)

![Web UI Input/Output Comparison](Screenshot%202026-02-06%20023736.jpg)

![Web UI Batch Processing](Screenshot%202026-02-06%20023845.jpg)

```bash
# From project root (after pip install -r requirements.txt && pip install -e .)
python run_web.py
# or
python -m image_ray.web
```

Open **http://127.0.0.1:5000** in your browser. Upload images, choose resize/quality/format/filter, then click **Process**. Compare input vs output thumbnails and download the ZIP when ready.

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
