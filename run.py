"""
Habit Tracker — Application entry point.
"""
import webbrowser
import threading
from app import create_app
from app.config import Config

app = create_app()


def open_browser(port):
    """Open the default browser after a short delay."""
    import time
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{port}")


if __name__ == "__main__":
    port = Config.PORT
    # Open browser in background thread
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    app.run(host="127.0.0.1", port=port, debug=Config.DEBUG)
