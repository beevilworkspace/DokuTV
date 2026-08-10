"""
Infrastructure Adapter - DokuTV Web Dashboard & HTTP Control Server.
Provides a lightweight local web interface and API endpoints for live status monitoring and interactive video skipping.
"""

import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Optional
from urllib.parse import urlparse, parse_qs

from dokutv.domain.overlay import FollowOverlayConfig
from dokutv.adapters.follow_overlay_template import render_follow_overlay

logger = logging.getLogger("WebDashboardAdapter")

HTML_DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DokuTV – Web Control Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@500;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-gradient: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 50%, #090d16 100%);
      --glass-bg: rgba(255, 255, 255, 0.04);
      --glass-border: rgba(255, 255, 255, 0.08);
      --glass-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
      --accent-purple: #8b5cf6;
      --accent-pink: #ec4899;
      --accent-cyan: #06b6d4;
      --accent-green: #10b981;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', sans-serif;
      background: var(--bg-gradient);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem 1rem;
    }
    header {
      width: 100%;
      max-width: 900px;
      margin-bottom: 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    h1 {
      font-family: 'Outfit', sans-serif;
      font-size: 2.2rem;
      font-weight: 800;
      background: linear-gradient(135deg, #c084fc 0%, #38bdf8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }
    .badge-live {
      background: rgba(16, 185, 129, 0.15);
      color: var(--accent-green);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 0.35rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      background: var(--accent-green);
      border-radius: 50%;
      box-shadow: 0 0 10px var(--accent-green);
      animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
      70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
      100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    .container {
      width: 100%;
      max-width: 900px;
      display: grid;
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }
    .card {
      background: var(--glass-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--glass-border);
      border-radius: 1.5rem;
      padding: 2rem;
      box-shadow: var(--glass-shadow);
    }
    .card-title {
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--text-muted);
      margin-bottom: 1rem;
      font-weight: 600;
    }
    .video-title {
      font-size: 1.4rem;
      font-weight: 700;
      line-height: 1.4;
      margin-bottom: 1rem;
      color: #ffffff;
    }
    .meta-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }
    .meta-item {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.04);
      padding: 0.85rem 1rem;
      border-radius: 0.85rem;
    }
    .meta-label {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-bottom: 0.25rem;
    }
    .meta-value {
      font-size: 1rem;
      font-weight: 600;
      color: var(--text-main);
    }
    .actions-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 1rem;
      text-align: center;
    }
    .btn-skip {
      background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-pink) 100%);
      color: #ffffff;
      border: none;
      padding: 1.1rem 2.5rem;
      border-radius: 1rem;
      font-size: 1.1rem;
      font-weight: 700;
      font-family: 'Outfit', sans-serif;
      cursor: pointer;
      box-shadow: 0 10px 25px -5px rgba(139, 92, 246, 0.5);
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 0.75rem;
      width: 100%;
      max-width: 360px;
      justify-content: center;
    }
    .btn-skip:hover {
      transform: translateY(-2px);
      box-shadow: 0 15px 30px -5px rgba(236, 72, 153, 0.6);
      background: linear-gradient(135deg, #9333ea 0%, #f43f5e 100%);
    }
    .btn-skip:active {
      transform: translateY(1px);
    }
    .btn-skip:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }
    .status-toast {
      font-size: 0.9rem;
      font-weight: 500;
      color: var(--accent-cyan);
      min-height: 1.25rem;
    }
    .history-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }
    .history-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.05);
      padding: 0.85rem 1.25rem;
      border-radius: 0.85rem;
      font-size: 0.9rem;
    }
    .history-item-title {
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 70%;
    }
    .history-item-time {
      color: var(--text-muted);
      font-size: 0.8rem;
    }
  </style>
</head>
<body>
  <header>
    <h1>📺 DokuTV Dashboard</h1>
    <div class="badge-live" id="liveBadge">
      <div class="pulse-dot"></div>
      <span id="liveStatusText">STREAM AKTIV</span>
    </div>
  </header>

  <div class="container">
    <!-- Current Playing Video Card -->
    <div class="card">
      <div class="card-title">Aktuell abgespielte Dokumentation</div>
      <div class="video-title" id="videoTitle">Lade Stream Status...</div>
      
      <div class="meta-grid">
        <div class="meta-item">
          <div class="meta-label">Kanal Name</div>
          <div class="meta-value" id="channelName">DokuTV_EN</div>
        </div>
        <div class="meta-item">
          <div class="meta-label">Dauer</div>
          <div class="meta-value" id="videoDuration">--:--</div>
        </div>
        <div class="meta-item">
          <div class="meta-label">Historien-Einträge</div>
          <div class="meta-value" id="historyCount">0</div>
        </div>
      </div>

      <!-- Action Button -->
      <div class="actions-card">
        <button class="btn-skip" id="btnSkip" onclick="triggerSkip()">
          <span>⏭️ Video überspringen</span>
        </button>
        <div class="status-toast" id="statusToast"></div>
      </div>
    </div>

    <!-- History Card -->
    <div class="card">
      <div class="card-title">Zuletzt abgespielte Dokumentationen</div>
      <ul class="history-list" id="historyList">
        <li class="history-item">Lade Historie...</li>
      </ul>
    </div>
  </div>

  <script>
    async function fetchStatus() {
      try {
        const resp = await fetch('/api/status');
        if (!resp.ok) return;
        const data = await resp.json();

        document.getElementById('channelName').textContent = data.channel_name || 'DokuTV_EN';
        document.getElementById('historyCount').textContent = data.history_count || 0;

        if (data.current_video) {
          document.getElementById('videoTitle').textContent = data.current_video.title || 'Aktuelles Video';
          const durSec = data.current_video.duration_seconds || 3600;
          const mins = Math.floor(durSec / 60);
          const secs = durSec % 60;
          document.getElementById('videoDuration').textContent = `${mins} min ${secs}s`;
        } else {
          document.getElementById('videoTitle').textContent = data.is_running ? 'Bereite nächsten Titel vor...' : 'Stream gestoppt';
          document.getElementById('videoDuration').textContent = '--:--';
        }

        if (data.history && Array.isArray(data.history)) {
          const list = document.getElementById('historyList');
          list.innerHTML = '';
          const recent = data.history.slice(-5).reverse();
          if (recent.length === 0) {
            list.innerHTML = '<li class="history-item">Noch keine Einträge in der Historie.</li>';
          } else {
            recent.forEach(item => {
              const li = document.createElement('li');
              li.className = 'history-item';
              const dateStr = item.played_at ? new Date(item.played_at).toLocaleTimeString() : '';
              li.innerHTML = `<span class="history-item-title">${item.title}</span><span class="history-item-time">${dateStr}</span>`;
              list.appendChild(li);
            });
          }
        }
      } catch (err) {
        console.warn('Status-Abfrage fehlgeschlagen:', err);
      }
    }

    async function triggerSkip() {
      const btn = document.getElementById('btnSkip');
      const toast = document.getElementById('statusToast');
      btn.disabled = true;
      toast.textContent = '⏳ Sende Skip-Signal...';

      try {
        const resp = await fetch('/api/skip', { method: 'POST' });
        const res = await resp.json();
        if (res.success) {
          toast.textContent = '✅ Video erfolgreich übersprungen!';
        } else {
          toast.textContent = 'ℹ️ ' + (res.message || 'Kein aktiver Stream zum Überspringen.');
        }
        await fetchStatus();
      } catch (err) {
        toast.textContent = '❌ Fehler beim Senden des Skip-Signals.';
      } finally {
        setTimeout(() => {
          btn.disabled = false;
          toast.textContent = '';
        }, 2000);
      }
    }

    // Auto-refresh status every 2.5 seconds
    setInterval(fetchStatus, 2500);
    fetchStatus();
  </script>
</body>
</html>
"""


class DashboardRequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for DokuTV Web Dashboard and REST API."""

    engine: Any = None

    def log_message(self, format, *args):
        """Suppress default HTTP server access logs to keep stdout clean."""
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        query_dict = {k: v[0] for k, v in params.items() if v}

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD_TEMPLATE.encode("utf-8"))
        elif path == "/overlay/follow":
            self._handle_follow_overlay(query_dict)
        elif path == "/api/overlay/config":
            self._handle_overlay_config(query_dict)
        elif path == "/api/status":
            self._handle_get_status()
        elif path == "/api/skip":
            self._handle_skip()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_follow_overlay(self, query_dict: dict):
        config = FollowOverlayConfig.from_dict(query_dict)
        html = render_follow_overlay(config)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _handle_overlay_config(self, query_dict: dict):
        config = FollowOverlayConfig.from_dict(query_dict)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(config.to_dict(), ensure_ascii=False).encode("utf-8"))


    def do_POST(self):
        if self.path == "/api/skip":
            self._handle_skip()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_get_status(self):
        status_data = {}
        if self.engine and hasattr(self.engine, "get_status"):
            status_data = self.engine.get_status()
        if self.engine and hasattr(self.engine, "get_history"):
            history_entries = self.engine.get_history()
            status_data["history"] = [entry.to_dict() for entry in history_entries]

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(status_data, ensure_ascii=False).encode("utf-8"))

    def _handle_skip(self):
        success = False
        message = "No engine connected"
        if self.engine and hasattr(self.engine, "skip_current_video"):
            success = self.engine.skip_current_video()
            message = "Skip request executed" if success else "No active video process to skip"

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        resp = {"success": success, "message": message}
        self.wfile.write(json.dumps(resp, ensure_ascii=False).encode("utf-8"))


class WebDashboardAdapter:
    """Adapter running local web control server in a daemon background thread."""

    def __init__(self, engine: Any = None, port: int = 8080):
        self.engine = engine
        self.port = port
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start local HTTP server in background thread."""
        if self._thread and self._thread.is_alive():
            return

        class BoundHandler(DashboardRequestHandler):
            pass

        BoundHandler.engine = self.engine

        try:
            self._server = HTTPServer(("0.0.0.0", self.port), BoundHandler)
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()
            logger.info(f"🚀 Web Control Dashboard running at http://localhost:{self.port}")
        except Exception as e:
            logger.error(f"Failed to start Web Control Dashboard on port {self.port}: {e}")

    def stop(self) -> None:
        """Stop local HTTP server."""
        if self._server:
            try:
                self._server.shutdown()
                self._server.server_close()
                logger.info("Web Control Dashboard server stopped.")
            except Exception as e:
                logger.warning(f"Error shutting down web dashboard: {e}")
            self._server = None
