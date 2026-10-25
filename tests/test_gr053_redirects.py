#!/usr/bin/env python3
"""Real urllib, two synthetic loopback HTTP servers; no external services."""
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'integration'))
from gateway.seafile import Seafile, SeafileError


class RedirectTests(unittest.TestCase):
    def test_redirect_policy(self):
        received = []

        class Target(BaseHTTPRequestHandler):
            def do_GET(self):
                received.append((self.path, self.headers.get('Authorization')))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'public')

            def log_message(self, *args):
                pass

        target = HTTPServer(('127.0.0.1', 0), Target)
        target_url = f'http://127.0.0.1:{target.server_port}'

        class Source(Target):
            def do_GET(self):
                self.send_response(int(self.headers.get('X-Test-Status', '302')))
                self.send_header('Location', target_url + self.path)
                self.end_headers()

            do_POST = do_GET

        source = HTTPServer(('127.0.0.1', 0), Source)
        servers = (source, target)
        threads = [threading.Thread(target=s.serve_forever) for s in servers]
        for thread in threads:
            thread.start()
        try:
            base = f'http://127.0.0.1:{source.server_port}'
            client = Seafile(base, 'synthetic-account')
            cases = [dict(), dict(auth=False, headers={'authorization': 'Bearer synthetic'})]
            cases += [dict(auth=False, query=f'?{key}=synthetic-query') for key in
                      ('access_token', 'token', 'jwt', 'signature', 'password', 'ToKeN',
                       '%74oken', 'pa%C5%BFsword')]
            cases += [dict(auth=False, query='?token='), dict(auth=False, allow_redirects=False)]
            for code in (301, 302, 303, 307, 308):
                for case in cases:
                    with self.subTest(code=code, case=case):
                        options = dict(case)
                        query = options.pop('query', '')
                        headers = dict(options.pop('headers', {}), **{'X-Test-Status': str(code)})
                        with self.assertRaises(SeafileError) as caught:
                            client._request(base + '/opaque-capability' + query,
                                            headers=headers, **options)
                        self.assertEqual(caught.exception.status, code)
                        self.assertNotIn('synthetic', str(caught.exception))
                        self.assertEqual(received, [])
            self.assertEqual(client._request(base + '/public?p=hello', auth=False), (200, b'public'))
            self.assertEqual(received, [('/public?p=hello', None)])
            # Each signed-link caller must opt out even when its token is path-only.
            client.download_link = lambda *args: base + '/files/synthetic-path'
            client.update_link = lambda *args: base + '/update/synthetic-path'
            client._json = lambda *args: base + '/upload/synthetic-path'
            for call in (lambda: client.download('repo', '/file'),
                         lambda: client.update_file('repo', '/file', b'body'),
                         lambda: client.upload_file('repo', '/', 'file', b'body')):
                with self.assertRaises(SeafileError):
                    call()
                self.assertEqual(len(received), 1)
        finally:
            for server in servers:
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join(timeout=3)
                self.assertFalse(thread.is_alive())


if __name__ == '__main__':
    unittest.main()
