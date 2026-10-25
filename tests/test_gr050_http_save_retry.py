#!/usr/bin/env python3
"""Real gateway route with deterministic post-commit HTTP response loss."""
import http.client
import json
import socket
import threading
import unittest
from http.server import ThreadingHTTPServer

from test_gateway_unit import Handler, make_gateway, valid_docx
from test_gr049_save_retry import RetrySeafile


class DropFirstSaveResponse(Handler):
    def log_message(self, *_args):
        pass

    def _json(self, status, payload):
        if self.path == self.server.save_path and self.server.dropped_result is None:
            # Handler.do_POST has already called the real Gateway.save. Send no
            # status line, headers or body: the HTTP client must observe EOF.
            self.server.dropped_result = (status, dict(payload))
            self.close_connection = True
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()
            return
        return super()._json(status, payload)


class HttpSaveRetryTests(unittest.TestCase):
    def test_response_lost_after_commit_retry_writes_once(self):
        upstream = RetrySeafile()
        gateway = make_gateway(upstream)
        session, error = gateway.open_session('synthetic-token')
        self.assertIsNone(error)
        data = valid_docx()
        with ThreadingHTTPServer(('127.0.0.1', 0), DropFirstSaveResponse) as server:
            server.gateway = gateway
            server.save_path = f'/session/{session.sid}/save'
            server.dropped_result = None
            thread = threading.Thread(target=server.serve_forever,
                                      kwargs={'poll_interval': 0.05}, daemon=True)
            thread.start()
            host, port = server.server_address
            headers = {'Origin': f'http://{host}:{port}',
                       'Content-Type': 'application/octet-stream',
                       'X-ArtCraft-Filename': session.name}
            try:
                first = http.client.HTTPConnection(host, port, timeout=3)
                try:
                    first.request('POST', server.save_path, data, headers)
                    with self.assertRaises(http.client.RemoteDisconnected):
                        first.getresponse()
                finally:
                    first.close()
                self.assertEqual(server.dropped_result[0], 200)
                self.assertTrue(server.dropped_result[1]['ok'])
                self.assertEqual(upstream.save_calls, 1)
                self.assertEqual(len(upstream.written), 1)
                self.assertEqual((upstream.obj_id, upstream.head_id), ('bbbb', 'head-b'))
                self.assertEqual(upstream.content, data)

                retry = http.client.HTTPConnection(host, port, timeout=3)
                try:
                    retry.request('POST', server.save_path, data, headers)
                    response = retry.getresponse()
                    self.assertEqual(response.status, 200)
                    self.assertEqual(json.loads(response.read()), server.dropped_result[1])
                finally:
                    retry.close()
                self.assertEqual(upstream.save_calls, 1)
                self.assertEqual(len(upstream.written), 1)
                self.assertEqual((upstream.obj_id, upstream.head_id), ('bbbb', 'head-b'))
                self.assertEqual(upstream.content, data)
            finally:
                server.shutdown()
                thread.join(timeout=3)
                self.assertFalse(thread.is_alive())


if __name__ == '__main__':
    unittest.main(verbosity=2)
