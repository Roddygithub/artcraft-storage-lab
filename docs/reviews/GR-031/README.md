# GR-031 evidence bundle — SoundCraft Seafile E2E

Scope: actual SoundCraft Web/WASM open, edit, Seafile version save, ACK, and
fresh Seahub file-list reopen on an isolated synthetic stack.

| Artifact | SHA-256 | Purpose |
|---|---|---|
| [`soundcraft-seafile-save-confirmed-20261025.png`](runtime/soundcraft-seafile-save-confirmed-20261025.png) | `8444ebf06ccee0c7b302f20f8cedbe6757d12bc3d9b47ca82c765f9090b03bc9` | Seafile version confirmation after adding `Audio 2` |
| [`soundcraft-seafile-reopen-20261025.png`](runtime/soundcraft-seafile-reopen-20261025.png) | `2b338884d73ff97b5e98b425a68a1bcc6801d6b0337b8712462bf9d10811f2b5` | Fresh Seahub file-list reopen showing all three tracks and clean state |

The final Seafile API readback is 6,877 bytes, SHA-256
`895bce8fa565730ded872bbf1dd1746ddddc0345e72d9485279e3d987a5a3aff`, with
file ID `9dcd6e06ab96d7e6f1ffc46b3a073ceeb7645c46` and head
`d2ffd245b443e291d0dd956e3448f7e9612dfc7b`. The synthetic fixture and built
Web assets are not included.

The exact editor-to-gateway message hash, optimized WASM bundle, production
security, and ONLYOFFICE regression remain NOT VERIFIED. SoundCraft is not in
the committed dispatch configuration.

Independent reviews: [R1](REVIEW-INDEPENDENT-LUNA-HIGH-R1.md) returned a
bounded PROVISIONAL PASS with three minor qualifications. [R2](REVIEW-INDEPENDENT-LUNA-HIGH-R2.md)
verified the documentation remediations and returned PROVISIONAL PASS. Save
As/export browser rejection and independently verified Seafile response bytes
remain evidence gaps.
