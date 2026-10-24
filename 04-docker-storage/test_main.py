import json
import tempfile
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import main
from main import DockerStorageHandler


class DockerStorageServerTest(unittest.TestCase):
    """DockerStorageHandler의 헬스체크 및 파일 저장/조회 영속 로직을 검증하는 자동 단위 테스트."""

    @classmethod
    def setUpClass(cls):
        # 테스트 격리를 위한 임시 데이터 디렉터리 생성
        cls.tmp_dir = tempfile.TemporaryDirectory()
        main.DATA_DIR = Path(cls.tmp_dir.name)
        main.NOTE_FILE = main.DATA_DIR / "note.txt"

        # 포트 충돌 방지를 위해 OS 동적 포트(0)로 테스트 서버 바인딩
        cls.server = HTTPServer(("127.0.0.1", 0), DockerStorageHandler)
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
        cls.tmp_dir.cleanup()

    def test_health(self):
        """GET /health 호출 시 200 OK 및 서비스명 반환 검증"""
        url = f"http://127.0.0.1:{self.port}/health"
        with urlopen(url, timeout=3) as response:
            data = json.load(response)
            self.assertEqual(response.status, 200)
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["service"], "cloud-docker-lab")

    def test_note_roundtrip(self):
        """POST /note로 노트 저장(201) 후 GET /note로 동일 데이터 조회(200) 검증"""
        post_url = f"http://127.0.0.1:{self.port}/note"
        payload = json.dumps({"note": "persist-me"}).encode("utf-8")
        req = Request(
            post_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urlopen(req, timeout=3) as response:
            self.assertEqual(response.status, 201)
            data = json.load(response)
            self.assertTrue(data.get("saved"))
            self.assertEqual(data.get("note"), "persist-me")

        # GET 조회 검증
        get_url = f"http://127.0.0.1:{self.port}/note"
        with urlopen(get_url, timeout=3) as response:
            self.assertEqual(response.status, 200)
            data = json.load(response)
            self.assertEqual(data.get("note"), "persist-me")

    def test_bad_note(self):
        """잘못된 입력(빈 본문, 필드 누락 등) 전송 시 400 Bad Request 반환 검증"""
        post_url = f"http://127.0.0.1:{self.port}/note"
        bad_payload = json.dumps({"wrong_field": "test"}).encode("utf-8")
        req = Request(
            post_url,
            data=bad_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with self.assertRaises(HTTPError) as ctx:
            urlopen(req, timeout=3)
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
