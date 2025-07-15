# run.py
from admin_page import create_app
from admin_page.config import Dev

app = create_app(Dev)

if __name__ == "__main__":
    # 0.0.0.0 makes it reachable from Docker or VMs;
    # remove debug=True in prod.
    app.run(host="0.0.0.0", port=5000, debug=True)
