# 09단계: Terraform & Infrastructure as Code (IaC)

## 1. 개요 및 학습 목표
- **학습 주제**: Terraform 기초, IaC(코드로서의 인프라), `init` → `validate` → `plan` → `apply` 수명주기
- **비용**: 0원 (로컬 파일/도커 프로바이더 중심 PoC)
- **목표**:
  1. 클라우드 인프라 자원을 코드로 선언하고 버전 관리하는 IaC의 기본 철학을 학습합니다.
  2. HCL(HashiCorp Configuration Language) 문법과 상태 파일(`terraform.tfstate`)의 역할을 이해합니다.
  3. 로컬 환경에서 비용 없이 인프라 생성 및 변경 계획(`plan`)을 검증합니다.
