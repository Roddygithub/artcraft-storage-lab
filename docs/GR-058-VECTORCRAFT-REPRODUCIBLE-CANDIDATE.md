# GR-058 — reproducible VectorCraft candidate

Date: 2026-10-25. Result: **exact-source candidate built; synthetic browser
host roundtrip PASS**. Independent R1 review: **PROVISIONAL PASS**, no findings.
Work-item status: **GPT REVIEW PENDING**; project verdict remains
**INCOMPLETE**.

## Candidate and decision

Built VectorCraft Web from tag `v0.14.0` at exact source commit
`ad0566943ab9741e6356bbc9b53c3cc09895068d`, with the official release's pinned
`craft-fonts` input `a71c20e30af613287c504f7e685ca8fad77752bc`. The final static
candidate is staged at
`/home/roddy/.cache/artcraft-storage-lab/gr058-vectorcraft-static/vectorcraft`,
outside dispatch. No production, Seafile, ONLYOFFICE, or credentials were used;
dispatch is unchanged.

The source pin is independently recorded by `git ls-remote`, detached checkout,
and `git rev-parse` in [build evidence](reviews/GR-058/checks/build.txt). The
VectorCraft source release workflow at this commit pins `craft-fonts` at
`a71c20e30af613287c504f7e685ca8fad77752bc` and enables web fonts
([release.yml lines 29–30](https://github.com/storytold/vectorcraft/blob/ad0566943ab9741e6356bbc9b53c3cc09895068d/.github/workflows/release.yml#L29-L30));
the Trunk post-build hook and optional `CRAFT_FONTS_DIR` are described in
[Trunk.toml lines 12–15](https://github.com/storytold/vectorcraft/blob/ad0566943ab9741e6356bbc9b53c3cc09895068d/apps/vectorcraft-web/Trunk.toml#L12-L15)
and [text build.rs](https://github.com/storytold/vectorcraft/blob/ad0566943ab9741e6356bbc9b53c3cc09895068d/crates/text/build.rs#L1-L8).
The downloaded web ZIP SHA-256 matches its published `SHA256SUMS.txt` entry,
and its `index.html`, JS, and WASM hashes exactly match the three VectorCraft
files recorded by GR-054 from the parent-local static tree. The fresh source
build's `index.html`, JS, and WASM hashes differ from that release bundle; do
not describe the build as byte-identical to the release. The three copied web
fonts and their OFL files do match the release. Full candidate and release
asset hashes plus index references are in the [inventory](reviews/GR-058/inventory.json).

VectorCraft continues to use its page API (`window.vectorcraft`) and the
gateway's existing polling adapter ([`hostpage.py`](../integration/gateway/hostpage.py#L75-L90));
the prior runtime evidence describes its polling/save boundary in
[GR-012](reviews/GR-012/VECTORCRAFT-SEAFILE-E2E-20261023.md). This candidate does not add or claim the
common `?host=parent` protocol. The actual staged WASM opened the synthetic SVG,
the pencil API drew a visible path, `app.save` serialized it, and the current
`hostpage.render` adapter polled and wrote the exact 609-byte editor output to
an isolated loopback fake storage endpoint as synthetic version
`synthetic-v1`; the stored bytes' SHA-256 was
`fad9b3e60c2e76e29214dccdd6edfeb00b5edc9be605aaefddaed8372d3497f2`. A fresh
host/editor session reopened the bytes and `document.inspect` found the path at
the expected geometry. Browser output and screenshot are in the evidence
directory.

## Source, release, and build record

| Item | Exact record |
|---|---|
| Source | `https://github.com/storytold/vectorcraft.git`, tag `v0.14.0`, commit `ad0566943ab9741e6356bbc9b53c3cc09895068d`; tag is lightweight and resolves directly to this commit |
| Optional release input | `https://github.com/storytold/craft-fonts.git`, commit `a71c20e30af613287c504f7e685ca8fad77752bc`; the VectorCraft release workflow at the source commit names this pin |
| Release archive | [`vectorcraft-web-0.14.0.zip`](https://github.com/storytold/vectorcraft/releases/download/v0.14.0/vectorcraft-web-0.14.0.zip), SHA-256 `6f28a8bcee1c5ad6c37c6a0c44058793a40ea4443085866d5f78afb16aba075e`; matched the release `SHA256SUMS.txt` entry |
| Release-to-GR-054 comparison | Release index SHA-256 `55f3e447…faf7800f`, JS `6fefae15…bedd5f01b`, WASM `6ff3616f…b24254d`; these match GR-054's recorded parent-local VectorCraft files |
| Toolchain | Rust/Cargo 1.95.0, Trunk 0.22.0, target `wasm32-unknown-unknown`, Trunk-managed wasm-opt v131 with `-Oz` |
| Build | `CRAFT_FONTS_DIR=/home/roddy/.cache/artcraft-storage-lab/gr058-source/craft-fonts CRAFT_FONTS_REQUIRED=1 RUSTUP_TOOLCHAIN=1.95.0 trunk build --release --locked --dist /home/roddy/.cache/artcraft-storage-lab/gr058-vectorcraft-static/vectorcraft` from `apps/vectorcraft-web` |
| Cargo directories | Existing Cargo target `/home/roddy/.cache/cargo-target`; no `TMPDIR` or target override under `/tmp` |
| Build result | Exit 0; Trunk copied three web font files and their OFL license files. Candidate includes nine files total; `.trunk-lock` is transient and excluded from the inventory. |

The pinned `craft-fonts` commit predates a number of faces listed by this
VectorCraft source. Cargo/Trunk warn that the listed Cairo, Tajawal, Almarai,
IBM Plex Sans Arabic, Noto Kufi Arabic, Amiri, Alexandria, Fustat, Reem Kufi,
Aref Ruqaa, and Gulzar faces are unavailable. The build copied Noto Sans Arabic,
Thai, and Georgian; those six files (fonts plus OFL notices) byte-match the
release ZIP. VectorCraft documents that fetched fonts are optional and missing
faces are skipped ([fonts.rs](https://github.com/storytold/vectorcraft/blob/ad0566943ab9741e6356bbc9b53c3cc09895068d/apps/vectorcraft-web/src/fonts.rs#L1-L5));
the release ZIP's `HOSTING.md` says Arabic may render as boxes when its font
files are absent ([release archive](https://github.com/storytold/vectorcraft/releases/download/v0.14.0/vectorcraft-web-0.14.0.zip)). Missing optional
faces and their runtime impact remain explicit;
the smoke covers the synthetic Latin SVG path, not those scripts/fonts.

The source repository's [release workflow](https://github.com/storytold/vectorcraft/blob/ad0566943ab9741e6356bbc9b53c3cc09895068d/.github/workflows/release.yml#L23-L30)
delegates to `storytold/craft-common-actions/.github/workflows/release.yml@main`;
that workflow reference floats. The verified release ZIP has 35 files; the
staged candidate has the nine runtime files generated by this build, not a
repackaging of the archive's ancillary documentation and licenses. A complete
immutable release-builder/toolchain
snapshot was not available in the retained evidence. Accordingly, exact source
and pinned-font candidate reproducibility is established for the commands
above, but release-binary reproducibility is **NOT VERIFIED**. The candidate's
three principal files differ from the archive; hashes are in the comparison
matrix in `inventory.json`.

## Reproduction and checks

See [evidence README](reviews/GR-058/README.md) for source validation, checksum
verification, build commands, and browser harness. Verify the final staged
candidate with:

```sh
python3 docs/reviews/GR-058/verify_candidate.py
```

The verifier checks exact file membership, all candidate file sizes and
SHA-256 hashes, and every file reference in `index.html`. The browser command
replays the edit/save/reopen against the staged build and current VectorCraft
page-API host adapter, backed by loopback synthetic storage.

## Evidence limits

| Boundary | Result |
|---|---|
| Exact source tag/commit and official pinned font input | **VERIFIED** |
| Official release archive checksum and comparison to GR-054 bundle bytes | **VERIFIED**; release JS/WASM/index hashes match GR-054 |
| Rebuild byte-identical to release archive | **NOT VERIFIED**; JS/WASM/index hashes differ |
| Actual source-built editor open/edit/save/fresh reopen through current host page API | **PASS** in isolated synthetic storage; not Seafile |
| Persistent Seafile version/history/readback/reopen using this exact build | **NOT RUN**. Parent reports real Seafile 12.0.14's `/thirdparty-editor/file-save/` endpoint is 404; no service was contacted in this task. |
| Common `?host=parent` protocol | **NOT CLAIMED**; VectorCraft uses its page API |
| Production, credentials, ONLYOFFICE, dispatch changes, upstream issues/PRs/RFCs | **NOT USED** |
| Independent review | R1 **PROVISIONAL PASS**, no findings; see [`INDEPENDENT-REVIEW-R1.md`](reviews/GR-058/INDEPENDENT-REVIEW-R1.md) |

This is a staged candidate, not a dispatch promotion, deployment-ready bundle,
Seafile persistence result, or upstream publication.
