# 09 Terraform IaC 학습 기록

- **Terraform 버전**: Terraform v1.17.0 (darwin_arm64)
- **init 결과**: Success (`terraform.io/builtin/terraform is built in`)
- **validate 결과**: Success (`Success! The configuration is valid.`)
- **test 결과**: Success (`3 passed, 0 failed` - subnet_cidrs, resource_dependency, production_label)
- **plan 결과**: Success (`Plan: 3 to add, 0 to change, 0 to destroy.`)
- **apply 결과**: Success (`Apply complete! Resources: 3 added, 0 changed, 0 destroyed.`)
- **state list 결과**: `terraform_data.vpc`, `terraform_data.public_subnet`, `terraform_data.private_subnet` (3개 리소스 등록)
- **destroy 결과**: Success (`Destroy complete! Resources: 3 destroyed.`, state 비워짐)
- **Git commit hash**: `f545c96`
- **Git push 결과**: `origin/main` 전송 완료

## 오류 기록

| 실패 명령 | 오류 로그 | 원인 | 수정 | 재검증 |
|---|---|---|---|---|
| 없음 | - | - | - | 3/3 테스트 및 생명주기 100% 정상 통과 |
