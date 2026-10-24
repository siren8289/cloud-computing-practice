import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class CloudHandler(BaseHTTPRequestHandler):
    """클라우드 HTTP 요청을 처리하는 핸들러 클래스.
    
    클라이언트(웹 브라우저, curl, 모니터링 도구 등)의 HTTP 요청 경로(path)를 판별하여
    JSON 규격의 응답 헤더와 본문을 반환합니다.
    """

    def do_GET(self):
        # 1. HTTP 요청 경로(path) 확인 및 분기
        if self.path == "/health":
            status = 200
            data = {
                "status": "ok",
                "service": "cloud-http-lab"
            }
        else:
            status = 404
            data = {
                "error": "not_found"
            }

        # 2. 파이썬 딕셔너리를 JSON 문자열로 직렬화한 후 UTF-8 바이트로 인코딩
        body = json.dumps(data).encode("utf-8")

        # 3. HTTP 응답 헤더 구성
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        # 4. 소켓 출력 스트림(wfile)을 통해 클라이언트에게 응답 본문 전송
        self.wfile.write(body)


def run():
    """서버 구동 함수.
    
    127.0.0.1(로컬 루프백 인터페이스)과 8081 포트에 TCP 소켓을 바인딩하고
    무한 루프(serve_forever)를 돌며 클라이언트의 연결 요청을 대기합니다.
    """
    server = HTTPServer(("127.0.0.1", 8081), CloudHandler)
    print("Server: http://127.0.0.1:8081", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    run()
