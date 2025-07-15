# run.py
import logging

from admin_page import create_app
from admin_page.config import Dev

# —————— 1) load local.settings.json ——————
""" cfg_path = Path(__file__).parent / "local.settings.json"
if cfg_path.exists():
    data = json.loads(cfg_path.read_text())
    for section in ("Values", "ConnectionStrings"):
        for k, v in data.get(section, {}).items():
            # only set if not already in the real environment
            os.environ.setdefault(k, v) """

logging.basicConfig(
    level=logging.INFO,  # show INFO+ from the root
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
app = create_app(Dev)
# from bootstrap_base_columns import *   # noqa: F401,F403
# from bootstrap_customers import *
if __name__ == "__main__":
    # 0.0.0.0 makes it reachable from Docker or VMs;
    # remove debug=True in prod.
    app.run(host="0.0.0.0", port=5000, debug=True)
