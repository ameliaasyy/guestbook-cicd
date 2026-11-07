import json, os, threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DATA_DIR = os.environ.get("DATA_DIR", "/var/lib/backend_data")
DATA_FILE = os.path.join(DATA_DIR, "guestbook.json")
lock = threading.Lock()

def load():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/messages":
            with lock:
                self._send(200, load())
        else:
            self._send(404, {"error": "Not found"})

    def do_POST(self):
        if urlparse(self.path).path != "/messages":
            return self._send(404, {"error": "Not found"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
            name = str(payload.get("name", "")).strip()
            message = str(payload.get("message", "")).strip()
        except (ValueError, AttributeError, TypeError):
            return self._send(400, {"error": "Invalid JSON"})
        if not name or not message:
            return self._send(400, {"error": "name and message are required"})
        entry = {"name": name, "message": message,
                 "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        with lock:
            data = load()
            data.append(entry)
            save(data)
        self._send(201, entry)

    def do_DELETE(self):
        url = urlparse(self.path)
        if url.path != "/messages":
            return self._send(404, {"error": "Not found"})
        try:
            index = int(parse_qs(url.query)["index"][0])
        except (KeyError, ValueError):
            return self._send(400, {"error": "index query param (integer) required"})
        with lock:
            data = load()
            if index < 0 or index >= len(data):
                return self._send(404, {"error": "Index not found"})
            removed = data.pop(index)
            save(data)
        self._send(200, {"deleted": removed})

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
