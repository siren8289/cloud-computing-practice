import unittest
from planner import plan, select_route


class PlannerTest(unittest.TestCase):
    """VPC 서브넷 유효성 검증, 중복 충돌 감지, Longest Prefix Match 라우팅을 검증하는 자동 단위 테스트."""

    def test_valid_plan(self):
        """정상적인 VPC 및 서브넷 분할 시 총 주소 수 및 AWS 가용 주소 수(-5) 계산 검증"""
        result = plan(
            "10.0.0.0/16",
            {"public": "10.0.1.0/24", "private": "10.0.2.0/24"}
        )
        subnet = result["subnets"][0]
        self.assertEqual(subnet["total_addresses"], 256)
        self.assertEqual(subnet["aws_usable_ipv4"], 251)

    def test_overlap_rejected(self):
        """동일 대역 내 서브넷 주소 범위가 중첩(Overlap)될 때 ValueError 발생 검증"""
        with self.assertRaisesRegex(ValueError, "overlaps"):
            plan(
                "10.0.0.0/16",
                {"first": "10.0.1.0/24", "second": "10.0.1.128/25"}
            )

    def test_outside_vpc_rejected(self):
        """VPC CIDR 범위를 벗어난 서브넷 지정 시 ValueError 발생 검증"""
        with self.assertRaisesRegex(ValueError, "outside"):
            plan("10.0.0.0/16", {"bad": "10.1.0.0/24"})

    def test_longest_prefix(self):
        """최장 접두사 일치(Longest Prefix Match) 원리에 따른 라우팅 우선순위 선택 검증"""
        routes = {
            "0.0.0.0/0": "igw",
            "10.0.0.0/16": "local",
            "10.0.2.0/24": "specific"
        }
        # 10.0.2.15는 /0, /16, /24 모두 매칭되나 가장 구체적인 /24(specific) 선택
        self.assertEqual(
            select_route("10.0.2.15", routes)["target"], "specific"
        )
        # 10.0.3.15는 /0, /16 매칭 중 더 구체적인 /16(local) 선택
        self.assertEqual(
            select_route("10.0.3.15", routes)["target"], "local"
        )
        # 8.8.8.8은 /0(igw)만 매칭
        self.assertEqual(
            select_route("8.8.8.8", routes)["target"], "igw"
        )

    def test_no_matching_route(self):
        """일치하는 라우팅 규칙이 없을 때 None 반환 검증"""
        result = select_route("8.8.8.8", {"10.0.0.0/16": "local"})
        self.assertIsNone(result)

    def test_invalid_network(self):
        """호스트 비트가 포함된 잘못된 CIDR 표기 시 ValueError 발생 검증"""
        with self.assertRaises(ValueError):
            plan("10.0.0.0/16", {"bad": "10.0.1.7/24"})


if __name__ == "__main__":
    unittest.main()
