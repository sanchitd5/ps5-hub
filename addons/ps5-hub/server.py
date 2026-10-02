#!/usr/bin/env python3
"""Entry point for PS5 Hub.

AdGuard DNS-rewrites manuals.playstation.net straight to this add-on's
IP with no port control, and the PS5 browser hardcodes HTTPS, so this
needs to answer on 443 directly to make the hostname a usable bookmark
for the dashboard. Each dashboard card used to link out to its own
plugin add-on's container; those are now vendored here instead and
each gets its own plain-HTTP listener on its own port, run as a thread
inside this one process.
"""
import http.server
import os
import posixpath
import ssl
import subprocess
import tempfile
import threading
import urllib.parse

HTTPS_PORT = 443
HTTP_PORT = 80
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(APP_DIR, "www")

# Vendored plugin file-trees, each served flat on its own port — same
# layout as when they were separate add-ons (see www/ for the dashboard).
PLUGIN_PORTS = {
    "webkit-autoloader": (8082, os.path.join(APP_DIR, "plugins", "webkit-autoloader")),
    "relapse": (8083, os.path.join(APP_DIR, "plugins", "relapse")),
    "relapse-sonic": (8084, os.path.join(APP_DIR, "plugins", "relapse-sonic")),
}


def make_static_handler(base_dir):
    class StaticHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=base_dir, **kwargs)

        def log_message(self, fmt, *args):
            print(f"[HTTP:{base_dir}] " + (fmt % args))

    return StaticHandler


class Handler(http.server.SimpleHTTPRequestHandler):
    """Static file server for the dashboard.

    The PS5's User's Guide requests /document/en/ps5/index.html (and the
    webkit-autoloader app hardcodes /app/... for its own asset paths) —
    both need to be rewritten back onto this flat www/ directory, the
    same mapping host.py's DualDirHandler does for the standalone
    PC-host build.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, fmt, *args):
        print("[HTTP] " + (fmt % args))

    def _relative_path(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]

        if path.startswith("/document/") and "/ps5/" in path:
            path = "/" + path.split("/ps5/", 1)[1]

        if path.startswith("/app/"):
            path = path[4:]

        try:
            path = urllib.parse.unquote(path, errors="surrogatepass")
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = [
            word for word in path.split("/")
            if word and not (os.path.dirname(word) or word in (os.curdir, os.pardir))
        ]
        return "/".join(words)

    def send_head(self):
        raw_path = self.path.split("?", 1)[0].split("#", 1)[0]
        rel = self._relative_path()

        candidates = [rel]
        if not rel or rel.endswith("/"):
            candidates = [rel + name for name in ("index.html", "index.htm")]

        for candidate in candidates:
            full = os.path.join(BASE_DIR, candidate)
            if os.path.isfile(full):
                self.path = "/" + candidate
                return super().send_head()

        self.send_error(404, "File not found")
        print(f"[HTTP] {self.command} {raw_path} -> Not Found")
        return None


class RedirectToHttpsHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[HTTP->HTTPS] " + (fmt % args))

    def _redirect(self):
        host = self.headers.get("Host", "").split(":", 1)[0]
        location = f"https://{host}{self.path}"
        self.send_response(301)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self):
        self._redirect()

    def do_HEAD(self):
        self._redirect()


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


def start_plugin_servers():
    for name, (port, base_dir) in PLUGIN_PORTS.items():
        if not os.path.isdir(base_dir):
            print(f"[-] Skipping plugin '{name}': {base_dir} not found")
            continue
        handler = make_static_handler(base_dir)
        httpd = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        print(f"[+] Plugin '{name}' serving {base_dir} on 0.0.0.0:{port} (HTTP)")


if __name__ == "__main__":
    cert_path, key_path = get_server_cert()
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", HTTPS_PORT), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    redirector = http.server.ThreadingHTTPServer(("0.0.0.0", HTTP_PORT), RedirectToHttpsHandler)
    threading.Thread(target=redirector.serve_forever, daemon=True).start()
    print(f"[+] Redirecting 0.0.0.0:{HTTP_PORT} -> https (HTTP)")

    start_plugin_servers()

    print(f"[+] Serving {BASE_DIR} on 0.0.0.0:{HTTPS_PORT} (HTTPS)")
    httpd.serve_forever()
