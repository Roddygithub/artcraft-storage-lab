# Craft Web asset ingestion

The release fetcher is an **ingestion tool**, not an installer. It requires an
explicit release tag and asset SHA-256, stages under `integration/static/candidates/`,
and refuses to overwrite an existing candidate or active app directory.

```sh
gh release view vX.Y.Z --repo storytold/wordcraft --json assets \
  --jq '.assets[] | select(.name | test("^wordcraft-web-.*\\.zip$")) | {name, digest}'
./scripts/fetch-craft-web.sh wordcraft vX.Y.Z <64-hex-digit-asset-sha256>
```

GitHub's `digest` value is prefixed with `sha256:`; pass only the 64 hex digits.

The script checks the downloaded archive digest and rejects unsafe ZIP paths,
symlinks, ambiguous top-level layouts, and archives without `index.html` and a
WASM module. It also refuses symlinked candidate directories. Each staged
directory contains `ARTIFACT-PROVENANCE.txt` with the source release and digest.

**A digest proves which archive was fetched; it does not prove that the app
implements this repository's host protocol.** The script deliberately does not
copy staged files into `integration/static/<app>/`. Promote only after checking
the exact WASM/JS build against the app's required Open/Save/ACK behavior and
recording that evidence. Prefer app builds produced from the pinned source and
adapter patches when the upstream release lacks that protocol.

The existing `integration/static/<app>/` tree remains the active build selected
by the dispatcher. Generated downloads are gitignored and must not be treated as
reviewed or deployable merely because their checksum matches.
