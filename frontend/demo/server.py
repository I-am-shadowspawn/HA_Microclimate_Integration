"""Serve the card demo with the same model-icon paths as the HA integration."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
MODEL_ICONS = {"evo-connect.png", "evo-connect-ii.png", "evo-connect-iii.png"}


class DemoHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path.startswith("/microclimate_integration/"):
            filename = path.removeprefix("/microclimate_integration/")
            if filename in MODEL_ICONS:
                self.path = (
                    "/custom_components/microclimate_integration/frontend/" + filename
                )
        super().do_GET()


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8767), DemoHandler).serve_forever()
