import json
import socket
import sys
from urllib.request import urlopen


def diagnose(host="api", port=8081):
    """Docker 내부 DNS를 통해 서비스 이름을 컨테이너 IP로 해석하고, TCP 연결 및 HTTP 헬스체크를 수행합니다."""
    # 1. 서비스 이름을 컨테이너 IP 주소 목록으로 해석 (Docker 내장 DNS)
    ips = sorted({
        r[4][0] for r in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    })

    # 2. TCP 3-Way Handshake 연결 확인
    with socket.create_connection((host, port), timeout=3):
        tcp = True

    # 3. HTTP GET /health 요청 및 JSON 응답 검증
    with urlopen(f"http://{host}:{port}/health", timeout=3) as response:
        status = response.status
        payload = json.load(response)

    result = {
        "dns": ips,
        "tcp": tcp,
        "http_status": status,
        "body": payload
    }

    if status != 200 or payload.get("status") != "ok":
        raise RuntimeError(f"health failed: {result}")

    return result


if __name__ == "__main__":
    try:
        print(json.dumps(diagnose(), indent=2))
    except Exception as exc:
        print(f"DIAGNOSTIC FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
