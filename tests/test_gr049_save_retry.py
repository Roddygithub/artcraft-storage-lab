#!/usr/bin/env python3
"""Synthetic gateway receipt regression; no Seafile or network-loss runtime."""
import threading
import unittest

from test_gateway_unit import FakeSeafile, Seafile, make_gateway, valid_docx, zip_payload


class RetrySeafile(FakeSeafile):
    # Exercise the real token-to-user/document binding checks on replay.
    user_file_detail = Seafile.user_file_detail

    def __init__(self):
        super().__init__()
        self.info_error = None
        self.save_error = None
        self.save_expectations = []

    def thirdparty_file_info(self, token):
        if self.info_error:
            raise self.info_error
        return super().thirdparty_file_info(token)

    def thirdparty_file_save(self, *args):
        self.save_expectations.append(args[1:3])
        if self.save_error:
            self.save_calls += 1
            raise self.save_error
        return super().thirdparty_file_save(*args)


class SaveRetryTests(unittest.TestCase):
    def setUp(self):
        self.upstream = RetrySeafile()
        self.gateway = make_gateway(self.upstream)
        self.session, error = self.gateway.open_session('synthetic-token')
        self.assertIsNone(error)
        self.data = valid_docx()

    def save(self, data=None, **kwargs):
        return self.gateway.save(self.session, self.data if data is None else data, **kwargs)

    def test_discarded_response_retry(self):
        first = self.save()  # Commit succeeds; simulate caller losing this result.
        self.assertEqual(self.save(), first)
        self.assertEqual(self.upstream.save_calls, 1)
        self.assertEqual(len(self.upstream.written), 1)
        digest, length, result = self.session.last_save
        self.assertEqual((len(digest), length), (32, len(self.data)))
        self.assertEqual(result, first[0])
        first[0]['version'] = 'caller mutation'
        self.assertEqual(self.save()[0]['version'], 'head-b')

    def test_changed_payload_uses_cas(self):
        self.save()
        changed = zip_payload([('[Content_Types].xml',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'),
            ('word/document.xml', '<document>changed</document>')])
        self.assertEqual(self.save(changed)[1], 200)
        self.assertEqual(self.upstream.save_calls, 2)
        self.assertEqual(self.upstream.save_expectations,
                         [("aaaa", "head-a"), ("bbbb", "head-b")])
        self.upstream.head_id = 'external-head'
        self.assertEqual(self.save(self.data)[1], 409)
        self.assertEqual(len(self.upstream.written), 2)

    def test_replay_revalidates_payload_and_local_authorization(self):
        self.save()
        self.assertEqual(self.save(name='export.docx')[1], 400)
        self.assertEqual(self.save(b'invalid')[1], 400)
        self.gateway.max_bytes = len(self.data) - 1
        self.assertEqual(self.save()[1], 413)
        self.gateway.max_bytes = len(self.data)
        self.session.user_authorized = False
        self.assertEqual(self.save()[1], 403)
        self.assertEqual(self.upstream.save_calls, 1)

    def test_replay_rechecks_permission_identity_and_freshness(self):
        from gateway.seafile import SeafileError
        self.save()
        for attribute, value, status in [('permission', 'r', 403),
                                          ('user', 'mallory', 403),
                                          ('obj_id', 'external-file', 409),
                                          ('head_id', 'external-head', 409)]:
            original = getattr(self.upstream, attribute)
            setattr(self.upstream, attribute, value)
            self.assertEqual(self.save()[1], status, attribute)
            setattr(self.upstream, attribute, original)
        for upstream_status, expected in [(401, 403), (404, 404), (503, 502)]:
            self.upstream.info_error = SeafileError('synthetic failure', upstream_status)
            self.assertEqual(self.save()[1], expected)
        self.assertEqual(self.upstream.save_calls, 1)
        self.assertEqual(len(self.upstream.written), 1)

    def test_failed_save_does_not_create_receipt(self):
        from gateway.seafile import SeafileError
        self.upstream.save_error = SeafileError('unconfirmed', 502)
        self.assertEqual(self.save()[1], 502)
        self.assertIsNone(self.session.last_save)
        self.upstream.save_error = None
        self.assertEqual(self.save()[1], 200)
        self.assertEqual(self.upstream.save_calls, 2)

    def test_concurrent_identical_saves_share_receipt(self):
        start = threading.Barrier(3)
        results = []
        def run():
            start.wait()
            results.append(self.save())
        threads = [threading.Thread(target=run) for _ in range(2)]
        for thread in threads:
            thread.start()
        start.wait()
        for thread in threads:
            thread.join(timeout=3)
            self.assertFalse(thread.is_alive())
        self.assertEqual([status for _, status in results], [200, 200])
        self.assertEqual(self.upstream.save_calls, 1)
        self.assertEqual(len(self.upstream.written), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
