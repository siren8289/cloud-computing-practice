import os
import unittest
from monitor import inspect_process


class ProcessMonitorTest(unittest.TestCase):
    """프로세스 모니터링 함수의 동작을 검증하는 자동 단위 테스트."""

    def test_running_process(self):
        """현재 실행 중인 테스트 프로세스 자체의 PID를 전달했을 때 정상 파싱 및 상태 반환 검증"""
        current_pid = os.getpid()
        info = inspect_process(current_pid)

        self.assertTrue(info["running"])
        self.assertEqual(info["pid"], current_pid)
        self.assertIsInstance(info["ppid"], int)
        self.assertIsInstance(info["cpu_percent"], float)
        self.assertIsInstance(info["rss_kib"], int)
        self.assertGreater(info["rss_kib"], 0)
        self.assertIsInstance(info["status"], str)
        self.assertIsInstance(info["command"], str)

    def test_nonexistent_process(self):
        """존재하지 않는 가상 PID(999999)를 전달했을 때 running=False 정상 반환 검증"""
        fake_pid = 999999
        info = inspect_process(fake_pid)

        self.assertFalse(info["running"])
        self.assertEqual(info["pid"], fake_pid)


if __name__ == "__main__":
    unittest.main()
