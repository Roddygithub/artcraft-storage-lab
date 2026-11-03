#!/usr/bin/env python3
"""Semantic reader regression for DeckCraft native .deckcraft lab saves.

Only synthetic ZIP/JSON documents are used; this test starts no browser or service.
"""
import io
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lab", "real-seafile"))

for _key, _value in (("SEAFILE_URL", "http://127.0.0.1:1/seahub"),
                     ("BRIDGE_URL", "http://127.0.0.1:1/bridge"),
                     ("ONLYOFFICE_URL", "http://127.0.0.1:1/onlyoffice"),
                     ("ADMIN_EMAIL", "synthetic@example.invalid"),
                     ("ADMIN_PASSWORD", "synthetic-not-a-real-password")):
    os.environ.setdefault(_key, _value)

import run_slice as rs  # noqa: E402


def archive(document, mimetype="application/vnd.storyteller.deckcraft+zip"):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as output:
        output.writestr("mimetype", mimetype)
        output.writestr("presentation.json", json.dumps(document))
    return buffer.getvalue()


def raises_value_error(data):
    try:
        rs.deckcraft_text(data)
    except ValueError:
        return True
    return False


def main():
    sample = archive({"slides": [{"title": "Northern Lights", "notes": ["synthetic note"]}]})
    assert rs.deckcraft_text(sample) == ["Northern Lights", "synthetic note"]
    assert raises_value_error(b"not a zip")
    assert raises_value_error(archive({"slides": []}, mimetype="application/zip"))

    missing_mime = io.BytesIO()
    with zipfile.ZipFile(missing_mime, "w", zipfile.ZIP_DEFLATED) as output:
        output.writestr("presentation.json", "{}")
    assert raises_value_error(missing_mime.getvalue())

    invalid_json = io.BytesIO()
    with zipfile.ZipFile(invalid_json, "w", zipfile.ZIP_DEFLATED) as output:
        output.writestr("mimetype", "application/vnd.storyteller.deckcraft+zip")
        output.writestr("presentation.json", "{")
    assert raises_value_error(invalid_json.getvalue())
    print("DeckCraft native parser checks: 5/5 passed")


if __name__ == "__main__":
    main()
