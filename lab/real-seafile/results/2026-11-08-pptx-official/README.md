# Official DeckCraft PPTX edit/save/reopen

Source `4f4b2dc`; unmodified official DeckCraft **v0.16.0** ZIP SHA-256
`8795d58ab02c30ad25f38525a79ee0e69c40b3d122e223dc04d2703827621f55`,
extracted through `scripts/craft_web_zip.py`. No editor or Seafile patch.

Fresh rootless synthetic Seafile: HTTP **40/40**, focused browser **15/15**,
launcher exit **0**. Offline command groups **19/19**. Option `--pptx` adds the
PPTX route to the disposable lab configuration; the default six-editor candidate
is unchanged. Run with `--pptx --editor deckcraft` and the verified seven-editor
asset snapshot. `--pptx` without a filter runs the combined candidate.

The browser clicked synthetic.pptx in Seafile, typed a unique marker, saved the
same PPTX, observed host confirmation and a new attributed Seafile version,
closed the original page, logged into a new browser context and clicked the file
again. The reopened relay bytes equal readback and retain original slide title
plus marker. No download was observed. This is one synthetic title-box edit;
full PPTX fidelity, arbitrary presentations and legacy PPT/ODP are not proved.

The parent inspected saved/reopened screenshots: the typed marker is visible in
both, the title wraps, and the canvas has an Arial fallback-font warning. Thus
font fidelity is explicitly NOT VERIFIED. No claim of exact rendering is made.
Retained ZIP parts and images were scanned against the run's synthetic credentials
before retention. URLs, accounts, tokens and version IDs are omitted from JSON.
Earlier failed attempts are preserved in sanitized earlier-attempts.json.

Run `python3 lab/real-seafile/results/2026-11-08-pptx-official/verify.py`.
Independent review NOT PERFORMED; HTTPS acceptance remains open. Production
unchanged; project INCOMPLETE; upstream LOCKED.
