# Independent review — GR-027 validated ftyp bounds (round 3)

**Verdict:** PROVISIONAL, one MINOR.

The exact r3 patch hash matched; reverse-apply check passed against the
reviewed source. The prior `ftyp` bounds finding was resolved. The remaining
finding was that `audio_params` could select an audio track with
`CODEC_ID_NULL_AUDIO`, instead of skipping it and selecting a later decodable
track as Symphonia's helper does. R4 adds that filter and a null-before-valid
track regression. This reviewer did not run builds or tests and could not
verify apply against the base from its checkout. Browser/Seafile remain NOT
VERIFIED.
