# Independent review — GR-027 zero-padded MP4 preflight (round 5)

**Verdict:** PROVISIONAL PASS; no findings.

The exact patch hash matched. The reviewer verified its base and target blobs,
reverse applicability, and the fixes for R1–R4: root-only marker checks,
`ftyp` bounds, skipping `CODEC_ID_NULL_AUDIO`, and preserving the start offset
for zero-padded MP4. The r5 implementation is in the stored patch. Reported
validation is 57 audio-io tests and the locked audio-io WASM check; the reviewer
did not rerun them. Full SoundCraft Web WASM remains blocked by the separate
egui mismatch; browser and Seafile save/version/reopen remain NOT VERIFIED.
