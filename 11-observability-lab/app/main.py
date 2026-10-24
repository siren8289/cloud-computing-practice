import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

REQUESTS = Counter(
    "http_requests_total",
    "HTTP requests",
    ["method", "route", "status"],
)

LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Prometheus 수집용 엔드포인트
        if self.path == "/metrics":
            data = generate_latest()
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        start = time.perf_counter()
        route = (
            self.path if self.path in ("/health", "/work", "/error") else "/other"
        )
        if route == "/work":
            time.sleep(0.025)

        status = 500 if route == "/error" else 404 if route == "/other" else 200
        payload = (
            {"status": "ok", "service": "cloud-observability-lab"}
            if status == 200
            else {"error": "demo_error" if status == 500 else "not_found"}
        )
        body = json.dumps(payload).encode()
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        finally:
            # 상태 코드별 요청 건수
            REQUESTS.labels("GET", route, str(status)).inc()
            # 응답 소요시간
            LATENCY.labels(route).observe(time.perf_counter() - start)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8081), Handler).serve_forever()
