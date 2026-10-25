# GR-029 evidence — SoundCraft egui 0.37 WASM compatibility

**Status:** bounded local compatibility slice; GPT REVIEW PENDING. Sol low R3
returned a provisional PASS with no remaining findings in this scope. R1's
accessibility issue and R2's lock-order issue are remediated. It clears the
compile blocker in the local probe, but
does not prove browser or Seafile save behavior.

| Item | Value |
|---|---|
| SoundCraft base | `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588` |
| craft-libs base | `5c874d51eeb3de70e735c8ce87a59a7dedd47675` |
| Prior patches | GR-025 `f8f9da024b80b3292cca1a60ee69eaf4e19c450d7582fac582596fd11aebc331`; GR-027 `e4a63489cfdfc0fd3cfc347a1998347bd92bb0b682ac9a25d1051f887e357e6b`; GR-028 `ff1ced58251397b8077f92ee9b92c7cae1ada25a8a7fe9068c50ba7cdad5901c` |
| craft-ui compatibility patch | [`craft-ui-egui-0.37-compat.patch`](craft-ui-egui-0.37-compat.patch), SHA-256 `5cf2728d20ed74d9fe0521543280d77ce9ef1a5efd3b6f3db3862b6363b06292` |
| SoundCraft compatibility patch | [`soundcraft-egui-0.37-compat.patch`](soundcraft-egui-0.37-compat.patch), SHA-256 `af31ccc5d69ea1e9577e0a7f989077ccafd9e40cfe3643a2e8c8f934cc6fa098` |
| SoundCraft lockfile patch | [`soundcraft-egui-0.37-build-lock.patch`](soundcraft-egui-0.37-build-lock.patch), SHA-256 `d86d74198de55f7f98a4a381d1d18183013f9195c046dd0f56667cbc305f0743`; generated against the lock after GR-025 |

## Implementation notes

The locked SoundCraft app used egui/eframe 0.37 while its pinned `craft-ui`
used egui 0.36. In a scratch checkout, changing the craft-libs workspace
dependency to egui 0.37 and updating five removed `WidgetType` enum references
reduced the app failure from 52 type/API errors to nine SoundCraft-side API
errors. The SoundCraft patch addresses those errors: screenshot delivery moved
to `ScreenshotCallback`, synthetic mouse-wheel events specify
`MouseWheelSource::Unknown`, widget roles use 0.37's variants, track rows expose
selected (not toggled) accessibility state, and the custom gutter scrollbar
uses the public offset getter plus `vertical_scroll_offset`.

The screenshot callback and timeout share an atomic one-shot guard, so a late
frame cannot send a second reply after the request has timed out. Track rows
also mark selected state explicitly for accessibility.

## Commands and results

Against the two pinned scratch checkouts, after applying GR-025/027/028 and
both GR-029 patches:

```text
cargo +1.95.0 check -p soundcraft-web --target wasm32-unknown-unknown   PASS
cargo +1.95.0 check --locked -p soundcraft-web --target wasm32-unknown-unknown   PASS
cargo +1.95.0 test -p soundcraft-ui-egui --lib host_bound_session_routes_save_and_refuses_replacement_and_save_as --locked   1 passed
rustfmt --edition 2024 --check crates/ui-egui/src/control.rs crates/ui-egui/src/panels.rs   PASS
git diff --check   PASS
```

R1 found two minors: track selection was represented as toggled rather than
selected for assistive technology, and the local lock/configuration was not
preserved. R2 confirmed the accessibility fix but found that the first lock
patch repeated the `craft-platform` package already added by GR-025, so the
documented sequence did not apply. The lock delta was regenerated from the
post-GR-025 state. The standalone host-save test had a cold native
test build; compilation of the full integration test suite was stopped after it
began building unrelated test binaries. The
focused library test subsequently passed.

## Review and limits

Neither a browser screenshot callback nor the gutter scrollbar was exercised
in a browser. This is a compile-compatibility
result, not Seafile E2E evidence. Production Seafile and ONLYOFFICE were not
accessed or modified. No upstream artifact was published.

## Independent review

- [R1](REVIEW-INDEPENDENT-R1.md): provisional PASS with two minor findings;
  both addressed.
- [R2 response](REMEDIATION-R2.md): corrected the lock patch's intermediate
  base after the reviewer found the documented order would fail.
- [R3](REVIEW-INDEPENDENT-R3.md): bounded provisional PASS; no blocker, major,
  or minor remains. Browser/Seafile workflow remains NOT VERIFIED.
