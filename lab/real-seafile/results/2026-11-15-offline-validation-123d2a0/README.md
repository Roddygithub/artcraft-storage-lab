# Offline candidate validation — `123d2a0`

Command: `uv run --with playwright --with pillow python3 scripts/validate-candidate.py --output <private-output-dir>`

Result: **21/21 command groups passed**, 0 failed, against exact HEAD `123d2a0ca8435e93e37b6d2f31fb73ac016fc5fb`. The run includes bridge, launcher (including CE12 isolation), browser fixtures, save/reopen fixtures, scope and security checks. It is offline evidence only; it does not verify the owner's server, HTTPS runtime, physical hardware, broad format fidelity or production safety. `summary.json` and every command log are retained here.
