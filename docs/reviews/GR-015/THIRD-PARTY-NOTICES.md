# GR-015 patch provenance and notices

Status: **not approved for distribution or upstream submission**. This inventory
records source provenance; it is not a legal compatibility opinion.

The patch artifacts are diffs, not vendored source trees. They still contain
context copied from upstream files, so keep the original file headers and source
revision references with each artifact.

| Artifact | Exact source | License evidence | Handling |
| --- | --- | --- | --- |
| `seahub-12.0.14.patch` | `haiwen/seahub` commit `1e9bde801b4360c14d784d9681d4261abc233a8b` | Root `LICENSE.txt` at that revision says Apache License 2.0; individual changed files retain Seafile copyright headers | Preserve the source SHA and license reference; do not relabel the patch MIT/Apache without a file-level compatibility review |
| `seafile-server-12.0.14.patch` | `haiwen/seafile-server` commit `32ed9c69594c9faa5cea28024403fcde362589ec` | Root `LICENSE.txt` at that revision says AGPLv3 with an OpenSSL linking exception | Keep distinct from the repository's dual MIT/Apache license; do not distribute or combine binaries without an explicit compatibility review |

The patch files were built and exercised in the isolated synthetic GR-015
runtime; they have not been installed in production, published, or approved for
redistribution. Any upstream submission must follow each target repository's
contribution and licensing requirements and retain its own provenance.
