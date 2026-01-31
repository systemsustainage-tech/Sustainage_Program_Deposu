import logging
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class UTF8SimpleHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Ensure .txt and .md are served with UTF-8 charset to prevent garbled characters
    extensions_map = SimpleHTTPRequestHandler.extensions_map.copy()
    extensions_map.update({
        '.txt': 'text/plain; charset=utf-8',
        '.md': 'text/markdown; charset=utf-8',
        '.csv': 'text/csv; charset=utf-8',
        # Keep other mappings as-is
    })

    # Optionally normalize default to UTF-8 for unknown text types
    def guess_type(self, path):
        ctype = super().guess_type(path)
        if ctype.startswith('text/') and 'charset=' not in ctype:
            # Add charset for text types missing explicit encoding
            ctype = f"{ctype}; charset=utf-8"
        return ctype


def run_server(port: int):
    httpd = ThreadingHTTPServer(('', port), UTF8SimpleHandler)
    logging.info(f"Serving UTF-8 HTTP on http://localhost:{port}/ (cwd: {os.getcwd()})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt as e:
        logging.error(f'Silent error in serve_utf8.py: {str(e)}')
    finally:
        httpd.server_close()


if __name__ == '__main__':
    # Usage: python tools/serve_utf8.py [port]
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            logging.info("Invalid port provided; falling back to 8000")
    run_server(port)
