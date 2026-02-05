# image-ray

A learning-focused image processing pipeline that demonstrates parallel data pipelines on a single machine using [Ray](https://www.ray.io/). Images are processed in batches by splitting work into chunks and running them on Ray workers.

## Phase 1 – Setup and single-image processing

### Requirements

- Python 3.10+
- Windows (or any OS supported by Ray)

### Setup

```bash
cd image-ray
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Run

1. **Ray sanity check** – confirm Ray starts and runs a remote task:

   ```bash
   python -m image_ray.ray_check
   ```

2. **Single-image resize** – process one image (creates a test image if none is provided):

   ```bash
   python main.py
   ```

   Or with your own image:

   ```bash
   python main.py --input path\to\your\image.png --output path\to\output.png
   ```

### Project layout (Phase 1)

```
image-ray/
  main.py              # Entrypoint: Ray check + single-image demo
  requirements.txt
  README.md
  src/
    image_ray/
      __init__.py
      image_ops.py     # Pillow-based image operations (e.g. resize)
      ray_check.py     # Ray init + one remote task
```

Later phases add the parallel batch pipeline, full CLI, and optional web UI.
