# GR-040 — ONLYOFFICE synthetic preservation regression

## Result

The existing Seafile-to-ONLYOFFICE route completed an actual browser edit,
created two Seafile file versions, and reopened the final edit from the Seafile
file list in a new editor page. This closes the **synthetic ONLYOFFICE
regression** check for the current remediation. It does not establish
production-readiness or change the project-level GPT verdict: it remains
**INCOMPLETE**, and upstream publication remains locked.

## Runtime and procedure

- Synthetic Seahub and Seafile C-fileserver, loopback ports only:
  `127.0.0.1:18000`, `:18082`, and `:18777`.
- ONLYOFFICE Document Server image:
  `docker.io/onlyoffice/documentserver@sha256:5ed447a097b368e97de8c25ba5ef53c425acfa1bb084e33b8a0de4a7a1e2099c`.
  The loaded editor resources identify version `8.0.1-31`.
- Seahub source revision `dce43b88568f2963ede843a6c10cb63e2667ac88` and C-fileserver source revision `cc778584492f4e7132da7b47b447e5b4cd83d1bc`; both are the lab's local synthetic patched checkout, not an upstream release build.
- Test document: `/synthetic.docx` in the synthetic `ArtCraft Synthetic` library.

Flow exercised:

1. Open the synthetic DOCX through Seahub's regular file route and verify the
   actual ONLYOFFICE editor loads in desktop mode.
2. Add `gr039seafilecommit`, wait for ONLYOFFICE's `All changes saved` status,
   and close the editor. Seahub receives the ONLYOFFICE callback and commits a
   new version.
3. Reopen that version, add `gr040onlyofficeack`, wait for the same editor
   status, and close it. Seahub commits another version.
4. Read the file through Seafile's authenticated file API, validate the DOCX
   ZIP, inspect `word/document.xml`, then reopen it in a fresh Seahub route and
   by clicking `synthetic.docx` in the library listing.

The fresh editor showed both markers. The final API readback is 24,960 bytes,
SHA-256 `861c00c56e1b9ae42d1d99f5ae9feed6e2d0a038178fbc6b41343e2559c9c2fa`;
the DOCX ZIP validates and contains both markers. Details are in
[`reviews/GR-040/README.md`](reviews/GR-040/README.md) and the sanitized
[runtime transcript](reviews/GR-040/runtime/sanitized-runtime-transcript.txt).

## Rollback and limits

ONLYOFFICE was temporarily configured **only in the synthetic Seahub
container** for `.docx`; ArtCraft dispatch was disabled for this route. The
initial callback attempt exposed an internal loopback reachability problem. It
was fixed inside the synthetic runtime using a pasta host-loopback mapping and
a loopback-only proxy; the test then produced successful callbacks and durable
versions. Temporary Seahub settings and the generated env file were removed
after evidence capture. The still-running synthetic Document Server container
retains test-only environment configuration, and its host mapping remains in
place; both are local test infrastructure. No production Seafile/ONLYOFFICE
instance, configuration, or document was accessed or changed.

This verifies the lab's synthetic patched stack and one DOCX flow only. It does
not verify the deployed production version, other document types, production
TLS/proxy/CSP/CSRF controls, external network isolation, or all supported
ONLYOFFICE versions. It does not prove editor-callback byte-for-byte identity;
the retained proof is the committed Seafile head, history growth, DOCX
readback, and fresh rendering of the exact markers.
