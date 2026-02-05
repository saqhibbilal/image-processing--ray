"""Run the Phase 4 web UI. Requires: pip install -e . && pip install flask."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from image_ray.web import app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
