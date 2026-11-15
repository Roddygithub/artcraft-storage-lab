# Offline candidate validation — `11b75a2`

Command: `uv run --with playwright --with pillow python scripts/validate-candidate.py --output /home/roddy/.cache/artcraft-validation-11b75a2`

Result: **20/20 command groups passed**, 0 failed, at source
`11b75a23be5e263f9bb7b4b9cb332caa2158bd6d`. The run re-executed bridge,
launcher, fixture, edit/save, scope, and security checks. This is the offline
suite only; it does not cover owner-server WOPI behavior or physical hardware.
The summary and per-command logs are retained beside this file.
