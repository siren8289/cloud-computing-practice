import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    """멀티 컨테이너 네트워크 실습용 HTTP 서버 핸들러."""

    def do_GET(self):
        status = 200 if self.path == "/health" else 404
        payload = (
            {"status": "ok", "service": "api"}
            if status == 200
            else {"error": "not_found"}
        )
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    # 다른 컨테이너에서도 브리지 네트워크를 통해 접근 가능하도록 0.0.0.0 인터페이스 바인딩
    print("API Server starting on 0.0.0.0:8081...", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8081), Handler).serve_forever()
