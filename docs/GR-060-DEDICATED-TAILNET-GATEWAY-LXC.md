# GR-060 — dedicated tailnet gateway LXC

Date: 2026-10-25
Status: **PAUSED by owner — device authentication pending**

## Goal

Move the ArtCraft Seafile gateway off the developer desktop into a dedicated,
non-privileged Debian 13 LXC. When enrolled, Tailscale Serve will give it a
separate HTTPS hostname, preserving the cookie-origin separation required by
Seahub. The working GR-059 gateway remains in service until the new LXC has
been authenticated and its browser/Seafile flow is independently checked.

## Provisioned state

- Created one new Debian 13 LXC with 2 vCPU, 1 GiB RAM, 512 MiB swap and an
  8 GiB thin-provisioned root filesystem. It uses one DHCP interface on the
  existing LAN bridge. It is unprivileged; no routes are advertised.
- Installed the official Tailscale stable package (version 1.104.2) and
  enabled `tailscaled`. The host TUN device is passed through only to this
  container. Its current Tailscale state is `NeedsLogin`; **the LXC is not yet
  enrolled and no HTTPS Serve hostname is active**.
- Copied the GR-055 WordCraft gateway, dispatch config and exact four-file
  candidate into `/opt/artcraft/integration`. The private gateway environment
  file was transferred outside Git; it contains no Seafile account token.
- Added a systemd service running as a dedicated unprivileged `artcraft`
  account. It binds only to `127.0.0.1:8777` and uses read-only application
  files and systemd sandbox controls.
- Before pausing, local-only health check and WordCraft static index each
  returned HTTP 200. The GR-055 candidate verifier passes against the staged
  files.
- Seahub still points at the working GR-059 desktop Serve origin. No Seahub
  setting, Tailscale configuration on Proxmox, or ONLYOFFICE setting has been
  changed for this GR-060 step.
- At the owner’s request, LXC 114 was cleanly shut down and its Proxmox `onboot`
  flag disabled. It remains on disk for resumption and consumes no runtime CPU
  or RAM. The validated GR-059 route and desktop gateway remain active.

## Pending steps

1. Resume the LXC and complete owner-authenticated Tailscale enrollment. No auth
   key or password is stored in the repository or passed through chat.
2. Confirm the enrolled node is private to the tailnet and configure
   Tailscale Serve to proxy HTTPS to the loopback gateway.
3. Back up the current Seahub settings again, switch only
   `ARTCRAFT_ACTION_URL` to the new Serve origin, and restart Seahub with a
   rollback path to the known-working GR-059 config.
4. Repeat the real synthetic Seafile WordCraft open/edit/save/version/fresh
   reopen flow through the LXC origin. Recheck ONLYOFFICE open behavior and
   keep its configuration untouched.
5. Remove the desktop gateway only after the new route passes and a reviewer
   accepts the migration. Retain the GR-059 rollback archive until then.

## Evidence and limits

See [GR-060 evidence](reviews/GR-060/README.md) for local checks. This is not a
completed tailnet enrollment, public HTTPS endpoint, deployment review, or
project GPT PASS. GR-059 remains the verified live route. The project verdict
is **INCOMPLETE** and upstream publication remains **LOCKED**.
