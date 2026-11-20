#!/usr/bin/env python3
"""
Game server and Leaderboard manager for Dao Den Long (Island of Lanterns).
Supports:
- Local WebGL 3D game server with API endpoints for persistent leaderboard.
- CLI leaderboard export: python run_game.py --export-leaderboard out.json
"""

import argparse
import http.server
import json
import os
import re
import socketserver
import sys
import webbrowser

PORT = 8000
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.json")


def load_leaderboard() -> list:
    """Load and sort top 10 leaderboard entries from disk."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            entries = data.get("entries", []) if isinstance(data, dict) else data
            # Sort: score descending, then achieved_at ascending
            entries.sort(key=lambda e: (-e.get("score", 0), e.get("achieved_at", "")))
            return entries[:10]
    except Exception:
        return []


def save_leaderboard(entries: list):
    """Save top 10 sorted leaderboard entries to disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    # Sort: score descending, achieved_at ascending
    entries.sort(key=lambda e: (-e.get("score", 0), e.get("achieved_at", "")))
    top10 = entries[:10]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump({"entries": top10}, f, indent=2, ensure_ascii=False)


def add_leaderboard_entry(entry: dict) -> list:
    """Validate and insert a new leaderboard entry, keeping top 10."""
    name = str(entry.get("name", "")).strip()
    if not (3 <= len(name) <= 12):
        raise ValueError("Name must be between 3 and 12 characters")

    score = int(entry.get("score", 0))
    nights_won = int(entry.get("nights_won", 0))
    achieved_at = str(entry.get("achieved_at", ""))
    seed = int(entry.get("seed", 42))

    new_item = {
        "name": name,
        "score": score,
        "nights_won": nights_won,
        "achieved_at": achieved_at,
        "seed": seed,
    }

    entries = load_leaderboard()
    entries.append(new_item)
    save_leaderboard(entries)
    return load_leaderboard()


def export_leaderboard(out_path: str):
    """Export leaderboard JSON strictly formatted per Ticket-04 specification."""
    entries = load_leaderboard()
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"entries": entries}, f, indent=2, ensure_ascii=False)

    print(f"Leaderboard exported successfully to {out_path} ({len(entries)} entries)")
    sys.exit(0)


class GameRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler supporting static web files and /api/leaderboard."""

    def __init__(self, *args, **kwargs):
        web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "web"))
        super().__init__(*args, directory=web_dir, **kwargs)

    def do_GET(self):
        if self.path == "/api/leaderboard":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            entries = load_leaderboard()
            self.wfile.write(json.dumps({"entries": entries}, ensure_ascii=False).encode("utf-8"))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/leaderboard":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)
            try:
                data = json.loads(post_body.decode("utf-8"))
                updated = add_leaderboard_entry(data)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"entries": updated}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_error(404, "Endpoint not found")


def main():
    parser = argparse.ArgumentParser(description="Dao Den Long Game Server & Tools")
    parser.add_argument("--export-leaderboard", type=str, default=None, help="Export leaderboard to JSON file")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open web browser")

    args = parser.parse_args()

    if args.export_leaderboard:
        export_leaderboard(args.export_leaderboard)

    # Start Game HTTP Server
    global PORT
    for p in range(PORT, PORT + 20):
        try:
            httpd = socketserver.TCPServer(("", p), GameRequestHandler)
            PORT = p
            break
        except OSError:
            continue
    else:
        sys.stderr.write("Error: No available port found between 8000 and 8020\n")
        sys.exit(1)

    url = f"http://localhost:{PORT}/index.html"
    print(f"Island of Lanterns Game Server running at: {url}")

    if not args.no_browser:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        sys.exit(0)


if __name__ == "__main__":
    main()
