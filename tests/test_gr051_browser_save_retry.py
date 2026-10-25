#!/usr/bin/env python3
"""Loopback browser retry; synthetic editor (not WASM) and FakeSeafile.

Run: uv run --with playwright --python 3.14 -- python -u tests/test_gr051_browser_save_retry.py
Only gateway-to-browser response loss AFTER gateway receipt is injected.
"""
import json
import os
import socket
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from test_gateway_unit import Handler, make_gateway, valid_docx, zip_payload
from test_gr049_save_retry import RetrySeafile


class ParentHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        body = ("<!doctype html><iframe id='host' name='host'></iframe>"
                f"<form method='POST' action='{self.server.gateway_url}' target='host'>"
                "<input name='access_token' value='synthetic-token'></form>").encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class DropFirstSaveResponse(Handler):
    protocol_version = 'HTTP/1.0'

    def log_message(self, *_args):
        pass

    def _send(self, status, body, content_type='text/plain; charset=utf-8', headers=None):
        self.server.routes.append((self.command, self.path, status))
        return super()._send(status, body, content_type, headers)

    def _json(self, status, payload):
        if self.path.endswith('/save'):
            self.server.save_results.append((status, dict(payload)))
            if len(self.server.save_results) == 1:
                # Inherited Handler has returned from real Gateway.save. No
                # status line, headers or body reach Chromium for this POST.
                assert status == 200 and payload['ok'] is True
                assert self.server.gateway.seafile.save_calls == 1
                self.server.routes.append((self.command, self.path, 'DROP'))
                self.close_connection = True
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()
                return
        return super()._json(status, payload)

    def do_GET(self):
        if urllib.parse.urlsplit(self.path).path == '/artcraft/test-editor':
            body = """<!doctype html><p>Synthetic editor, not actual WASM</p>
<button id="edit" disabled>Edit synthetic document</button>
<button id="save" disabled>Save synthetic edit</button><script>
window.proof = {opened:false, dirty:false, tickets:[], results:[], cleanSignals:0};
const bytes = new Uint8Array(__BYTES__);
addEventListener('message', event => {
  if (event.origin !== location.origin || event.source !== parent) return;
  const data = event.data;
  if (data?.type === 'wordcraft:open') {
    proof.opened = data.name === 'a.docx' && data.bytes.length > 0;
    document.querySelector('#edit').disabled = !proof.opened;
    document.querySelector('#save').disabled = !proof.opened;
  }
  if (data?.type === 'wordcraft:saveResult') {
    proof.results.push(data);
    if (data.ok === true) {
      proof.dirty = false;
      proof.cleanSignals++;
      parent.postMessage({type:'wordcraft:dirty', dirty:false}, location.origin);
    }
  }
});
document.querySelector('#edit').onclick = () => {
  proof.dirty = true;
  parent.postMessage({type:'wordcraft:dirty', dirty:true}, location.origin);
};
document.querySelector('#save').onclick = () => {
  const ticket = 'ticket-' + (proof.tickets.length + 1);
  proof.tickets.push(ticket);
  parent.postMessage({type:'wordcraft:save', ticket, name:'a.docx', bytes}, location.origin);
};
parent.postMessage({type:'wordcraft:ready', version:1}, location.origin);
</script>""".replace('__BYTES__', json.dumps(list(self.server.edited_bytes)))
            return self._send(200, body, 'text/html; charset=utf-8')
        return super().do_GET()


def main():
    from playwright.sync_api import sync_playwright

    upstream = RetrySeafile()
    upstream.content = valid_docx()
    edited = zip_payload([('[Content_Types].xml',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'),
        ('word/document.xml', '<document>synthetic edit</document>')])
    gateway = make_gateway(upstream, {'docx': {'app': 'wordcraft', 'url': '/artcraft/test-editor'}})
    parent = ThreadingHTTPServer(('127.0.0.1', 0), ParentHandler)
    host = ThreadingHTTPServer(('127.0.0.1', 0), DropFirstSaveResponse)
    # Join request threads on server_close as well as the serve_forever threads.
    parent.daemon_threads = host.daemon_threads = False
    host.gateway = gateway
    host.edited_bytes = edited
    host.routes = []
    host.save_results = []
    origin = f'http://127.0.0.1:{host.server_port}'
    parent.gateway_url = origin + '/open/'
    old_origin = os.environ.get('ARTCRAFT_SEAFILE_ORIGIN')
    os.environ['ARTCRAFT_SEAFILE_ORIGIN'] = f'http://127.0.0.1:{parent.server_port}'
    servers = (parent, host)
    threads = [threading.Thread(target=server.serve_forever,
                                kwargs={'poll_interval': 0.05}) for server in servers]
    for thread in threads:
        thread.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.set_default_timeout(10_000)
                page.on('dialog', lambda dialog: dialog.dismiss())
                responses, failures = [], []
                page.on('response', lambda response: responses.append(
                    (response.request.method, response.url.removeprefix(origin), response.status))
                    if response.url.startswith(origin) else None)
                page.on('requestfailed', lambda request: failures.append(
                    (request.method, request.url.removeprefix(origin), request.failure)))
                page.goto(os.environ['ARTCRAFT_SEAFILE_ORIGIN'])
                page.locator('form').evaluate('form => form.submit()')
                host_frame = page.frame_locator('#host')
                host_frame.locator('#state').filter(has_text='a.docx opened').wait_for()
                editor = host_frame.frame_locator('#frame')
                editor_frame = next(frame for frame in page.frames
                                    if frame.url.endswith('/artcraft/test-editor'))
                session, = gateway.sessions._sessions.values()
                save_path = f'/session/{session.sid}/save'
                dirty_path = f'/session/{session.sid}/dirty'
                document_path = f'/session/{session.sid}/document'
                with page.expect_response(lambda response: response.url == origin + dirty_path) as dirty:
                    editor.locator('#edit').click()
                assert dirty.value.status == 200 and dirty.value.json() == {'ok': True, 'unsaved': True}
                editor.locator('#save').click()
                editor_frame.wait_for_function('proof.results.length === 1')
                first = editor.locator('body').evaluate('() => proof')
                assert first == {'opened': True, 'dirty': True, 'tickets': ['ticket-1'],
                                 'results': [{'type': 'wordcraft:saveResult', 'ticket': 'ticket-1',
                                              'ok': False, 'error': 'the file could not be stored'}],
                                 'cleanSignals': 0}, first
                host_frame.locator('#state').filter(has_text='Save failed:').wait_for()
                host_body = host_frame.locator('body')
                state = host_body.evaluate('() => [__lastDirty, __editorConfirmedSave, __saveConfirmationPending, __saveInFlight, __lastSave]')
                assert state == [True, False, False, False, {'ok': False}], state
                assert upstream.save_calls == len(upstream.written) == 1
                # The commit is durable at the gateway even though the browser
                # cannot confirm it after losing the response.
                assert session.unsaved is False
                assert upstream.content == edited
                assert session.last_save is not None
                assert host.save_results[0][0] == 200 and host.save_results[0][1]['ok'] is True
                assert failures == [('POST', save_path, 'net::ERR_EMPTY_RESPONSE')], failures
                assert not [route for route in responses if route[1] == save_path], responses
                with page.expect_response(lambda response: response.url == origin + dirty_path
                                          and response.request.post_data == 'false') as clean:
                    editor.locator('#save').click()
                assert clean.value.status == 200 and clean.value.json() == {'ok': True, 'unsaved': False}
                host_frame.locator('#state').filter(has_text='Saved — new version head-b').wait_for()
                final = editor.locator('body').evaluate('() => proof')
                assert final['tickets'] == ['ticket-1', 'ticket-2'], final
                assert final['results'] == [first['results'][0],
                    {'type': 'wordcraft:saveResult', 'ticket': 'ticket-2', 'ok': True, 'error': ''}], final
                assert final['dirty'] is False and final['cleanSignals'] == 1
                state = host_body.evaluate('() => [__lastDirty, __editorConfirmedSave, __saveConfirmationPending, __saveInFlight, __lastSave]')
                assert state == [False, True, False, False, host.save_results[0][1]], state
                assert host.save_results == [host.save_results[0], host.save_results[0]]
                assert upstream.save_calls == len(upstream.written) == 1
                assert upstream.content == edited and (upstream.obj_id, upstream.head_id) == ('bbbb', 'head-b')
                assert upstream.save_expectations == [('aaaa', 'head-a')]
                assert session.unsaved is False
                # Compare every route/status without depending on browser
                # response-event ordering across separate connections.
                expected = [('POST', '/open/', 200), ('GET', '/artcraft/test-editor', 200),
                            ('GET', document_path, 200), ('POST', dirty_path, 200),
                            ('POST', dirty_path, 200),
                            ('POST', save_path, 'DROP'), ('POST', save_path, 200)]
                assert sorted(host.routes, key=str) == sorted(expected, key=str), host.routes
                assert sorted(responses, key=str) == sorted(
                    [route for route in expected if route[2] != 'DROP'], key=str), responses
                print('PASS: real Handler /open/ + hostpage.render + /document HTTP 200; synthetic editor opened')
                print('PASS: first save committed HTTP 200 internally, socket dropped; Chromium net::ERR_EMPTY_RESPONSE')
                print('PASS: ticket-1 negative result; editor and host dirty, unconfirmed; no clean signal')
                print('PASS: user retry ticket-2, identical bytes, HTTP 200 receipt; upstream writes=1, head=head-b')
                print('PASS: editor dirty=false; host clean/confirmed; two dirty routes HTTP 200, gateway unsaved=false')
                print('PASS: exact browser/server route statuses and both ticket results asserted')
                print('OBSERVED server routes:', sorted(
                    [(method, path.replace(session.sid, '<sid>'), status)
                     for method, path, status in host.routes], key=str))
                print('OBSERVED browser save: DROP/net::ERR_EMPTY_RESPONSE, then HTTP 200; tickets: ticket-1=false, ticket-2=true')
            finally:
                browser.close()
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=3)
        if old_origin is None:
            os.environ.pop('ARTCRAFT_SEAFILE_ORIGIN', None)
        else:
            os.environ['ARTCRAFT_SEAFILE_ORIGIN'] = old_origin
        assert all(not thread.is_alive() for thread in threads), 'server thread did not stop'
    print('PASS: browser closed, servers closed, serve threads joined, origin environment restored')
    print('LIMIT: synthetic editor (not WASM), synthetic Seafile (not real); upstream response loss before gateway receipt NOT VERIFIED')


if __name__ == '__main__':
    main()
