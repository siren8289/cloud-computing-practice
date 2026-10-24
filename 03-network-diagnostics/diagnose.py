import argparse
import json
import socket
import urllib.error
import urllib.request


def resolve(host: str) -> dict:
    """호스트 이름(도메인 또는 IP)을 IP 주소 목록으로 변환(DNS 조회)합니다."""
    try:
        # SOCK_STREAM(TCP) 기준 레코드 조회
        records = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        addresses = sorted({item[4][0] for item in records})
        return {
            "ok": True,
            "addresses": addresses
        }
    except socket.gaierror as exc:
        return {
            "ok": False,
            "error": str(exc)
        }


def tcp_check(host: str, port: int, timeout: float = 2.0) -> dict:
    """지정된 호스트와 포트로 TCP 소켓 3-Way Handshake 연결을 시도하여 연결성을 검증합니다."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {
                "ok": True,
                "host": host,
                "port": port
            }
    except (OSError, TimeoutError) as exc:
        return {
            "ok": False,
            "host": host,
            "port": port,
            "error": str(exc)
        }


def http_check(host: str, port: int, path: str = "/", timeout: float = 2.0) -> dict:
    """지정된 호스트, 포트, 경로로 HTTP GET 요청을 전송하고 상태 코드 및 본문을 수집합니다."""
    if not path.startswith("/"):
        path = "/" + path

    # IPv6 주소인 경우 URL 규격에 맞게 대괄호 처리
    formatted_host = f"[{host}]" if ":" in host and not host.startswith("[") else host
    url = f"http://{formatted_host}:{port}{path}"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "cloud-network-diagnose/1.0"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.status
            content = response.read().decode("utf-8")
            try:
                body = json.loads(content)
            except json.JSONDecodeError:
                body = content
            return {
                "ok": True,
                "status": status,
                "body": body
            }
    except urllib.error.HTTPError as exc:
        content = exc.read().decode("utf-8")
        try:
            body = json.loads(content)
        except json.JSONDecodeError:
            body = content
        return {
            "ok": False,
            "status": exc.code,
            "error": f"HTTP {exc.code} {exc.reason}",
            "body": body
        }
    except urllib.error.URLError as exc:
        return {
            "ok": False,
            "status": None,
            "error": str(exc.reason)
        }
    except Exception as exc:
        return {
            "ok": False,
            "status": None,
            "error": str(exc)
        }


def diagnose(host: str, port: int, path: str = "/") -> dict:
    """DNS 해석 -> TCP 3-Way Handshake -> HTTP 요청/응답을 순차적으로 수행하는 통합 진단 함수."""
    dns_result = resolve(host)
    tcp_result = tcp_check(host, port)

    # TCP 연결이 성공했을 때만 상위 계층인 HTTP 요청 검증 진행
    if tcp_result.get("ok"):
        http_result = http_check(host, port, path)
    else:
        http_result = {
            "ok": False,
            "status": None,
            "error": "TCP connection failed; HTTP check skipped"
        }

    return {
        "host": host,
        "port": port,
        "path": path,
        "dns": dns_result,
        "tcp": tcp_result,
        "http": http_result
    }


def main():
    """CLI 진입점: host, --port, --path 인자를 받아 진단 리포트를 JSON으로 출력합니다."""
    parser = argparse.ArgumentParser(
        description="DNS · TCP · HTTP 계층별 네트워크 진단 CLI 도구"
    )
    parser.add_argument(
        "host",
        nargs="?",
        default="127.0.0.1",
        help="진단 대상 호스트명 또는 IP (기본값: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8081,
        help="진단 대상 TCP 포트 번호 (기본값: 8081)"
    )
    parser.add_argument(
        "--path",
        default="/health",
        help="진단 대상 HTTP 경로 (기본값: /health)"
    )

    args = parser.parse_args()
    report = diagnose(args.host, args.port, args.path)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
