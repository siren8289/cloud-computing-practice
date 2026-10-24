import argparse
import json
import os
import subprocess


def inspect_process(pid: int) -> dict:
    """운영체제(OS/커널)에 특정 PID의 프로세스 상태를 요청하여 자원 정보를 반환합니다.
    
    macOS/Linux의 `ps` 명령어를 호출하여 PID, 부모 프로세스 ID(PPID), CPU 사용률(%CPU),
    물리 메모리 상주량(RSS, KiB), 프로세스 상태 코드(STAT), 실행 명령어를 파싱합니다.
    """
    # 1. 운영체제에 프로세스 상태를 요청 (외부 시스템 명령어 실행)
    result = subprocess.run(
        [
            "ps", "-p", str(pid),
            "-o", "pid=,ppid=,%cpu=,rss=,stat=,comm="
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    # 2. 프로세스가 존재하지 않거나 비정상 종료된 경우
    if result.returncode != 0 or not result.stdout.strip():
        return {
            "pid": pid,
            "running": False
        }

    # 3. ps 출력 문자열을 공백 기준으로 분할하여 6개 필드로 매핑
    fields = result.stdout.strip().split(None, 5)
    if len(fields) != 6:
        raise ValueError(f"Unexpected ps output: {result.stdout!r}")

    actual_pid, ppid, cpu, rss, status, command = fields
    return {
        "pid": int(actual_pid),
        "ppid": int(ppid),
        "cpu_percent": float(cpu),
        "rss_kib": int(rss),
        "status": status,
        "command": command,
        "running": True,
    }


def main():
    """CLI 진입점: 터미널 인자로 PID를 받아 프로세스 정보를 JSON 형식으로 출력합니다."""
    parser = argparse.ArgumentParser(
        description="서버 프로세스 모니터 CLI (PID, CPU, 메모리, 상태 조회)"
    )
    parser.add_argument(
        "pid",
        type=int,
        nargs="?",
        default=os.getpid(),
        help="모니터링할 프로세스 ID (기본값: 현재 실행 중인 monitor.py 프로세스 PID)"
    )
    args = parser.parse_args()

    info = inspect_process(args.pid)
    print(json.dumps(info, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
