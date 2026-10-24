"""교육용 보안 정책 시뮬레이터: IAM, Security Group, NACL 평가 엔진."""

import argparse
import fnmatch
import ipaddress
import json


def iam_decision(statements: list, action: str, resource: str) -> str:
    """IAM 정책 평가 로직: 명시적 Deny가 우선하며, 일치하는 Allow가 없으면 암시적 Deny가 됩니다."""
    effects = []
    for item in statements:
        actions = item["Action"] if isinstance(item["Action"], list) else [item["Action"]]
        resources = item["Resource"] if isinstance(item["Resource"], list) else [item["Resource"]]

        action_match = any(fnmatch.fnmatchcase(action.lower(), x.lower()) for x in actions)
        resource_match = any(fnmatch.fnmatchcase(resource, x) for x in resources)

        if action_match and resource_match:
            effects.append(item["Effect"])

    # 1. 명시적 Deny(Explicit Deny)가 단 하나라도 있으면 최종 거부
    if "Deny" in effects:
        return "EXPLICIT_DENY"
    # 2. 명시적 Allow가 존재하면 허용
    if "Allow" in effects:
        return "ALLOW"
    # 3. 아무런 정책과도 일치하지 않으면 암시적 거부(Implicit Deny, Default Deny)
    return "IMPLICIT_DENY"


def matches(rule: dict, ip: str, port: int, protocol: str = "tcp") -> bool:
    """CIDR 네트워크 범위, 포트 범위, 프로토콜 일치 여부를 검사합니다."""
    return (
        ipaddress.ip_address(ip) in ipaddress.ip_network(rule["cidr"])
        and rule["from_port"] <= port <= rule["to_port"]
        and rule.get("protocol", "tcp") == protocol
    )


def sg_allow(rules: list, ip: str, port: int, established: bool = False) -> bool:
    """Security Group 평가 (Stateful): 이미 수립된 연결의 응답은 자동 허용(established=True)됩니다."""
    return established or any(matches(rule, ip, port) for rule in rules)


def nacl_decision(rules: list, ip: str, port: int) -> tuple[str, int | None]:
    """NACL 평가 (Stateless): 낮은 규칙 번호(Rule Number)부터 순서대로 평가하여 첫 번째 일치 규칙의 액션을 반환합니다."""
    for rule in sorted(rules, key=lambda r: r["number"]):
        if matches(rule, ip, port):
            return rule["action"].upper(), rule["number"]
    # 일치하는 규칙이 없으면 기본 거부 (Default Deny)
    return "DENY", None


def evaluate_web_flow(client_ip: str = "203.0.113.10", client_port: int = 55000) -> dict:
    """웹 서버 인바운드 요청 및 클라이언트 아웃바운드 응답의 엔드투엔드 보안 흐름을 시뮬레이션합니다."""
    # 8081 포트에 대한 인바운드 보안그룹 (특정 /24 대역만 허용)
    incoming_sg = [{
        "cidr": "203.0.113.0/24",
        "from_port": 8081,
        "to_port": 8081
    }]

    # 서브넷 레벨 인바운드 NACL (8081 포트 전체 허용)
    nacl_in = [{
        "number": 100,
        "action": "allow",
        "cidr": "0.0.0.0/0",
        "from_port": 8081,
        "to_port": 8081
    }]

    # 서브넷 레벨 아웃바운드 NACL (클라이언트 임시 포트 1024~65535 허용)
    nacl_out = [{
        "number": 100,
        "action": "allow",
        "cidr": "0.0.0.0/0",
        "from_port": 1024,
        "to_port": 65535
    }]

    # 1. 인바운드 평가: NACL 인바운드 통과 AND Security Group 인바운드 통과
    inbound = (
        nacl_decision(nacl_in, client_ip, 8081)[0] == "ALLOW"
        and sg_allow(incoming_sg, client_ip, 8081)
    )

    # 2. 아웃바운드 평가: Security Group 상태 저장(established=inbound) 통과 AND NACL 아웃바운드 통과
    outbound = (
        sg_allow([], client_ip, client_port, established=inbound)
        and nacl_decision(nacl_out, client_ip, client_port)[0] == "ALLOW"
    )

    return {
        "request_allowed": inbound,
        "response_allowed": inbound and outbound
    }


def main():
    """CLI 진입점: IAM 정책 평가 및 네트워크(SG + NACL) 패킷 평가 결과를 JSON으로 출력합니다."""
    parser = argparse.ArgumentParser(
        description="IAM · Security Group · NACL 보안 정책 시뮬레이터"
    )
    parser.add_argument("--client-ip", default="203.0.113.10", help="클라이언트 IP 주소")
    parser.add_argument("--client-port", type=int, default=55000, help="클라이언트 임시 포트")
    args = parser.parse_args()

    # IAM 정책 예시: S3 버킷 전체 읽기 허용하되 private/ 경로는 명시적 거부
    policy = [
        {
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::study-bucket/*"
        },
        {
            "Effect": "Deny",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::study-bucket/private/*"
        }
    ]

    result = {
        "iam_public": iam_decision(
            policy,
            "s3:GetObject",
            "arn:aws:s3:::study-bucket/public/a.txt"
        ),
        "iam_private": iam_decision(
            policy,
            "s3:GetObject",
            "arn:aws:s3:::study-bucket/private/secret.txt"
        ),
        "network": evaluate_web_flow(args.client_ip, args.client_port)
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
