# GR-082 release monitor — R1 response

R1 returned **PROVISIONAL** with two MEDIUM and two LOW findings.

- The partial scan is now described accurately: WordCraft/GridCraft completed;
  later GitHub API requests were rate-limited. All-five release pins and
  ahead/behind counts are attributed to separately linked official compare
  results, not to the partial scan.
- The scanner reads and validates `merge_base_commit`; its mocked response and
  assertion use that exact field. The historical scan is preserved and
  identified as pre-fix, with no merge-base evidence claimed from its null
  values.
- Documentation scopes `/releases/latest` to the latest qualifying
  non-prerelease release.
- `checks/monitor-tests.txt` records both test commands and zero exits.

The weekly task is enabled/configured with its next run retained, but
`lastRunStatus` is `never`; unattended execution is **NOT VERIFIED**.
Independent final verification remains pending.
