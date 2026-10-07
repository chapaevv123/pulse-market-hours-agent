from __future__ import annotations

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .config import Settings
from .engine import evaluate, replay
from .fixtures import scenario


def _resolve_web_root() -> Path:
    configured = os.getenv("PULSE_WEB_ROOT")
    candidates = ([Path(configured)] if configured else []) + [
        Path.cwd() / "web",
        Path(__file__).resolve().parents[2] / "web",
    ]
    for candidate in candidates:
        if (candidate / "index.html").is_file():
            return candidate.resolve()
    raise RuntimeError("Static web root not found; expected web/index.html")


WEB = _resolve_web_root()
SETTINGS = Settings.from_env()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def _json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, separators=(",", ":"), default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._json(200, SETTINGS.health())
            return
        if parsed.path in {"/api/evaluate", "/api/receipt"}:
            name = parse_qs(parsed.query).get("scenario", ["false_arbitrage"])[0]
            try:
                self._json(200, evaluate(scenario(name)).as_dict())
            except KeyError:
                self._json(404, {"error": "unknown scenario"})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/replay":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            receipt = json.loads(self.rfile.read(length))
            reproduced = replay(receipt)
            self._json(200, {"verified": True, "receipt": reproduced.as_dict()})
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            self._json(422, {"verified": False, "error": str(exc)})


def main() -> None:
    SETTINGS.validate_startup()
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8080"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Pulse Market Hours Agent: http://{host}:{port}")
    print(f"Mode: {SETTINGS.demo_mode}; live ready: {SETTINGS.health()['live_ready']}")
    server.serve_forever()


if __name__ == "__main__":
    main()
