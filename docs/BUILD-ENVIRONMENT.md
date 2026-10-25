# Local Rust build storage

On the development machine, Cargo is configured in `~/.cargo/config.toml` to
place build artifacts in `~/.cache/cargo-target` and to set `TMPDIR` to
`~/.cache/cargo-tmp`. `~/.profile`, `~/.bashrc`, and the user
`environment.d` entry set the same persistent temporary directory for tools
started outside Cargo. These locations are on the home filesystem, not the
small `/tmp` tmpfs.

Verify both the artifact location and the `TMPDIR` inherited by a Cargo-run
process (the script makes and removes a tiny dependency-free crate in the
persistent temp directory):

```sh
scripts/check-build-storage.sh
```

Expected paths on this machine are `/home/roddy/.cache/cargo-target` and
`/home/roddy/.cache/cargo-tmp`. This machine-local setup is not a repository
default for other contributors. Do not commit build artifacts or secrets from
these cache directories.
