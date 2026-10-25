# GR-029 independent review — round 1

**Reviewer:** GPT-6.1 Sol low
**Result:** PROVISIONAL PASS with two MINOR findings. No blocker or major
defect found. This is not a project-level GPT verdict.

## Findings and remediation

1. **Track selection accessibility state:** egui 0.37's
   `WidgetInfo::selected(Role::ListItem, ...)` sets AccessKit's toggled state,
   not selected. Fixed in `soundcraft-egui-0.37-compat.patch` by clearing the
   toggled state and explicitly setting selected on the row's AccessKit node.
2. **Build recipe was not reproducible from the bundle alone:** the locked
   result depended on a regenerated scratch lockfile and local craft-ui path
   override. Fixed by storing `soundcraft-egui-0.37-build-lock.patch` and adding
   the exact local `[patch]` configuration to the GR-029 report.

## Other review conclusions

- Both patch hashes matched and the reviewer verified exact zero-fuzz
  application against both pinned Git bases, with SoundCraft patch order
  GR-025 → GR-027 → GR-028 → GR-029.
- Screenshot callback and timeout use an atomic one-shot guard; a timeout
  prevents a late callback from sending a second reply. Expiry remains
  frame-driven and cannot advance while rendering is suspended.
- Synthetic wheel source and gutter-scroll target handling were sound by
  inspection. Browser runtime remains untested.
- Seafile version creation and fresh reopen remain NOT VERIFIED.

The implementation changed the SoundCraft patch after this review to address
the accessibility finding and preserve the exact lockfile; the revised hashes
are listed in the GR-029 README. A second independent review is pending.
