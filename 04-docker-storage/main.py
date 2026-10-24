import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# 데이터 저장 디렉터리 및 파일 경로 (환경변수 또는 기본값 /data)
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
NOTE_FILE = DATA_DIR / "note.txt"


class DockerStorageHandler(BaseHTTPRequestHandler):
    """헬스체크 및 파일 기반 노트 저장/조회를 지원하는 HTTP 요청 핸들러."""

    def reply(self, status: int, data: dict):
        """JSON 규격 응답 헤더 및 본문을 클라이언트에게 전송합니다."""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # 1. 헬스체크 엔드포인트
        if self.path == "/health":
            self.reply(200, {
                "status": "ok",
                "service": "cloud-docker-lab"
            })
        # 2. 저장된 노트 조회 엔드포인트
        elif self.path == "/note":
            if NOTE_FILE.exists():
                content = NOTE_FILE.read_text(encoding="utf-8")
                self.reply(200, {
                    "note": content
                })
            else:
                self.reply(404, {
                    "error": "note_not_found"
                })
        # 3. 기타 미등록 엔드포인트
        else:
            self.reply(404, {
                "error": "not_found"
            })

    def do_POST(self):
        # /note 경로 이외의 POST 요청 차단
        if self.path != "/note":
            self.reply(404, {
                "error": "not_found"
            })
            return

        # Content-Length 헤더 검증
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            content_length = 0

        if content_length <= 0:
            self.reply(400, {
                "error": "invalid_payload"
            })
            return

        # 본문 읽기 및 JSON 디코딩
        try:
            raw_body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(raw_body)
        except Exception:
            self.reply(400, {
                "error": "invalid_json"
            })
            return

        # 입력 필드 유효성 검증
        if not isinstance(payload, dict) or "note" not in payload:
            self.reply(400, {
                "error": "missing_note_field"
            })
            return

        note = payload["note"]
        if not isinstance(note, str) or not note.strip():
            self.reply(400, {
                "error": "empty_note"
            })
            return

        # Docker Volume으로 마운트된 디렉터리에 영속 저장
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            NOTE_FILE.write_text(note, encoding="utf-8")
            self.reply(201, {
                "saved": True,
                "note": note
            })
        except Exception as exc:
            self.reply(500, {
                "error": "storage_write_failed",
                "details": str(exc)
            })


def run():
    """서버 구동: 컨테이너 내부 및 외부 통신을 위해 0.0.0.0 인터페이스 바인딩"""
    server = HTTPServer(("0.0.0.0", 8081), DockerStorageHandler)
    print(f"Server listening on 0.0.0.0:8081 (DATA_DIR={DATA_DIR})", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    run()
