import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = os.environ.get("APP_VERSION", "v1")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            code, payload = 200, {"status": "ok", "version": VERSION}
        elif self.path == "/":
            code, payload = 200, {"service": "cloud-api", "version": VERSION}
        else:
            code, payload = 404, {"error": "not_found"}

        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8081), Handler).serve_forever()
