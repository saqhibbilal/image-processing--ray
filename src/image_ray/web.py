"""
Phase 4: Minimal web UI for the image pipeline.

Run with: python -m image_ray.web
Or: flask --app src/image_ray/web.py run
"""

import io
import shutil
import tempfile
import zipfile
from pathlib import Path

from flask import Flask, render_template, request, send_file

from image_ray import pipeline

# Resize string "WxH" -> (w, h)
def parse_resize(s):
    s = (s or "200x150").strip().lower()
    try:
        w, h = s.split("x")
        return (int(w), int(h))
    except (ValueError, AttributeError):
        return (200, 150)

# Build ops dict from form
def form_to_ops(form):
    resize = parse_resize(form.get("resize"))
    ops = {
        "resize": resize,
        "resize_keep_aspect": form.get("resize_keep_aspect") == "on",
        "quality": int(form.get("quality") or 95),
    }
    if form.get("format"):
        ops["format"] = form.get("format").strip().lower()
    if form.get("filter"):
        ops["filter"] = form.get("filter").strip().lower()
    return ops

def create_app():
    app = Flask(__name__, template_folder=str(Path(__file__).resolve().parent / "templates"))
    app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB total upload

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/process", methods=["POST"])
    def process():
        if "images" not in request.files and not request.files.getlist("images"):
            return {"error": "No images selected"}, 400

        files = request.files.getlist("images")
        if not files or not any(f.filename for f in files):
            return {"error": "No images selected"}, 400

        allowed = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
        input_dir = Path(tempfile.mkdtemp(prefix="image_ray_in_"))
        output_dir = Path(tempfile.mkdtemp(prefix="image_ray_out_"))
        try:
            for f in files:
                if not f.filename:
                    continue
                ext = Path(f.filename).suffix.lower()
                if ext not in allowed:
                    continue
                f.save(input_dir / Path(f.filename).name)

            ops = form_to_ops(request.form)
            result = pipeline.run_pipeline(
                input_dir=input_dir,
                ops=ops,
                output_dir=output_dir,
                num_chunks=None,
            )

            # Zip output
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in output_dir.iterdir():
                    if f.is_file():
                        zf.write(f, f.name)
            buf.seek(0)
            resp = send_file(
                buf,
                mimetype="application/zip",
                as_attachment=True,
                download_name="image_ray_results.zip",
            )
            resp.headers["X-Processed-Count"] = str(result["total_processed"])
            resp.headers["X-Duration-Seconds"] = str(round(result["duration_seconds"], 2))
            return resp
        finally:
            shutil.rmtree(input_dir, ignore_errors=True)
            shutil.rmtree(output_dir, ignore_errors=True)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
