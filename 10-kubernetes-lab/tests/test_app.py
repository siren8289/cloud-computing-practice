import importlib.util
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

module_path = Path(__file__).resolve().parents[1] / "app" / "main.py"
spec = importlib.util.spec_from_file_location("cloud_lab_app", module_path)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class AppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def get(self, path):
        url = f"http://127.0.0.1:{self.port}{path}"
        with urlopen(url, timeout=3) as response:
            return response.status, json.load(response)

    def test_health(self):
        status, body = self.get("/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_version(self):
        status, body = self.get("/")
        self.assertEqual(status, 200)
        self.assertEqual(body["version"], app.VERSION)

    def test_404(self):
        with self.assertRaises(HTTPError) as caught:
            self.get("/missing")
        self.assertEqual(caught.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
