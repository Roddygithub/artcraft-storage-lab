# GR-041 focused evidence

Base: `1e94723ad967f5fdec384c938062fcf37daf092a` (`main`, worktree left
uncommitted).

The focused tests use small synthetic data and reduced limits. They cover exact
and over-limit download/extraction, socket and total-deadline timeout wiring,
entry-count rejection before constructing `ZipFile`, ZIP64 and multi-disk
rejection, duplicate/traversal/absolute/backslash names, a Unix symlink,
multi-root and missing required assets, and malformed archive rejection. The
test ZIPs are small; no large files are allocated.

```text
$ bash -n scripts/fetch-craft-web.sh
$ python3 tests/test_gr041_craft_zip_limits.py
........
Ran 8 tests in 0.006s
OK
$ git diff --check
# exit 0
```

Independent exact review round 3 returned **PROVISIONAL PASS**, with no blocker
or major. It confirms the size/count bounds, duplicate/path protections and
negative tests. Round 2's claim that the shell lacked a cleanup trap was a
misread: `fetch-craft-web.sh` installs `trap cleanup EXIT` before staging.
SIGKILL and machine failure cannot run shell cleanup, so a stale `.stage.*`
directory may remain in those cases. See
[`INDEPENDENT-REVIEW-R3.md`](INDEPENDENT-REVIEW-R3.md) for the disposition and
remaining NOT VERIFIED items.

The tests do not exercise the full remote release-fetch flow, active-tree
behavior in a live invocation, or host-protocol compatibility. No Seafile or
ONLYOFFICE service or upstream state was touched.
