# 05단계: VPC Network Planner PoC (VPC · Subnet · CIDR · Routing)

> **실습 목표**: Python 표준 라이브러리 `ipaddress`를 활용하여 클라우드 가상 사설망(VPC)의 CIDR 블록 설계, 서브넷 분할 및 중복 충돌 감지, 그리고 패킷 전달의 핵심 원리인 **Longest Prefix Match(최장 접두사 일치)** 라우팅 알고리즘을 로컬 환경에서 직접 모델링하고 검증한다.

---

## 📌 1. 핵심 학습 개념

- **VPC (Virtual Private Cloud)**: 클라우드 상에서 고객 전용으로 논리적으로 격리된 가상 프라이빗 네트워크 (`10.0.0.0/16`)
- **CIDR (Classless Inter-Domain Routing)**: IP 주소와 네트워크 프리픽스 길이를 `/16`, `/24`로 표현하는 표준 표기법
- **AWS 예약 주소 (-5개)**: AWS 서브넷에서는 전체 IPv4 주소($2^{32-p}$) 중 처음 4개(네트워크 주소, VPC 라우터, DNS, 향후 예약)와 마지막 1개(브로드캐스트) 등 총 5개를 시스템이 예약하므로, 할당 가능한 IP는 `전체 - 5`개가 됨
- **Longest Prefix Match**: 목적지 IP가 라우트 테이블의 여러 CIDR 규칙에 매칭될 때, 가장 구체적이고 프리픽스가 긴(서브넷 마스크 비트 수가 큰) 규칙을 최우선 적용하는 인터넷 라우팅의 대원칙

---

## 🚀 2. 실행 방법 (Mac zsh)

### 1) 기본 VPC 설계 및 목적지 라우팅 검증
```zsh
cd 05-vpc-network-planner
python3 planner.py
```
출력 예시:
```json
{
  "vpc": "10.0.0.0/16",
  "subnets": [
    {
      "name": "public",
      "cidr": "10.0.1.0/24",
      "total_addresses": 256,
      "aws_usable_ipv4": 251
    },
    {
      "name": "private",
      "cidr": "10.0.2.0/24",
      "total_addresses": 256,
      "aws_usable_ipv4": 251
    }
  ],
  "route": {
    "destination": "10.0.2.15",
    "matched_cidr": "10.0.2.0/24",
    "target": "specific"
  }
}
```

### 2) 다른 목적지 IP 라우팅 시뮬레이션
```zsh
# VPC 내부 다른 대역 (10.0.0.0/16 local 라우트 매칭)
python3 planner.py --destination 10.0.3.15

# 외부 공인 인터넷 주소 (0.0.0.0/0 igw 라우트 매칭)
python3 planner.py --destination 8.8.8.8
```

---

## 🧪 3. 자동 단위 테스트 실행

```zsh
cd 05-vpc-network-planner
python3 -m unittest -v test_planner.py
```

### 검증 기준 (6건)
- `test_valid_plan`: 정상 서브넷 분할 및 AWS 가용 주소 수(251개) 검증
- `test_overlap_rejected`: 서브넷 간 주소 중복 시 `ValueError("overlaps")` 발생
- `test_outside_vpc_rejected`: VPC 범위를 벗어난 서브넷 설정 차단
- `test_longest_prefix`: Longest Prefix Match 우선순위(/24 > /16 > /0) 검증
- `test_no_matching_route`: 일치하는 경로 부재 시 `None` 반환
- `test_invalid_network`: 비트 오류가 있는 잘못된 CIDR 표기 차단
- 6건 모두 `OK`
