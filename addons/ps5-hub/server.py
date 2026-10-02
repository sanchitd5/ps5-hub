#!/usr/bin/env python3
"""HTTPS entry point for PS5 Hub.

AdGuard DNS-rewrites manuals.playstation.net straight to this add-on's
IP with no port control, and the PS5 browser hardcodes HTTPS, so this
needs to answer on 443 directly to make the hostname a usable bookmark
for the dashboard. Plain static file server otherwise — each dashboard
card links out to its own plugin/add-on.
"""
import http.server
import os
import ssl
import subprocess
import tempfile

PORT = 443
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "www")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, fmt, *args):
        print("[HTTP] " + (fmt % args))


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
    httpd.serve_forever()
