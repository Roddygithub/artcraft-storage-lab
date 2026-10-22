#!/usr/bin/env python3
"""Unit checks for the gateway's security-critical logic.

These are the rules that must hold no matter what the network does. They need
no Seafile instance: they exercise the gateway's own code.

    python3 tests/test_gateway_unit.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "integration"))

from gateway.server import Gateway, load_dispatch  # noqa: E402
from gateway.sessions import SessionStore  # noqa: E402

FAILURES = []


def check(name, condition, detail=""):
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    if not condition:
        FAILURES.append(name)
    return condition


class FakeSeafile:
    """Just enough of the Seafile client for the gateway's checks."""

    def __init__(self, permission="rw", obj_id="aaaa", content=b"hello"):
        self.permission = permission
        self.obj_id = obj_id
        self.content = content
        self.written = []
        self.detail_calls = 0

    def file_detail(self, repo_id, path):
        self.detail_calls += 1
        return {"id": self.obj_id, "permission": self.permission, "size": len(self.content)}

    def download(self, repo_id, path):
        return self.content

    def thirdparty_file_content(self, access_token):
        return self.content

    def update_file(self, repo_id, path, data):
        self.written.append((repo_id, path, data))
        self.obj_id = "bbbb"
        return self.obj_id


def make_gateway(seafile, dispatch=None):
    dispatch = dispatch or {
        "xlsx": {"app": "gridcraft", "url": "/artcraft/gridcraft/?host=parent"},
        "docx": {"app": "wordcraft", "url": "/artcraft/wordcraft/?host=parent"},
    }
    return Gateway(seafile, dispatch)


def main():
    # ---- the extension rule ------------------------------------------------
    gw = make_gateway(FakeSeafile())
    check("the extension is the one after the last dot",
          gw.app_for("report.final.docx") is not None and gw.app_for("archive.tar.gz") is None,
          "report.final.docx -> docx")
    check("the extension is lowercased",
          gw.app_for("REPORT.XLSX") is not None, "REPORT.XLSX -> xlsx")
    check("a file with no dot has no editor", gw.app_for("README") is None)

    # ---- a read-only session cannot write ---------------------------------
    seafile = FakeSeafile(permission="r")
    gw = make_gateway(seafile)
    session, error = gw.open_session_direct("repo", "/a.xlsx")
    check("a read-only file opens in view mode", session is not None and session.can_edit is False,
          f"can_edit={getattr(session, 'can_edit', None)}")
    result, status = gw.save(session, b"payload")
    check("a read-only session cannot write", status == 403 and result["ok"] is False, str(result)[:120])
    check("a refused write writes nothing", seafile.written == [], f"{len(seafile.written)} write(s)")

    # ---- the permission is re-read on every write --------------------------
    seafile = FakeSeafile(permission="rw")
    gw = make_gateway(seafile)
    session, _ = gw.open_session_direct("repo", "/a.xlsx")
    check("an editable file may write", session.can_edit is True)
    # the permission is taken away while the editor is open
    seafile.permission = "r"
    result, status = gw.save(session, b"payload")
    check("a revoked permission stops the write", status == 403 and result["ok"] is False,
          f"HTTP {status}")
    check("the revoked write wrote nothing", seafile.written == [])

    # ---- a stale session is refused ---------------------------------------
    seafile = FakeSeafile(permission="rw", obj_id="aaaa")
    gw = make_gateway(seafile)
    session, _ = gw.open_session_direct("repo", "/a.xlsx")
    seafile.obj_id = "cccc"          # somebody else saved
    result, status = gw.save(session, b"payload")
    check("a stale save is refused", status == 409 and result.get("conflict") is True, f"HTTP {status}")
    check("the refused stale save wrote nothing", seafile.written == [])

    # ---- a current session writes -----------------------------------------
    seafile = FakeSeafile(permission="rw", obj_id="aaaa")
    gw = make_gateway(seafile)
    session, _ = gw.open_session_direct("repo", "/a.xlsx")
    result, status = gw.save(session, b"payload")
    check("a current save is accepted", status == 200 and result["ok"] is True, str(result)[:120])
    check("the write happened", len(seafile.written) == 1)
    check("the session now holds the new content id", session.file_id == "bbbb",
          f"file_id={session.file_id}")

    # ---- the document size limit ------------------------------------------
    seafile = FakeSeafile()
    gw = make_gateway(seafile)
    gw.max_bytes = 10
    session, _ = gw.open_session_direct("repo", "/a.xlsx")
    result, status = gw.save(session, b"x" * 11)
    check("a document over the limit is refused", status == 413 and result["ok"] is False,
          f"HTTP {status}")
    check("the oversized save wrote nothing", seafile.written == [])

    # ---- an unknown extension is refused ----------------------------------
    gw = make_gateway(FakeSeafile())
    session, error = gw.open_session_direct("repo", "/a.unknownext")
    check("an extension with no editor is refused", session is None and error, str(error)[:100])

    # ---- the session store -------------------------------------------------
    store = SessionStore(ttl=60, idle_ttl=30, max_sessions=3)
    a = store.create(repo_id="r", path="/a", name="a", file_id="1", user="u", can_edit=True,
                     access_token="t", app="gridcraft")
    check("a session is created with an unguessable id", len(a.sid) >= 24, f"{len(a.sid)} chars")
    check("a session is found", store.get(a.sid) is not None)
    check("an unknown session is not found", store.get("nope") is None)
    for i in range(5):
        store.create(repo_id="r", path=f"/{i}", name="x", file_id="1", user="u", can_edit=True,
                     access_token="t", app="gridcraft")
    check("the session store is capped", len(store._sessions) <= 3, f"{len(store._sessions)} sessions")
    store.ttl = 0
    check("an expired session is not found", store.get(a.sid) is None)

    # ---- the dispatch table ------------------------------------------------
    dispatch = load_dispatch()
    check("the dispatch table is read from the file", isinstance(dispatch, dict) and dispatch)
    check("every dispatch entry names an app and a url",
          all("app" in v and "url" in v for v in dispatch.values()), str(dispatch)[:120])
    check("the dispatch keys carry no dot", all("." not in k for k in dispatch), str(list(dispatch)))
    # Only the applications that speak the ?host=parent bridge name it in their
    # URL. VectorCraft is driven by its own page API instead, so its URL does
    # not claim a contract it does not implement (REVIEW-04, G4).
    bridge_apps = {"pdfcraft", "gridcraft", "wordcraft"}
    for ext, entry in dispatch.items():
        if entry["app"] in bridge_apps:
            check(f"the {ext} url asks for the host mode", "host=parent" in entry["url"],
                  entry["url"])
        else:
            check(f"the {ext} url does not claim the host mode",
                  "host=parent" not in entry["url"], entry["url"])

    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s): {', '.join(FAILURES)}")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
