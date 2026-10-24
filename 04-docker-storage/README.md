# 04단계: Docker 컨테이너 및 볼륨 영속성 PoC (가상화 · 스토리지)

> **실습 목표**: 애플리케이션을 Docker 이미지로 빌드하고 컨테이너로 격리 실행하며, 호스트 포트 포워딩(`127.0.0.1:8081:8081`) 및 Docker Named Volume(`notes_data:/data`)을 통해 컨테이너가 삭제되어도 데이터가 안전하게 보존되는 영속성(Persistence)을 검증한다.

---

## 📌 1. 핵심 학습 개념

- **Docker Image vs Container**: 이미지는 불변(Immutable)의 실행 템플릿(코드+런타임+설정), 컨테이너는 이미지 위에 얇은 임시 쓰기 계층(R/W Layer)을 얹어 실행되는 격리 프로세스
- **Port Mapping (`127.0.0.1:8081:8081`)**: Mac 호스트의 127.0.0.1:8081로 들어오는 패킷을 Docker 브리지 가상 네트워크를 통해 컨테이너의 8081 포트로 NAT 포워딩
- **Docker Named Volume (`notes_data:/data`)**: 컨테이너의 수명주기(Lifecycle)와 무관하게 호스트 스토리지 영역에 영구 보존되는 전용 볼륨 마운트

---

## 🚀 2. 실행 및 검증 방법 (Mac zsh)

### 1) 단위 테스트 (로컬 Python 검증)
```zsh
cd 04-docker-storage
python3 -m unittest -v test_main.py
```

### 2) Docker Compose 컨테이너 빌드 및 실행
```zsh
cd 04-docker-storage
# 이미지 빌드 및 백그라운드 기동
docker compose up -d --build

# 컨테이너 상태 확인
docker compose ps
```

### 3) 데이터 영속성 3단계 검증 (엔드투엔드)
```zsh
# Step A: 헬스체크 확인
curl -i http://127.0.0.1:8081/health

# Step B: 볼륨에 데이터 저장 (POST /note)
curl -i -X POST http://127.0.0.1:8081/note \
  -H "Content-Type: application/json" \
  -d '{"note":"persist-me"}'

# Step C: 컨테이너 완전 삭제 (볼륨은 보존)
docker compose down

# Step D: 새 컨테이너 생성 및 기존 데이터 재조회 (영속성 확인!)
docker compose up -d
curl -i http://127.0.0.1:8081/note
# {"note": "persist-me"} 응답 확인!

# 정리 (실습 완료 후 컨테이너 및 볼륨 정리 시)
docker compose down -v
```
