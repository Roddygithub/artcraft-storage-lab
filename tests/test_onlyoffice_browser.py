#!/usr/bin/env python3
"""Offline ONLYOFFICE evidence predicates; no imports of browser/API dependencies."""
import importlib.util
import io
from pathlib import Path
import zipfile

path = Path(__file__).resolve().parents[1] / "lab/real-seafile/run_onlyoffice_browser.py"
spec = importlib.util.spec_from_file_location("onlyoffice_browser", path)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def odt(body="", metadata="", mime="application/vnd.oasis.opendocument.text"):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("mimetype", mime)
        z.writestr("meta.xml", "marker baseline")
        z.writestr("content.xml", f'<office:document-content xmlns:office="{runner.OFFICE}" '
                   f'xmlns:text="{runner.TEXT}"><office:meta>{metadata}</office:meta>'
                   f'<office:body><office:text>{body}</office:text></office:body></office:document-content>')
    return out.getvalue()


def rejects(data):
    try:
        runner.odt_text(data)
    except ValueError:
        return
    raise AssertionError("malformed archive accepted")


def main():
    assert runner.odt_text(odt('<text:p>hello <text:span>mar</text:span>ker</text:p>')) == "hello marker"
    assert runner.odt_text(odt('<text:p>hello</text:p>', 'marker')) == "hello"
    assert "marker" not in runner.odt_text(odt(metadata="marker"))
    rejects(b"not a ZIP")
    rejects(odt(mime="application/zip"))
    for content in (b"<broken", b"<root/>"):
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w") as z:
            z.writestr("mimetype", "application/vnd.oasis.opendocument.text")
            z.writestr("content.xml", content)
        rejects(out.getvalue())
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("content.xml", "<root/>")
    rejects(out.getvalue())

    before = [{"id": "commit1", "rev_file_id": "object1", "creator": "lab-user"}]
    after = [{"id": "commit2", "rev_file_id": "object2", "creator": "lab-user"}] + before
    assert runner.persisted_revision(before, after, "lab-user")
    assert not runner.persisted_revision(before, before, "lab-user")
    assert not runner.persisted_revision(before, after, "other-user")
    assert not runner.persisted_revision([], after, "lab-user")
    for field, value in (("id", "commit1"), ("id", None), ("rev_file_id", "object1"),
                         ("rev_file_id", None), ("creator", "other-user")):
        invalid = [dict(after[0], **{field: value})]
        assert not runner.persisted_revision(before, invalid, "lab-user"), field
    print("ONLYOFFICE offline semantic/version checks passed; browser runtime NOT RUN")


if __name__ == "__main__":
    main()
