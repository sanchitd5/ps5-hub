#!/usr/bin/env python3
"""HTTPS entry point for PS5 Hub.

AdGuard DNS-rewrites manuals.playstation.net straight to this add-on's
IP with no port control, and the PS5's User's Guide hardcodes HTTPS, so
this is the only thing that can answer that request. PS5's own exploit
paths (/document/.../ps5/..., /app/...) get redirected on to
ps5-webkit-server, which does the real path-rewriting and serves the
built exploit files; every other request gets the plugin dashboard.
"""
import http.server
import os
import ssl
import subprocess
import sys
import tempfile

PORT = 443
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "www")
TARGET = os.environ.get("EXPLOIT_REDIRECT_URL", "").rstrip("/")


def is_exploit_path(path):
    return path.startswith("/document/") or path.startswith("/app/") or path.rstrip("/").endswith("selected_exploit")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, fmt, *args):
        print("[HTTP] " + (fmt % args))

    def do_GET(self):
        if TARGET and is_exploit_path(self.path):
            location = TARGET + self.path
            self.send_response(302)
            self.send_header("Location", location)
            self.end_headers()
            print(f"[HTTP] {self.command} {self.path} -> 302 {location}")
            return
        super().do_GET()


def get_server_cert():
    tmpdir = tempfile.mkdtemp(prefix="ps5-hub-")
    cert_path = os.path.join(tmpdir, "cert.pem")
    key_path = os.path.join(tmpdir, "key.pem")
    subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-nodes", "-days", "3650", "-sha256",
            "-keyout", key_path, "-out", cert_path,
            "-subj", "/CN=manuals.playstation.net",
        ],
        check=True,
        capture_output=True,
    )
    return cert_path, key_path


if __name__ == "__main__":
    cert_path, key_path = get_server_cert()
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    print(f"[+] Serving {BASE_DIR} on 0.0.0.0:{PORT} (HTTPS)")
    if TARGET:
        print(f"[+] Exploit paths redirect to {TARGET}")
    else:
        print("[-] exploit_redirect_url not set — exploit paths will fall through to the dashboard 404.", file=sys.stderr)
    httpd.serve_forever()
