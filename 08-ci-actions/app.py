import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # /health 요청만 정상 처리
        status = 200 if self.path == "/health" else 404
        payload = (
            {"status": "ok", "service": "cloud-ci-lab"}
            if status == 200
            else {"error": "not_found"}
        )
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # 콘솔 로그 출력 (표준 출력)
        pass


def serve(host="0.0.0.0", port=8081):
    server = ThreadingHTTPServer((host, port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    serve()
