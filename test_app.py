import json
import threading
import unittest
import urllib.request
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer

import app


class FooterLinks(HTMLParser):
    """Collects (href, text) for every anchor inside a <footer>."""

    def __init__(self):
        super().__init__()
        self.links, self._footer, self._href, self._text = [], 0, None, []

    def handle_starttag(self, tag, attrs):
        if tag == "footer":
            self._footer += 1
        elif tag == "a" and self._footer:
            self._href, self._text = dict(attrs).get("href"), []

    def handle_endtag(self, tag):
        if tag == "footer":
            self._footer -= 1
        elif tag == "a" and self._href is not None:
            self.links.append((self._href, "".join(self._text).strip()))
            self._href = None

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)


class ElementAfterHeading(HTMLParser):
    """Records the first element that follows the page's <h1>, with its class and text."""

    def __init__(self):
        super().__init__()
        self.tag, self.cls, self._state, self._text = None, None, "before", []

    def handle_starttag(self, tag, attrs):
        if self._state == "before" and tag == "h1":
            self._state = "in_h1"
        elif self._state == "after_h1":
            self.tag, self.cls, self._state = tag, dict(attrs).get("class"), "in_next"

    def handle_endtag(self, tag):
        if self._state == "in_h1" and tag == "h1":
            self._state = "after_h1"
        elif self._state == "in_next" and tag == self.tag:
            self._state = "done"

    def handle_data(self, data):
        if self._state == "in_next":
            self._text.append(data)

    @property
    def text(self):
        return "".join(self._text).strip()


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

    def test_page_shows_tagline_directly_under_heading(self):
        with urllib.request.urlopen(self.base + "/") as r:
            body = r.read().decode()
        self.assertIn("Built and run by Integrator Software Factory", body)
        parser = ElementAfterHeading()
        parser.feed(body)
        self.assertEqual((parser.tag, parser.cls, parser.text),
                         ("p", "tagline", "Built and run by Integrator Software Factory"))

    def test_healthz_body_unchanged(self):
        with urllib.request.urlopen(f"{self.base}/healthz") as r:
            self.assertEqual(r.headers["Content-Type"], "application/json")
            self.assertEqual(json.loads(r.read()), {"status": "ok", "version": app.VERSION})

    def test_page_footer_links_to_health_check(self):
        with urllib.request.urlopen(self.base + "/") as r:
            parser = FooterLinks()
            parser.feed(r.read().decode())
        self.assertIn(("/healthz", "Health"), parser.links)


if __name__ == "__main__":
    unittest.main()
