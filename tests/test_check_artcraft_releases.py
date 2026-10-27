import io
import importlib.util
import json
from email.utils import format_datetime
from pathlib import Path
import unittest
import urllib.error
from datetime import datetime, timezone
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/check-artcraft-releases.py"
SPEC = importlib.util.spec_from_file_location("check_artcraft_releases", MODULE_PATH)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


class ReleaseCheckerTests(unittest.TestCase):
    def test_reports_tag_and_compare_distance_without_mutation(self):
        responses = [
            {"tag_name": "v0.11.0", "html_url": "https://github.com/storytold/wordcraft/releases/tag/v0.11.0"},
            {"object": {"type": "tag", "sha": "a" * 40}},
            {"object": {"type": "commit", "sha": "b" * 40}},
            {
                "status": "ahead",
                "ahead_by": 293,
                "behind_by": 0,
                "merge_base_commit": {"sha": "c" * 40},
            },
        ]

        def open_url(request, timeout):
            payload = responses.pop(0)
            return FakeResponse(json.dumps(payload).encode())

        app = {
            "app": "wordcraft",
            "repository": "storytold/wordcraft",
            "qualified_ref": "old-base",
            "qualified_commit": "d" * 40,
        }
        with patch.object(checker.urllib.request, "urlopen", side_effect=open_url) as mocked:
            result = checker.inspect_app(app, 4.0)

        self.assertEqual(result["latest_release"]["tag"], "v0.11.0")
        self.assertEqual(result["latest_release"]["commit"], "b" * 40)
        self.assertEqual(result["drift"]["ahead_by"], 293)
        self.assertEqual(result["drift"]["behind_by"], 0)
        self.assertEqual(result["drift"]["merge_base_commit"], "c" * 40)
        self.assertEqual(mocked.call_count, 4)

    def test_retries_rate_limit_using_retry_after_then_succeeds(self):
        rate_limited = urllib.error.HTTPError(
            "https://api.github.com/test",
            429,
            "rate limited",
            {"Retry-After": "0"},
            None,
        )
        responses = [
            rate_limited,
            {"tag_name": "v0.11.0", "html_url": "https://example.test/release"},
            {"object": {"type": "commit", "sha": "b" * 40}},
        ]

        def open_url(_request, timeout):
            item = responses.pop(0)
            if isinstance(item, BaseException):
                raise item
            return FakeResponse(json.dumps(item).encode())

        app = {
            "app": "wordcraft",
            "repository": "storytold/wordcraft",
            "qualified_ref": "old-base",
            "qualified_commit": "b" * 40,
        }
        with patch.object(checker.urllib.request, "urlopen", side_effect=open_url) as mocked, patch.object(
            checker.time, "sleep"
        ) as sleep:
            result = checker.inspect_app(app, 4.0)

        self.assertEqual(result["latest_release"]["tag"], "v0.11.0")
        self.assertEqual(result["drift"]["status"], "same")
        self.assertEqual(mocked.call_count, 3)
        sleep.assert_called_once_with(0.0)

    def test_retries_transient_network_failure_with_bounded_backoff(self):
        app = {
            "app": "wordcraft",
            "repository": "storytold/wordcraft",
            "qualified_ref": "old-base",
            "qualified_commit": "d" * 40,
        }
        with patch.object(
            checker.urllib.request, "urlopen", side_effect=OSError("temporary network failure")
        ) as mocked, patch.object(checker.time, "sleep") as sleep:
            result = checker.inspect_app(app, 1.0)

        self.assertEqual(result["status"], "unknown")
        self.assertEqual(mocked.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1.0, 2.0])

    def test_retries_all_server_errors_and_closes_error_body(self):
        for status in range(500, 600):
            with self.subTest(status=status):
                error_body = io.BytesIO(b"temporary error")
                error = urllib.error.HTTPError("https://api.github.com/test", status, "server error", {}, error_body)
                with patch.object(checker.time, "sleep"):
                    self.assertEqual(checker.retry_delay(error, 0), 1.0)
                error.close()
        error_body = io.BytesIO(b"temporary error")
        error = urllib.error.HTTPError("https://api.github.com/test", 503, "server error", {}, error_body)
        with patch.object(checker.urllib.request, "urlopen", side_effect=[error, FakeResponse(b'{"ok": true}')]), patch.object(
            checker.time, "sleep"
        ):
            self.assertEqual(checker.github_json("https://api.github.com/test", 1.0), {"ok": True})
        self.assertTrue(error_body.closed)

    def test_retries_conditional_forbidden_only_for_rate_limit(self):
        limited = urllib.error.HTTPError(
            "https://api.github.com/test", 403, "rate limited", {"X-RateLimit-Remaining": "0"}, None
        )
        forbidden = urllib.error.HTTPError("https://api.github.com/test", 403, "forbidden", {}, None)
        self.assertEqual(checker.retry_delay(limited, 1), 2.0)
        self.assertIsNone(checker.retry_delay(forbidden, 1))
        limited.close()
        forbidden.close()

    def test_retry_after_http_date_is_parsed_and_capped(self):
        now = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc).timestamp()
        future = format_datetime(datetime.fromtimestamp(now + 90, timezone.utc), usegmt=True)
        error = urllib.error.HTTPError(
            "https://api.github.com/test", 429, "rate limited", {"Retry-After": future}, None
        )
        with patch.object(checker.time, "time", return_value=now):
            self.assertEqual(checker.retry_delay(error, 0), 30.0)
        error.close()

    def test_nonretryable_http_error_is_not_retried(self):
        error = urllib.error.HTTPError("https://api.github.com/test", 404, "missing", {}, None)
        self.assertIsNone(checker.retry_delay(error, 0))
        error.close()

    def test_api_failure_is_unknown(self):
        app = {
            "app": "wordcraft",
            "repository": "storytold/wordcraft",
            "qualified_ref": "old-base",
            "qualified_commit": "d" * 40,
        }
        with patch.object(checker.urllib.request, "urlopen", side_effect=OSError("offline")):
            result = checker.inspect_app(app, 1.0)
        self.assertEqual(result["status"], "unknown")
        self.assertIn("offline", result["error"])


if __name__ == "__main__":
    unittest.main()
