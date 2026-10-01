from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

LEVEL = {
    "width": 3300,
    "flag": 3150,
    "ground": [[0, 900], [1000, 1500], [1600, 2300], [2400, 3300]],
    "bricks": [
        [300, 290, 96], [500, 230, 96], [700, 290, 128], [1100, 300, 96],
        [1250, 240, 96], [1700, 300, 128], [1900, 240, 96], [2100, 300, 96],
        [2600, 290, 128], [2800, 230, 96],
    ],
    "pipes": [[600, 338, 48, 48], [1400, 338, 48, 48], [2000, 322, 48, 64], [2900, 322, 48, 64]],
    "coins": [
        [320, 250], [350, 250], [380, 250], [520, 190], [550, 190], [720, 250],
        [760, 250], [1120, 260], [1270, 200], [1300, 200], [1720, 260], [1760, 260],
        [1920, 200], [1950, 200], [2120, 260], [2620, 250], [2660, 250],
        [2820, 190], [2850, 190],
    ],
    "enemies": [[450, 340], [800, 340], [1200, 340], [1700, 340], [1850, 340], [2200, 340], [2700, 340]],
}

SCORES = []  # disimpan di memori (bisa reset di serverless Vercel)


class handler(BaseHTTPRequestHandler):
    def _send(self, code, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        action = q.get("action", ["level"])[0]
        if action == "scores":
            self._send(200, {"top": SCORES[:5]})
        else:
            self._send(200, LEVEL)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
            name = str(data.get("name", "Player"))[:12] or "Player"
            score = max(0, min(int(data.get("score", 0)), 1000000))
        except Exception:
            self._send(400, {"error": "data tidak valid"})
            return
        SCORES.append({"name": name, "score": score})
        SCORES.sort(key=lambda s: s["score"], reverse=True)
        del SCORES[10:]
        self._send(200, {"top": SCORES[:5]})
