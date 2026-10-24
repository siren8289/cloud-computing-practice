import importlib.util
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

module_path = Path(__file__).resolve().parents[1] / "app" / "main.py"
spec = importlib.util.spec_from_file_location("observability_app", module_path)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class ObservabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, path):
        url = f"http://127.0.0.1:{self.port}{path}"
        try:
            with urlopen(url, timeout=3) as resp:
                return resp.status, resp.read().decode("utf-8")
        except HTTPError as e:
            return e.code, e.read().decode("utf-8")

    def test_health(self):
        status, body = self.request("/health")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data.get("status"), "ok")

    def test_metrics_counter(self):
        # /work 요청 발생 후 메트릭 확인
        self.request("/work")
        status, metrics = self.request("/metrics")
        self.assertEqual(status, 200)
        self.assertIn("http_requests_total", metrics)
        self.assertIn('route="/work"', metrics)

    def test_error_metric(self):
        # /error 요청 시 의도적 500 발생 및 메트릭 기록 확인
        status, body = self.request("/error")
        self.assertEqual(status, 500)
        _, metrics = self.request("/metrics")
        self.assertIn('status="500"', metrics)

    def test_histogram(self):
        # 히스토그램 버킷 메트릭 생성 확인
        self.request("/work")
        status, metrics = self.request("/metrics")
        self.assertEqual(status, 200)
        self.assertIn("http_request_duration_seconds_bucket", metrics)
        self.assertIn("http_request_duration_seconds_count", metrics)


if __name__ == "__main__":
    unittest.main()
