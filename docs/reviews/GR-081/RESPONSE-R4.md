# GR-081 response to independent R4 code/security review

R4 returned **PROVISIONAL FAIL** with two MAJOR findings: same-name replacement
can still be stored over the selected file, and current-route ONLYOFFICE
preservation remains unverified. Both remain open. We will not claim that
filename checks establish document identity or that the ONLYOFFICE regression
is caused by ArtCraft.

R4 confirmed that the missing-name and dirty-state-latch R3 findings are closed
by source inspection. It also confirmed the static index confinement and
five-route verifier fixes by source inspection, with runtime exercise still
unverified. No new code/security findings were reported.

A proposed edit to the existing protocol test file was reverted before this
review response was finalized. The test suite was not run and test files are
unchanged in the current candidate.

The project GPT FAIL on `70fa192ed5d414daf28087315f0f77f8312e98b5` remains in
force. A fresh project review cannot establish PASS while the save-identity and
ONLYOFFICE gates remain open. Upstream publication remains locked.
