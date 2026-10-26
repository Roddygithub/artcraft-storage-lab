# GR-060 evidence bundle — in progress

This bundle records the preparation of a dedicated gateway LXC; it does not
claim Tailscale enrollment or a migrated Seafile route.

Verified locally:

- New non-privileged Debian 13 LXC provisioned with a DHCP interface, 2 vCPU,
  1 GiB RAM and 8 GiB root disk.
- Tailscale 1.104.2 installed from its official Debian stable repository.
  Before pause, `tailscale status` reported `NeedsLogin`.
- Before pause, the gateway unit ran as the `artcraft` system account and
  bound only to loopback port 8777. Health and static index returned 200.
- The exact staged WordCraft candidate passes the GR-055 file membership,
  size/hash and index-reference verifier.
- The LXC was cleanly stopped at the owner’s request and Proxmox auto-start is
  disabled. It remains provisioned for resume and uses no runtime CPU/RAM.
- Existing GR-059 origin remains in Seahub settings and continues serving the
  validated route. The desktop gateway remains active.

No Tailscale key, account secret, hostname, private IP, Seafile library ID,
user identity, or session capability is retained. Login/authentication is a
human-owned step; a browser page was opened for Tailscale sign-in. The owner
paused the work before completing it. Until resumed, Tailscale Serve is not
configured and the LXC remains stopped.

Project GPT remains **INCOMPLETE**; upstream publication remains **LOCKED**.

## Independent review

Independent R1–R2 returned bounded PROVISIONAL PASS. R1's STATUS wording MINOR
is closed: local checks are explicitly described as passing before shutdown.
See [`INDEPENDENT-REVIEW-R1.md`](INDEPENDENT-REVIEW-R1.md) and
[`INDEPENDENT-REVIEW-R2.md`](INDEPENDENT-REVIEW-R2.md). No live Proxmox/LXC
check was performed by the reviewers; enrollment and route migration remain
pending.
