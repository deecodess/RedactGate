from __future__ import annotations

import argparse
import json
from email import policy
from email.parser import BytesParser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .service import sanitize_upload


UI_DIR = Path(__file__).with_name("ui")


class RedactGateHandler(BaseHTTPRequestHandler):
    server_version = "RedactGateWeb/0.1"

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        route = urlparse(self.path).path
        assets = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/styles.css": ("styles.css", "text/css; charset=utf-8"),
            "/app.js": ("app.js", "text/javascript; charset=utf-8"),
        }
        if route not in assets:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        filename, content_type = assets[route]
        path = UI_DIR / filename
        self._send_bytes(path.read_bytes(), content_type)

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if urlparse(self.path).path != "/api/sanitize":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            result = self._sanitize_upload()
        except (OSError, ValueError, KeyError) as error:
            self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _sanitize_upload(self) -> dict[str, object]:
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            raise ValueError("Upload must use multipart/form-data.")
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)
        message = BytesParser(policy=policy.default).parsebytes(
            f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + body
        )
        upload = next((part for part in message.iter_attachments() if part.get_filename()), None)
        if upload is None:
            raise ValueError("Choose a file to sanitize.")
        filename = Path(upload.get_filename()).name
        data = upload.get_payload(decode=True) or b""
        return sanitize_upload(filename, data)

    def _send_json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        self._send_bytes(
            json.dumps(payload, indent=2).encode("utf-8"),
            "application/json; charset=utf-8",
            status,
        )

    def _send_bytes(
        self,
        payload: bytes,
        content_type: str,
        status: HTTPStatus = HTTPStatus.OK,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[redactgate] {format % args}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local RedactGate web UI.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), RedactGateHandler)
    print(f"RedactGate UI running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping RedactGate UI.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
