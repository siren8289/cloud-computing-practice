"""오프라인 YAML 구조 테스트."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ManifestTest(unittest.TestCase):
    def test_deployment_replica_and_readiness(self):
        text = (ROOT / "k8s/deployment.yaml").read_text()
        self.assertIn("replicas: 2", text)
        self.assertIn("readinessProbe:", text)
        self.assertIn("maxUnavailable: 0", text)

    def test_service_selector(self):
        dep = (ROOT / "k8s/deployment.yaml").read_text()
        svc = (ROOT / "k8s/service.yaml").read_text()
        self.assertIn("app: gitops-web", dep)
        self.assertIn("app: gitops-web", svc)
        self.assertIn("type: ClusterIP", svc)

    def test_argocd_policy_and_repo(self):
        app = (ROOT / "application.yaml").read_text()
        self.assertIn("selfHeal: true", app)
        self.assertIn("enabled: true", app)
        self.assertIn("prune: false", app)
        self.assertIn("12-gitops-argocd/k8s", app)
        self.assertIn("cloud-computing-practice.git", app)


if __name__ == "__main__":
    unittest.main()
