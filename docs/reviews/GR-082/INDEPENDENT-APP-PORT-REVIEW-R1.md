# GR-082 Wave 1 app-port review R1

**Verdict: PROVISIONAL — remediation required.** Read-only review of the first
archived patch set for WordCraft, GridCraft, PdfCraft and PhotoCraft. No code,
tests or builds were changed or run by the reviewer. VectorCraft was outside
this patch review.

## Findings

1. **HIGH — GridCraft patch omitted the native XLSX admission check.** The
   source clone had an extension/sniff gate, but the archived patch did not.
   Generic `file.open` accepts text-like input with an `.xlsx` name, which could
   create a replacement workbook under the selected file identity.
2. **HIGH — PhotoCraft patch omitted its local `craft-platform` snapshot.** The
   manifest referenced the identity transport but the patch did not include the
   referenced directory.
3. **MEDIUM — WordCraft/GridCraft patches contained stale transport packaging
   checksums** for lab-root Cargo files that do not belong in relocated app
   patches.
4. **MEDIUM — final validation was not consistently bound to final patch bytes.**
   Earlier WordCraft/GridCraft build logs ended during compilation; PhotoCraft's
   report described the prior Git transport pin and patch hash.
5. **MEDIUM — PdfCraft remained unqualified.** Its first report recorded native
   tests and locked WASM check timing out before tests ran, and the first patch
   used the remote transport Git pin.

The complete independent review text and hashes are captured in the parent
turn. The review remains provisional until a final-state R2 checks the
remediated patches and validation records.
