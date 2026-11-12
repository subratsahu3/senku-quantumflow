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
        content_length = int(self.headers.get("Content-Length", 0))
        body = {}
        if content_length > 0:
            raw_body = self.rfile.read(content_length)
            try:
                body = json.loads(raw_body.decode("utf-8"))
            except Exception:
                body = {}

        if parsed.path == "/api/action/chaos":
            chaos_type = body.get("type", "LATENCY_SPIKE")
            report = self.multiverse.inject_chaos("random", chaos_type) if self.multiverse else None
            self._serve_json({"status": "ok", "report": report})
        elif parsed.path == "/api/action/spawn":
            # Spawn interactive speculative race
            if self.multiverse:
                async def _interactive_race():
                    import random
                    req_id = random.randint(1000, 9999)
                    tasks = {
                        f"HyperSpeed-{req_id}": lambda tl: self._task_speed(tl),
                        f"DeepVerify-{req_id}": lambda tl: self._task_verify(tl),
                        f"ShadowCache-{req_id}": lambda tl: self._task_cache(tl),
                    }
                    from quantumflow import CollapseStrategy
                    await self.multiverse.run_superposition(tasks, strategy=CollapseStrategy.FASTEST_VALID)

                # Schedule in background thread
                threading.Thread(target=lambda: asyncio.run(_interactive_race()), daemon=True).start()
            self._serve_json({"status": "spawned", "timestamp": time.time()})
        elif parsed.path == "/api/action/conflicts":
            conflicts = self.multiverse.inspect_conflicts() if self.multiverse else []
            self._serve_json({"conflicts": conflicts, "count": len(conflicts)})
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    @staticmethod
    async def _task_speed(tl):
        import asyncio, random
        await asyncio.sleep(random.uniform(0.03, 0.08))
        if random.random() < 0.3:
            raise RuntimeError("Jitter timeout on primary trunk")
        tl.mutate("route", "HyperSpeed-Direct")
        tl.metrics["alpha"] = 92
        return "SUCCESS"

    @staticmethod
    async def _task_verify(tl):
        import asyncio, random
        await asyncio.sleep(random.uniform(0.05, 0.12))
        tl.mutate("route", "DeepVerify-Mesh")
        tl.metrics["alpha"] = 98
        return "VERIFIED"

    @staticmethod
    async def _task_cache(tl):
        import asyncio, random
        await asyncio.sleep(random.uniform(0.08, 0.16))
        tl.mutate("route", "ShadowCache-Local")
        tl.metrics["alpha"] = 75
        return "CACHED"

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

    def __init__(self, multiverse: Multiverse, port: int = 8080, host: str = "0.0.0.0"):
        self.multiverse = multiverse
        self.port = port
        self.host = host
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

        self._server = HTTPServer((self.host, self.port), handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=daemon)
        self._thread.start()
        display_host = "localhost" if self.host == "0.0.0.0" else self.host
        print(f"[*] Senku QuantumFlow Visualizer running on http://{display_host}:{self.port} (bound to {self.host})")

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            print("[*] Dashboard server stopped.")
