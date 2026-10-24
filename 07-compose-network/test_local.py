import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from api.main import Handler
from client.check import diagnose


class NetworkLabTest(unittest.TestCase):
    """로컬 ThreadingHTTPServer와 diagnose 함수를 연동하여 DNS·TCP·HTTP를 검증하는 자동 단위 테스트."""

    @classmethod
    def setUpClass(cls):
        # 포트 충돌 방지를 위해 OS 자동 할당 임의 포트(0)로 테스트 서버 기동
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
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

    def test_dns_tcp_http(self):
        """DNS 해석, TCP 3-Way Handshake, HTTP 200 응답 수신 검증"""
        result = diagnose("127.0.0.1", self.port)
        self.assertTrue(result["dns"])
        self.assertTrue(result["tcp"])
        self.assertEqual(result["http_status"], 200)

    def test_response_json(self):
        """API 서버의 JSON 본문 응답 규격 일치 검증"""
        result = diagnose("127.0.0.1", self.port)
        self.assertEqual(
            result["body"],
            {"status": "ok", "service": "api"}
        )

    def test_unknown_route_404(self):
        """미등록 경로(/missing) 요청 시 HTTP 404 Not Found 반환 검증"""
        with self.assertRaises(HTTPError) as ctx:
            urlopen(f"http://127.0.0.1:{self.port}/missing")
        self.assertEqual(ctx.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
