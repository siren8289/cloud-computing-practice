import argparse
import ipaddress
import json


def parse_network(cidr: str) -> ipaddress.IPv4Network:
    """CIDR 문자열을 검증하여 IPv4Network 객체로 파싱합니다 (호스트 비트 설정 시 에러 발생)."""
    return ipaddress.IPv4Network(cidr, strict=True)


def plan(vpc_cidr: str, subnets: dict) -> dict:
    """VPC 및 하위 서브넷들의 CIDR 유효성, 범위 포함 여부, 중복 충돌을 검증하고 주소 용량을 산출합니다."""
    vpc = parse_network(vpc_cidr)
    parsed = []

    for name, cidr in subnets.items():
        network = parse_network(cidr)

        # 1. 서브넷이 VPC 주소 범위 내부에 완전히 포함되는지 검사
        if not network.subnet_of(vpc):
            raise ValueError(f"{name}: {network} is outside {vpc}")

        # 2. 이미 등록된 다른 서브넷과 IP 대역이 겹치는지(Overlap) 검사
        for existing_name, existing in parsed:
            if network.overlaps(existing):
                raise ValueError(f"{name} overlaps {existing_name}")

        parsed.append((name, network))

    return {
        "vpc": str(vpc),
        "subnets": [
            {
                "name": name,
                "cidr": str(net),
                "total_addresses": net.num_addresses,
                # AWS 서브넷은 네트워크/브로드캐스트 및 내부 예약 주소 5개를 제외함
                "aws_usable_ipv4": net.num_addresses - 5,
            }
            for name, net in parsed
        ],
    }


def select_route(destination: str, routes: dict) -> dict | None:
    """목적지 IP에 대해 Longest Prefix Match(가장 긴 서브넷 마스크 우선) 원리를 적용하여 최적 라우팅 경로를 선택합니다."""
    address = ipaddress.IPv4Address(destination)
    matches = []

    # 목적지 IP가 포함되는 모든 라우팅 규칙 추출
    for cidr, target in routes.items():
        network = parse_network(cidr)
        if address in network:
            matches.append((network.prefixlen, str(network), target))

    if not matches:
        return None

    # 가장 긴 접두사(가장 구체적인 서브넷)를 갖는 규칙 선택 (Longest Prefix Match)
    max_prefix = max(item[0] for item in matches)
    winners = [
        (cidr, target)
        for length, cidr, target in matches
        if length == max_prefix
    ]

    if len(winners) != 1:
        raise ValueError("Ambiguous routes with equal prefix lengths")

    cidr, target = winners[0]
    return {
        "destination": destination,
        "matched_cidr": cidr,
        "target": target,
    }


def main():
    """CLI 진입점: VPC 서브넷 계획을 수립하고 목적지 IP에 대한 라우팅 시뮬레이션 결과를 JSON으로 출력합니다."""
    parser = argparse.ArgumentParser(
        description="Local VPC and IPv4 routing planner (CIDR & Longest Prefix Match)"
    )
    parser.add_argument(
        "--destination",
        default="10.0.2.15",
        help="라우팅 판별 대상 목적지 IPv4 주소 (기본값: 10.0.2.15)"
    )
    args = parser.parse_args()

    vpc = "10.0.0.0/16"
    subnets = {
        "public": "10.0.1.0/24",
        "private": "10.0.2.0/24"
    }
    routes = {
        "0.0.0.0/0": "igw",
        "10.0.0.0/16": "local",
        "10.0.2.0/24": "specific"
    }

    result = plan(vpc, subnets)
    result["route"] = select_route(args.destination, routes)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
