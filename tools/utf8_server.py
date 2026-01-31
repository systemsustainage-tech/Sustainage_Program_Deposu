import logging
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class UTF8Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    extensions_map = SimpleHTTPRequestHandler.extensions_map.copy()
    extensions_map.update({
        # Kod ve metin dosyaları
        '.py': 'text/plain; charset=UTF-8',
        '.txt': 'text/plain; charset=UTF-8',
        '.md': 'text/plain; charset=UTF-8',
        '.csv': 'text/csv; charset=UTF-8',
        '.log': 'text/plain; charset=UTF-8',
        '.ini': 'text/plain; charset=UTF-8',
        '.cfg': 'text/plain; charset=UTF-8',
        '.conf': 'text/plain; charset=UTF-8',
        '.sql': 'text/plain; charset=UTF-8',
        '.yaml': 'text/plain; charset=UTF-8',
        '.yml': 'text/plain; charset=UTF-8',

        # Web içerikleri
        '.html': 'text/html; charset=UTF-8',
        '.htm': 'text/html; charset=UTF-8',
        '.css': 'text/css; charset=UTF-8',
        '.js': 'application/javascript; charset=UTF-8',
        '.mjs': 'application/javascript; charset=UTF-8',
        '.json': 'application/json; charset=UTF-8',
        '.xml': 'application/xml; charset=UTF-8',

        # Varsayılan
        '': 'application/octet-stream',
    })

def run():
    port = int(os.environ.get('PORT', '8001'))
    root = os.environ.get('ROOT', os.getcwd())
    os.chdir(root)
    server = ThreadingHTTPServer(('', port), UTF8Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt as e:
        logging.error(f'Silent error in utf8_server.py: {str(e)}')

if __name__ == '__main__':
    run()