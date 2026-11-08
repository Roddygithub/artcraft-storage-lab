# Current Craft-only WordCraft HTTPS replay

Application source `4f4b2dc`; documentation-only drift is listed in provenance.
Fresh rootless synthetic Seafile with distinct HTTPS origins for Seafile and
bridge, official unmodified WordCraft v0.13.2 and the layout DOCX fixture.
HTTP **40/40**, browser **28/28**, launcher exit **0**. No ONLYOFFICE service.

The browser typed and saved two edits, with a fresh authenticated Seafile
file-list reopen between saves. Two new user-attributed versions and retained
text are asserted. The first relay equals persisted bytes. The structural
verifier checks referenced header/footer text, PAGE instructions, table cells,
page breaks, geometry and paragraph style references across both saves.
No final reopen after save two is claimed.

Temporary TLS port-8443 routes on desktop and Proxmox and a private SSH forward
connected the isolated lab. Existing port-443 handlers were preserved. Before/
after Serve configurations were compared exactly; both restored successfully,
with no cleanup errors. Production Seafile settings and user documents were not
changed. Raw origins, Serve snapshots, account/token/version data remain private.
Public transport.json records only scheme/isolation and TLS verification scope.
The stdlib HTTP slice uses default certificate verification; Chromium in the
existing harness uses ignore_https_errors=True. This is automated HTTPS
save/reopen evidence, not human desktop acceptance, a real-hardware WebGPU test,
clipboard validation, full font fidelity or an unload-guard validation.

Synthetic retained documents/images were scanned against generated lab credentials.
Only the reopened-saved screenshot is retained; its visual inspection is recorded
in the project checkpoint. No arbitrary-document compatibility is claimed.

Run `python3 lab/real-seafile/results/2026-11-08-wordcraft-https-current/verify.py`.
Independent review NOT PERFORMED; project INCOMPLETE; upstream LOCKED.
