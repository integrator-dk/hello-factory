import json
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

import app


class AppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_healthz(self):
        with urllib.request.urlopen(f"{self.base}/healthz") as r:
            self.assertEqual(r.status, 200)
            self.assertEqual(json.loads(r.read())["status"], "ok")

    def test_page_greets_logged_in_user(self):
        req = urllib.request.Request(self.base + "/", headers={"X-Auth-Request-Email": "allan.frost@integrator.dk"})
        with urllib.request.urlopen(req) as r:
            self.assertIn("Hej, Allan", r.read().decode())

    def test_page_footer_shows_running_version(self):
        original = app.VERSION
        app.VERSION = "1.1.1"
        try:
            with urllib.request.urlopen(self.base + "/") as r:
                body = r.read().decode()
        finally:
            app.VERSION = original
        self.assertRegex(body, r"<footer[^>]*>hello-factory 1\.1\.1</footer>")

    def test_healthz_unchanged(self):
        with urllib.request.urlopen(f"{self.base}/healthz") as r:
            self.assertEqual(r.headers["Content-Type"], "application/json")
            self.assertEqual(json.loads(r.read()), {"status": "ok", "version": app.VERSION})


if __name__ == "__main__":
    unittest.main()
