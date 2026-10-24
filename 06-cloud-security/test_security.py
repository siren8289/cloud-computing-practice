import unittest
from security import (
    evaluate_web_flow,
    iam_decision,
    nacl_decision,
    sg_allow,
)


class SecurityTest(unittest.TestCase):
    """IAM 권한 판단, Security Group(Stateful), NACL(Stateless) 평가 엔진을 검증하는 자동 단위 테스트."""

    def setUp(self):
        self.policy = [
            {
                "Effect": "Allow",
                "Action": "s3:Get*",
                "Resource": "*"
            },
            {
                "Effect": "Deny",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::private/*"
            }
        ]

    def test_iam_allow(self):
        """허용 정책과 일치하고 Deny가 없을 때 ALLOW 반환 검증"""
        result = iam_decision(
            self.policy,
            "s3:GetObject",
            "arn:aws:s3:::public/a"
        )
        self.assertEqual(result, "ALLOW")

    def test_iam_explicit_deny(self):
        """Allow 규칙이 있더라도 명시적 Deny 규칙에 매칭되면 EXPLICIT_DENY 반환 검증"""
        result = iam_decision(
            self.policy,
            "s3:GetObject",
            "arn:aws:s3:::private/a"
        )
        self.assertEqual(result, "EXPLICIT_DENY")

    def test_iam_implicit_deny(self):
        """정책 목록 중 일치하는 규칙이 전혀 없을 때 기본 암시적 거부(IMPLICIT_DENY) 반환 검증"""
        result = iam_decision(
            self.policy,
            "s3:DeleteObject",
            "x"
        )
        self.assertEqual(result, "IMPLICIT_DENY")

    def test_sg_stateful(self):
        """Security Group 상태 저장(Stateful) 검증: established=True 시 아웃바운드 규칙 없이도 허용"""
        self.assertFalse(
            sg_allow([], "203.0.113.10", 55000)
        )
        self.assertTrue(
            sg_allow([], "203.0.113.10", 55000, established=True)
        )

    def test_sg_cidr(self):
        """Security Group CIDR 및 포트 매칭 검증: 허용 대역 내부 IP만 허용"""
        rules = [{
            "cidr": "203.0.113.0/24",
            "from_port": 443,
            "to_port": 443
        }]
        self.assertTrue(sg_allow(rules, "203.0.113.2", 443))
        self.assertFalse(sg_allow(rules, "198.51.100.2", 443))

    def test_nacl_order(self):
        """NACL 규칙 번호 우선순위 검증: 100(Deny)이 200(Allow)보다 낮은 번호이므로 먼저 적용됨"""
        rules = [
            {
                "number": 200,
                "action": "allow",
                "cidr": "0.0.0.0/0",
                "from_port": 8081,
                "to_port": 8081
            },
            {
                "number": 100,
                "action": "deny",
                "cidr": "203.0.113.0/24",
                "from_port": 8081,
                "to_port": 8081
            }
        ]
        self.assertEqual(
            nacl_decision(rules, "203.0.113.5", 8081),
            ("DENY", 100)
        )
        self.assertEqual(
            nacl_decision(rules, "198.51.100.5", 8081),
            ("ALLOW", 200)
        )

    def test_nacl_default_deny(self):
        """NACL 규칙 불일치 시 기본 거부(DENY, None) 반환 검증"""
        self.assertEqual(
            nacl_decision([], "203.0.113.5", 8081),
            ("DENY", None)
        )

    def test_end_to_end(self):
        """NACL + Security Group 결합 엔드투엔드 트래픽 검증"""
        # 1. 정상 인바운드 및 아웃바운드 허용 케이스
        self.assertEqual(
            evaluate_web_flow(),
            {
                "request_allowed": True,
                "response_allowed": True
            }
        )
        # 2. 허용되지 않은 클라이언트 IP (인바운드에서 차단)
        self.assertEqual(
            evaluate_web_flow("198.51.100.10"),
            {
                "request_allowed": False,
                "response_allowed": False
            }
        )
        # 3. 인바운드는 통과했으나 NACL 아웃바운드 임시 포트(1024~65535) 미허용 케이스 (port 80)
        self.assertEqual(
            evaluate_web_flow(client_port=80),
            {
                "request_allowed": True,
                "response_allowed": False
            }
        )


if __name__ == "__main__":
    unittest.main()
