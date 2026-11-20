#!/usr/bin/env python3
import http.server
import os
import socketserver
import sys
import webbrowser

PORT = 8000

def main():
    web_dir = os.path.join(os.path.dirname(__file__), "web")
    if not os.path.exists(web_dir):
        sys.stderr.write(f"Web directory missing: {web_dir}\n")
        sys.exit(1)

    os.chdir(web_dir)
    handler = http.server.SimpleHTTPRequestHandler

    global PORT
    for p in range(PORT, PORT + 20):
        try:
            httpd = socketserver.TCPServer(("", p), handler)
            PORT = p
            break
        except OSError:
            continue
    else:
        sys.stderr.write("No open port found\n")
        sys.exit(1)

    url = f"http://localhost:{PORT}/index.html"
    print(f"Game server: {url}")
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    main()
