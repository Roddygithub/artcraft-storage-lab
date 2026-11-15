# Offline candidate checks — 2026-11-15

Source `be51c3b577fda9834de4364a35d0784d28f62492` passed all 20 command
groups in `scripts/validate-candidate.py`. The sanitized summary records each
check name, exit code and duration; full command logs remain private.

Reproduce from the repository root:

```sh
uv run --with playwright --with pillow python scripts/validate-candidate.py \
  --output /absolute/new-private-dir
```

The runner covers Python bridge and lab checks, JS host/shim checks, and shell
syntax. It does not establish Seafile runtime, format fidelity, hardware
acceptance, or an independent review.
