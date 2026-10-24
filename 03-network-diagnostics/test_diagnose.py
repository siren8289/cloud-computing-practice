import os
import sys
import threading
import unittest
from http.server import HTTPServer

# 01-http-server의 CloudHandler 모듈 임포트
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "01-http-server")))
from main import CloudHandler

from diagnose import diagnose, http_check, resolve, tcp_check


class NetworkDiagnosticsTest(unittest.TestCase):
    """DNS 해석, TCP 연결, HTTP 상태 검증을 수행하는 자동 단위 테스트 케이스."""

    @classmethod
    def setUpClass(cls):
        # 포트 충돌 방지를 위해 OS 자동 할당 포트(0)로 테스트용 HTTP 서버 구동
        cls.server = HTTPServer(("127.0.0.1", 0), CloudHandler)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_dns(self):
        """호스트명(localhost)을 IP 주소로 변환하는 DNS 해석 기능 검증"""
        result = resolve("localhost")
        self.assertTrue(result["ok"])
        self.assertIn("127.0.0.1", result["addresses"])

    def test_tcp(self):
        """테스트 서버의 포트로 TCP 소켓 연결 성공 여부 검증"""
        result = tcp_check("127.0.0.1", self.port)
        self.assertTrue(result["ok"])
        self.assertEqual(result["port"], self.port)

    def test_http_200(self):
        """정상 경로(/health) 호출 시 HTTP 200 상태 및 JSON 본문 파싱 검증"""
        result = http_check("127.0.0.1", self.port, "/health")
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], 200)
        self.assertIsInstance(result["body"], dict)
        self.assertEqual(result["body"].get("status"), "ok")

    def test_http_404(self):
        """존재하지 않는 경로(/missing) 호출 시 HTTP 404 상태 및 에러 본문 검증"""
        result = http_check("127.0.0.1", self.port, "/missing")
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], 404)
        self.assertIsInstance(result["body"], dict)
        self.assertEqual(result["body"].get("error"), "not_found")

    def test_end_to_end(self):
        """DNS -> TCP -> HTTP 전체 단계를 순차적으로 검증하는 엔드투엔드 진단 검증"""
        result = diagnose("127.0.0.1", self.port, "/health")
        self.assertTrue(result["dns"]["ok"])
        self.assertTrue(result["tcp"]["ok"])
        self.assertTrue(result["http"]["ok"])
        self.assertEqual(result["http"]["status"], 200)


if __name__ == "__main__":
    unittest.main()
