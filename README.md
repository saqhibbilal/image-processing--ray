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

**Ray sanity check** – confirm Ray starts and runs a remote task:

```bash
python -m image_ray.ray_check
```

**Single-image resize** – process one image (creates a test image if none is provided):

```bash
python main.py
```

Or with your own image:

```bash
python main.py --input path\to\your\image.png --output path\to\output.png
```

## Phase 2 – Parallel batch processing

Process a directory of images in parallel using Ray workers:

```bash
# Process all images in a directory
python main.py --batch --input-dir ./images --output-dir ./output --resize 800x600

# Overwrite originals (no --output-dir)
python main.py --batch --input-dir ./images --resize 400x300

# Control number of chunks (default: CPU cores)
python main.py --batch --input-dir ./images --output-dir ./output --resize 800x600 --chunks 4
```

The pipeline will:
1. Discover all images in the input directory
2. Split them into chunks (one per CPU core by default)
3. Process each chunk in parallel on Ray workers
4. Aggregate results and report timing

**Example output:**
```
============================================================
Phase 2: Parallel Batch Processing Pipeline
============================================================

Discovering images in ./images...
Found 20 images
Split into 4 chunks (target: 4 chunks)
Submitting 4 tasks to Ray workers...

============================================================
Pipeline Results:
  Processed: 20 images
  Failed: 0 images
  Duration: 2.34 seconds
============================================================
```

## Project layout

```
image-ray/
  main.py              # Entrypoint: single-image or batch mode
  requirements.txt
  README.md
  src/
    image_ray/
      __init__.py
      image_ops.py     # Pillow-based image operations (resize)
      ray_check.py     # Ray init + one remote task
      pipeline.py      # Phase 2: chunking, Ray workers, aggregation
```

Later phases add more operations (compress, format conversion, filtering), full CLI, and optional web UI.
