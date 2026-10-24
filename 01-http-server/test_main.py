import json
import threading
import unittest
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from main import CloudHandler


class CloudServerTest(unittest.TestCase):
    """CloudHandler HTTP 서버의 동작을 검증하는 자동 단위 테스트 케이스.
    
    포트 충돌을 방지하기 위해 0번 포트(OS 자동 할당)를 사용하여 별도 데몬 스레드로
    테스트용 HTTP 서버를 구동하고 요청을 검증합니다.
    """

    @classmethod
    def setUpClass(cls):
        # OS가 사용 가능한 임의의 포트(0)를 할당하도록 서버 생성
        cls.server = HTTPServer(("127.0.0.1", 0), CloudHandler)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        # 모든 테스트 종료 후 서버 소켓 정리
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_health(self):
        """/health 엔드포인트 호출 시 200 OK와 올바른 JSON 응답이 오는지 검증"""
        url = f"http://127.0.0.1:{self.port}/health"
        with urlopen(url, timeout=3) as response:
            data = json.load(response)
            self.assertEqual(response.status, 200)
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["service"], "cloud-http-lab")

    def test_not_found(self):
        """존재하지 않는 경로(/missing) 호출 시 404 Not Found와 에러 JSON이 오는지 검증"""
        url = f"http://127.0.0.1:{self.port}/missing"
        with self.assertRaises(HTTPError) as ctx:
            urlopen(url, timeout=3)

        response = ctx.exception
        self.assertEqual(response.code, 404)
        error_data = json.loads(response.read().decode("utf-8"))
        self.assertEqual(error_data["error"], "not_found")


if __name__ == "__main__":
    unittest.main()
