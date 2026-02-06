# Setup Guide

Simple step-by-step instructions to get Image-Ray running on your machine.

## Prerequisites

- **Python 3.9+** installed
- **Windows, macOS, or Linux**

## Step 1: Clone and Navigate

```bash
# If you cloned the repo, navigate to it:
cd image-ray

# Or if you're already in the project folder, skip this step
```

## Step 2: Create Virtual Environment

```bash
# Create a virtual environment
python -m venv .venv

# Activate it:
# Windows:
.venv\Scripts\activate

# macOS/Linux:
# source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

## Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Install the package in editable mode (needed for Ray workers)
pip install -e .
```

This installs:
- Ray (parallel processing)
- Pillow (image operations)
- Flask (web UI)

## Step 4: Test It Works

### Quick Test - Ray Check

```bash
python -m image_ray.ray_check
```

Expected output: `Remote task returned: Ray is working!`

### Quick Test - Single Image

```bash
python main.py
```

This creates a test image and resizes it. Check the `output/` folder for `resized.png`.

## Running the Project

### Option 1: Command Line (CLI)

**Single image:**
```bash
python main.py --input path\to\your\image.png --output path\to\output.jpg --resize 800x600
```

**Batch processing (folder):**
```bash
python main.py --batch --input-dir ./images --output-dir ./output --resize 400x300
```

**With more options:**
```bash
python main.py --batch --input-dir ./photos --output-dir ./export --resize 1200x800 --format jpeg --quality 90 --filter grayscale
```

### Option 2: Web UI

**Start the server:**
```bash
python run_web.py
```

**Open in browser:**
```
http://127.0.0.1:5000
```

Then:
1. Click "Choose Files" and select one or more images
2. Set options (resize, quality, format, filter)
3. Click "Process"
4. Compare input vs output thumbnails
5. Click "Download ZIP" to get all processed images

**Stop the server:** Press `Ctrl+C` in the terminal

## Testing Examples

### Create Test Images

```bash
# Create 10 test images in ./test_images folder
python create_test_images.py --count 10 --output-dir ./test_images
```

### Process Test Images

```bash
# Batch process the test images
python main.py --batch --input-dir ./test_images --output-dir ./test_output --resize 400x300 --format jpeg
```

Check `./test_output` for processed images.

## Troubleshooting

**"No module named 'image_ray'"**
- Make sure you ran `pip install -e .` (the `-e` flag is important)

**"Ray is not working"**
- Make sure Python 3.9+ is installed
- Try: `python --version`

**Web UI won't start**
- Make sure Flask is installed: `pip install flask`
- Check if port 5000 is already in use

**Images not processing**
- Check file extensions: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`
- Make sure input directory exists and contains images

## Project Structure

```
image-ray/
  main.py              # CLI entrypoint
  run_web.py           # Web UI entrypoint
  requirements.txt     # Dependencies
  SETUP.md            # This file
  src/
    image_ray/        # Main package
      pipeline.py     # Batch processing logic
      image_ops.py    # Image operations
      web.py          # Web server
      templates/      # Web UI HTML
```

## Next Steps

- Read `README.md` for full feature documentation
- Try different resize, quality, format, and filter options
- Process your own image folders!
