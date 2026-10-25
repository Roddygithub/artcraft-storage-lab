#!/usr/bin/env python3
"""Synthetic upstream commit/response loss; no real Seafile or browser."""
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from test_gr049_save_retry import RetrySeafile
from test_gateway_unit import SeafileError, make_gateway, valid_docx


class LostResponseSeafile(RetrySeafile):
    def __init__(self):
        super().__init__()
        self.after_commit = lambda: None
        self.read_calls = []
        self.content_error = None
        self.after_content = lambda: None
        self.loss_status = None

    def thirdparty_file_save(self, *args):
        super().thirdparty_file_save(*args)
        self.after_commit()
        raise SeafileError('synthetic lost response', self.loss_status)

    def thirdparty_file_content(self, token, expected_file_id, max_bytes=None):
        self.read_calls.append((token, expected_file_id, max_bytes))
        if self.content_error:
            raise self.content_error
        content = super().thirdparty_file_content(token, expected_file_id, max_bytes)
        self.after_content()
        return content


class ContentionObservedLock:
    """RLock wrapper that signals only after a contender fails try-acquire."""
    def __init__(self, lock):
        self.lock = lock
        self.contended = Event()

    def __enter__(self):
        if not self.lock.acquire(blocking=False):
            self.contended.set()
            self.lock.acquire()
        return self

    def __exit__(self, *_):
        self.lock.release()


class UpstreamSaveLossTests(unittest.TestCase):
    def setUp(self):
        self.upstream = LostResponseSeafile()
        self.gateway = make_gateway(self.upstream)
        self.session, error = self.gateway.open_session('synthetic-token')
        self.assertIsNone(error)
        self.session.unsaved = True
        self.data = valid_docx()

    def save(self):
        return self.gateway.save(self.session, self.data)

    def assert_failed_baseline(self, status):
        result, actual = self.save()
        self.assertEqual(actual, status)
        self.assertFalse(result['ok'])
        self.assertEqual((self.session.file_id, self.session.head_commit_id), ('aaaa', 'head-a'))
        self.assertTrue(self.session.unsaved)
        self.assertIsNone(self.session.last_save)
        self.assertEqual(self.upstream.save_calls, 1)

    def test_committed_bytes_confirm_and_retry_without_write(self):
        first = self.save()
        self.assertEqual(first[1], 200)
        self.assertEqual((self.session.file_id, self.session.head_commit_id), ('bbbb', 'head-b'))
        self.assertFalse(self.session.unsaved)
        self.assertIsNotNone(self.session.last_save)
        self.assertEqual(self.save(), first)
        self.assertEqual(self.upstream.save_calls, 1)
        self.assertEqual(len(self.upstream.written), 1)
        self.assertEqual(self.upstream.read_calls,
                         [('synthetic-token', 'bbbb', self.gateway.max_bytes)])

    def test_concurrent_retry_after_reconciliation_reuses_receipt(self):
        commit_seen = Event()
        release_response = Event()
        observed_lock = ContentionObservedLock(self.session.lock)
        self.session.lock = observed_lock

        def lose_response_after_commit():
            commit_seen.set()
            if not release_response.wait(timeout=2):
                raise AssertionError('test did not release the simulated lost response')

        self.upstream.after_commit = lose_response_after_commit

        def first_save():
            return self.save()

        def concurrent_retry():
            return self.save()

        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(first_save)
            self.assertTrue(commit_seen.wait(timeout=2))
            second = pool.submit(concurrent_retry)
            self.assertTrue(observed_lock.contended.wait(timeout=2))
            release_response.set()
            first_result = first.result(timeout=2)
            second_result = second.result(timeout=2)

        self.assertEqual(first_result[1], 200)
        self.assertEqual(second_result, first_result)
        self.assertFalse(self.session.unsaved)
        self.assertEqual(self.upstream.save_calls, 1)
        self.assertEqual(len(self.upstream.written), 1)

    def test_different_bytes_do_not_confirm(self):
        self.upstream.after_commit = lambda: setattr(self.upstream, 'content', b'different')
        self.assert_failed_baseline(502)
        self.assertEqual(self.save()[1], 409)  # Old CAS baseline is retained.
        self.assertEqual(len(self.upstream.written), 1)

    def test_revoked_permission(self):
        self.upstream.after_commit = lambda: setattr(self.upstream, 'permission', 'r')
        self.assert_failed_baseline(403)
        self.assertEqual(self.upstream.read_calls, [])

    def test_changed_user_repo_or_path(self):
        for field, value in [('username', 'mallory'), ('repo_id', 'other'), ('file_path', '/other.docx')]:
            with self.subTest(field=field):
                self.setUp()
                original = self.upstream.thirdparty_file_info
                def changed(token, field=field, value=value):
                    return dict(original(token), **{field: value})
                self.upstream.after_commit = lambda: setattr(self.upstream, 'thirdparty_file_info', changed)
                self.assert_failed_baseline(403)
                self.assertEqual(self.upstream.read_calls, [])

    def test_read_failures(self):
        for status, expected in [(401, 403), (404, 404), (None, 502), (503, 502)]:
            for stage in ('info', 'content'):
                with self.subTest(status=status, stage=stage):
                    self.setUp()
                    error = SeafileError('synthetic secret-bearing error', status)
                    if stage == 'info':
                        self.upstream.after_commit = lambda: setattr(self.upstream, 'info_error', error)
                    else:
                        self.upstream.content_error = error
                    self.assert_failed_baseline(expected)

    def test_missing_read_capability(self):
        # Missing method raises AttributeError just as an older client would.
        self.upstream.after_commit = lambda: setattr(self.upstream, 'thirdparty_file_content', self.missing)
        self.assert_failed_baseline(503)

    @staticmethod
    def missing(*args, **kwargs):
        raise AttributeError('no content API')

    def test_missing_current_identity(self):
        for field in ('obj_id', 'head_id'):
            with self.subTest(field=field):
                self.setUp()
                self.upstream.after_commit = lambda: setattr(self.upstream, field, '')
                self.assert_failed_baseline(502)

    def test_change_during_content_read(self):
        for field, value, status in [('head_id', 'head-c', 409), ('obj_id', 'cccc', 409),
                                     ('permission', 'r', 403), ('user', 'mallory', 403)]:
            with self.subTest(field=field):
                self.setUp()
                self.upstream.after_content = lambda: setattr(self.upstream, field, value)
                self.assert_failed_baseline(status)

    def test_known_errors_are_not_reconciled(self):
        for status, expected in [(409, 409), (403, 403), (400, 502), (502, 502)]:
            with self.subTest(status=status):
                self.setUp()
                self.upstream.loss_status = status
                self.assert_failed_baseline(expected)
                self.assertEqual(self.upstream.read_calls, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
