# 🧪 Test & Verification Log (테스트 검증 로그)

이 문서는 실습 기능에 대한 단위·통합·수동 검증 결과, 실행 명령어, 성공/실패 여부 및 미검증 항목을 기록합니다.

---

## [2026-10-24] 01단계: HTTP 기초 서버 단위 및 통합 테스트 (준비 중)
- **작업 목적**: HTTP 서버 응답 및 상태 코드 검증
- **테스트 대상**: `01-http-server/main.py`
- **테스트 코드**: `01-http-server/test_main.py`
- **테스트 계획**:
  - `GET /health` 요청 시 200 OK 및 JSON 응답 반환 검증
  - `GET /missing` 요청 시 404 Not Found 및 오류 JSON 반환 검증
