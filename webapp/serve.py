#!/usr/bin/env python3
"""Serve the KuttyPy I/O webapp on localhost (required for Web Serial API)."""

import http.server
import os
import socketserver

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def end_headers(self):
        path = self.path.split('?', 1)[0]
        ext = os.path.splitext(path)[1].lower()
        if ext in ('.js', '.css', '.html', '.mjs', '.json'):
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Pragma', 'no-cache')
        super().end_headers()


def main():
    os.chdir(DIR)
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        print(f'KuttyPy I/O Monitor: http://localhost:{PORT}/')
        print('Use Chrome or Edge. Connect your KuttyPy board (CH340 / MCP2200).')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nStopped.')


if __name__ == '__main__':
    main()
