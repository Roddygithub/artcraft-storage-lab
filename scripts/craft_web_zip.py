#!/usr/bin/env python3
"""Bounded download and safe extraction for staged Craft Web release ZIPs."""

import os
import stat
import struct
import sys
import time
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_EXTRACTED_BYTES = 1024 * 1024 * 1024
MAX_ZIP_ENTRIES = 10_000
DOWNLOAD_TIMEOUT_SECONDS = 30
MAX_DOWNLOAD_SECONDS = 15 * 60
CHUNK_BYTES = 1024 * 1024
EOCD = struct.Struct("<4s4H2LH")


def _preflight_entry_count(archive, max_entries):
    """Bound central-directory allocation before zipfile builds ZipInfo objects."""
    with open(archive, "rb") as source:
        size = os.fstat(source.fileno()).st_size
        source.seek(max(0, size - (65_535 + EOCD.size)))
        tail = source.read()

    offset = tail.rfind(b"PK\x05\x06")
    if offset < 0 or offset + EOCD.size > len(tail):
        raise zipfile.BadZipFile("ZIP has no valid end-of-central-directory record")
    (signature, disk, directory_disk, disk_entries, total_entries,
     directory_size, directory_offset, comment_size) = EOCD.unpack_from(tail, offset)
    if (signature != b"PK\x05\x06"
            or offset + EOCD.size + comment_size != len(tail)):
        raise zipfile.BadZipFile("ZIP end-of-central-directory record is malformed")
    if disk or directory_disk or disk_entries != total_entries:
        raise ValueError("multi-disk ZIPs are not supported")
    if offset >= 20 and tail[offset - 20:offset - 16] == b"PK\x06\x07":
        raise ValueError("ZIP64 archives are not supported")
    if (total_entries == 0xFFFF or directory_size == 0xFFFFFFFF
            or directory_offset == 0xFFFFFFFF):
        raise ValueError("ZIP64 archives are not supported")
    if total_entries > max_entries:
        raise ValueError(f"ZIP has more than {max_entries} entries")
    # Directory entries must end before the EOCD record itself.
    if directory_offset + directory_size > size - (len(tail) - offset):
        raise zipfile.BadZipFile("ZIP central-directory bounds are invalid")


def download(url, destination, limit=MAX_ARCHIVE_BYTES,
             max_seconds=MAX_DOWNLOAD_SECONDS):
    total = 0
    deadline = time.monotonic() + max_seconds
    with urllib.request.urlopen(url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response, open(destination, "wb") as output:
        while True:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"ZIP download exceeds {max_seconds} seconds")
            chunk = response.read(min(CHUNK_BYTES, limit + 1 - total))
            if not chunk:
                break
            if time.monotonic() >= deadline:
                raise TimeoutError(f"ZIP download exceeds {max_seconds} seconds")
            total += len(chunk)
            if total > limit:
                raise ValueError(f"ZIP download exceeds {limit} bytes")
            output.write(chunk)


def extract(archive, destination, limit=MAX_EXTRACTED_BYTES,
            max_entries=MAX_ZIP_ENTRIES):
    _preflight_entry_count(archive, max_entries)
    with zipfile.ZipFile(archive) as zf:
        infos = zf.infolist()
        if len(infos) > max_entries:
            raise ValueError(f"ZIP has more than {max_entries} entries")
        roots = set()
        names = set()
        for info in infos:
            name = info.filename
            path = PurePosixPath(name)
            mode = info.external_attr >> 16
            if (not name or "\\" in name or path.is_absolute()
                    or ".." in path.parts or stat.S_ISLNK(mode)):
                raise ValueError(f"unsafe ZIP entry: {name!r}")
            normalized_name = path.as_posix()
            if normalized_name in names:
                raise ValueError(f"duplicate ZIP entry: {name!r}")
            names.add(normalized_name)
            file_type = stat.S_IFMT(mode)
            if file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise ValueError(f"unsupported ZIP entry type: {name!r}")
            # A zero type means the creator omitted Unix type bits. We always
            # materialize entries as regular files/directories, never symlinks.
            if path.parts:
                roots.add(path.parts[0])
        if len(roots) != 1:
            raise ValueError("web asset must contain exactly one top-level directory")
        root = roots.pop()
        if f"{root}/index.html" not in names:
            raise ValueError("web asset has no root index.html")
        if not any(n.startswith(root + "/") and n.endswith(".wasm") for n in names):
            raise ValueError("web asset contains no WASM module")
        if sum(i.file_size for i in infos) > limit:
            raise ValueError(f"ZIP contents exceed {limit} bytes")

        destination = Path(destination)
        total = 0
        for info in infos:
            target = destination.joinpath(*PurePosixPath(info.filename).parts)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as source, open(target, "wb") as output:
                while chunk := source.read(CHUNK_BYTES):
                    total += len(chunk)
                    if total > limit:
                        raise ValueError(f"ZIP contents exceed {limit} bytes")
                    output.write(chunk)
        return root


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "download":
        download(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 4 and sys.argv[1] == "extract":
        print(extract(sys.argv[2], sys.argv[3]))
    else:
        raise SystemExit(f"Usage: {sys.argv[0]} download URL DEST | extract ZIP DEST")
