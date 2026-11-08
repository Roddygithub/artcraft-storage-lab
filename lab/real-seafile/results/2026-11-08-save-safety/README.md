# GR-086 safety/launcher replay

Candidate `7380e4629e0815e2088fae486cbedaa25d27782d`: HTTP **48/48**, then
focused corrected-layout WordCraft Chromium **28/28**. This is the old lab
configuration, not the final six-editor replay.

- `slice.json`, `browser.json`: sanitized check names/status and private raw hashes.
- `provenance.json`: ten source/config hashes matching Git and the snapshot,
  exact 66 served asset hashes, five archive pins, screenshot and private log hashes.
- Three original PNGs: initial document, first save, second save after fresh reopen.
- `SOURCE-REVIEW.md`: bounded GPT source verdict and original findings.
- `SHA256SUMS`: retained artifact inventory.

The parent visually inspected the screenshots; CRC/framing checks passed and
there are no text/EXIF chunks. Runtime URLs, capabilities, credentials and
library/account identifiers are omitted. Runtime/import/cleanup chronology is
parent-reported; the reviewer did not independently replay it.

Reproduction: `python3 lab/real-seafile/local.py --help`, with independently
pinned assets and a fresh run directory. The exact snapshot source is identified
in provenance; current default configuration has subsequently changed.
Offline: `node tests/bridge/test_host.mjs`, `python3 tests/lab/test_local.py`,
`python3 tests/bridge/test_bridge.py`.

Project INCOMPLETE; upstream LOCKED. This is not Aptarchy completion.
