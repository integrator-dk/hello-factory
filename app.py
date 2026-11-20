"""hello-factory: the smallest possible solution under Integrator Software Factory.

It exists to prove the whole path end to end: repo -> pipeline -> "Ny version klar" in
Factory -> blue/green deploy on a Docker host -> Entra login -> health checks.
"""

import html
import json
import os
import socket
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = os.getenv("APP_VERSION", "dev")
STARTED = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

PAGE = """<!doctype html><html lang="da"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>hello-factory</title>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@600&family=Open+Sans&display=swap" rel="stylesheet">
<style>body{{margin:0;font-family:'Open Sans',sans-serif;background:#F4F6F9;color:#1F2A47}}
header{{background:#1F2A47;color:#fff;padding:14px 24px;font-family:Barlow,sans-serif;font-size:18px}}
main{{max-width:640px;margin:40px auto;background:#fff;border:1px solid #E2E6EE;border-top:4px solid #007F83;border-radius:10px;padding:24px}}
h1{{font-family:Barlow,sans-serif;margin:0 0 8px}} .v{{color:#E6007E;font-weight:600}} dt{{color:#66708A}} dd{{margin:0 0 8px;font-weight:600}}</style>
</head><body><header>Integrator <strong>hello-factory</strong></header><main>
<h1>Hej{name} 👋</h1><p>Denne løsning (blå/grøn-testet) kører på en Docker-host, som Integrator Software Factory administrerer.</p>
<dl><dt>Version</dt><dd class="v">{version}</dd><dt>Container</dt><dd>{host}</dd><dt>Startet</dt><dd>{started}</dd></dl>
</main></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == "/healthz":
            self._send(200, "application/json", json.dumps({"status": "ok", "version": VERSION}))
            return
        email = self.headers.get("X-Auth-Request-Email", "")
        name = f", {html.escape(email.split('@')[0].split('.')[0].title())}" if email else ""
        self._send(200, "text/html; charset=utf-8",
                   PAGE.format(name=name, version=html.escape(VERSION), host=socket.gethostname(), started=STARTED))

    def _send(self, status, ctype, body):
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        if "/healthz" not in (args[0] if args else ""):
            super().log_message(fmt, *args)


def main():
    ThreadingHTTPServer(("0.0.0.0", int(os.getenv("PORT", "8080"))), Handler).serve_forever()


if __name__ == "__main__":
    main()
