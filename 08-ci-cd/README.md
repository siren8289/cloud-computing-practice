# 08단계: CI/CD Pipeline & GitHub Actions Automation

## 1. 학습 개요 및 목표
- **학습 주제**: CI/CD (지속적 통합 및 지속적 배포), GitHub Actions 워크플로, 파이프라인 자동화, 테스트 격리
- **비용**: 0원 (GitHub Actions 무료 티어 및 로컬 유효성 검사)
- **목표**:
  1. 개발자가 코드를 `git push`했을 때 원격 빌드 서버에서 자동으로 테스트가 실행되는 CI 파이프라인의 핵심 구조를 학습합니다.
  2. `.github/workflows/ci.yml` 파일 문법(Jobs, Steps, Runners, Actions)을 이해하고 작성합니다.
  3. 로컬 테스트 통과 여부가 원격 저장소의 배포 안전성을 어떻게 보장하는지 직접 검증합니다.
