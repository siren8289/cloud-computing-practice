import json
import threading
import unittest
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from app import Handler


class AppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 포트 충돌 방지를 위해 임의 가용 포트(0번)로 테스트 서버 바인딩
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_health_status(self):
        """/health 엔드포인트 HTTP 200 상태 코드 검증"""
        url = f"http://127.0.0.1:{self.port}/health"
        with urllib.request.urlopen(url, timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)

    def test_health_json(self):
        """/health 응답 본문 JSON 스키마 및 내용 검증"""
        url = f"http://127.0.0.1:{self.port}/health"
        with urllib.request.urlopen(url, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ok")
            self.assertEqual(data.get("service"), "cloud-ci-lab")

    def test_unknown_route(self):
        """미등록 경로(/missing) 요청 시 HTTP 404 및 JSON 에러 반환 검증"""
        url = f"http://127.0.0.1:{self.port}/missing"
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(url, timeout=3.0)
        self.assertEqual(ctx.exception.code, 404)
        error_body = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertEqual(error_body, {"error": "not_found"})


if __name__ == "__main__":
    unittest.main()
