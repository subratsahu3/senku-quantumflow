"""
QuantumFlow - Real-Time Multiverse Telemetry Server.

Zero-dependency HTTP & SSE server using standard library.
Serves a responsive Cyberpunk visualizer displaying real-time timeline branches,
superposition states, and wavefunction collapses.
"""

from __future__ import annotations
import json
import os
import queue
import threading
import time
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
from urllib.parse import urlparse, parse_qs

from quantumflow.core.multiverse import Multiverse


class SSEBroadcaster:
    """Manages Server-Sent Event (SSE) client queues."""
    def __init__(self):
        self._clients: list[queue.Queue] = []
        self._lock = threading.Lock()

    def subscribe(self) -> queue.Queue:
        q = queue.Queue(maxsize=100)
        with self._lock:
            self._clients.append(q)
        return q

    def unsubscribe(self, q: queue.Queue) -> None:
        with self._lock:
            if q in self._clients:
                self._clients.remove(q)

    def broadcast(self, event_name: str, data: dict) -> None:
        payload = f"event: {event_name}\ndata: {json.dumps(data)}\n\n"
        with self._lock:
            for q in list(self._clients):
                try:
                    q.put_nowait(payload)
                except queue.Full:
                    pass


class MultiverseHTTPHandler(BaseHTTPRequestHandler):
    """Handles static files, REST state queries, and SSE streaming."""

    multiverse: Optional[Multiverse] = None
    broadcaster: Optional[SSEBroadcaster] = None
    static_dir: str = ""

    def log_message(self, format, *args):
        # Silence default HTTP access logs to keep terminal clean
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self._serve_file("index.html", "text/html; charset=utf-8")
        elif path == "/style.css":
            self._serve_file("style.css", "text/css; charset=utf-8")
        elif path == "/app.js":
            self._serve_file("app.js", "application/javascript; charset=utf-8")
        elif path == "/api/state":
            self._serve_json(self.multiverse.get_topology() if self.multiverse else {})
        elif path == "/api/events":
            self._serve_sse()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/action/simulate":
            # Handled by demo loop or action dispatcher
            self._serve_json({"status": "acknowledged", "timestamp": time.time()})
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def _serve_file(self, filename: str, content_type: str):
        filepath = os.path.join(self.static_dir, filename)
        if not os.path.exists(filepath):
            self.send_error(HTTPStatus.NOT_FOUND, f"File {filename} not found")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def _serve_json(self, data: dict):
        body = json.dumps(data).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _serve_sse(self):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        client_queue = self.broadcaster.subscribe()
        try:
            # Send initial greeting
            self.wfile.write(b"event: connected\ndata: {\"status\":\"connected\"}\n\n")
            self.wfile.flush()
            while True:
                try:
                    msg = client_queue.get(timeout=20.0)
                    self.wfile.write(msg.encode("utf-8"))
                    self.wfile.flush()
                except queue.Empty:
                    # Heartbeat
                    self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self.broadcaster.unsubscribe(client_queue)


class DashboardServer:
    """Spins up background HTTP & SSE server."""

    def __init__(self, multiverse: Multiverse, port: int = 8080):
        self.multiverse = multiverse
        self.port = port
        self.broadcaster = SSEBroadcaster()
        self.static_dir = os.path.join(os.path.dirname(__file__), "static")
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

        # Wire multiverse events directly to SSE broadcast
        self.multiverse.subscribe(self._on_multiverse_event)

    def _on_multiverse_event(self, event_data: dict):
        self.broadcaster.broadcast(event_data.get("event", "update"), event_data)

    def start(self, daemon: bool = True):
        handler = MultiverseHTTPHandler
        handler.multiverse = self.multiverse
        handler.broadcaster = self.broadcaster
        handler.static_dir = self.static_dir

        self._server = HTTPServer(("127.0.0.1", self.port), handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=daemon)
        self._thread.start()
        print(f"[*] QuantumFlow Multiverse Visualizer running on http://127.0.0.1:{self.port}")

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            print("[*] Dashboard server stopped.")
