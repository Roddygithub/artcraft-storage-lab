# Owner-authorized ONLYOFFICE retirement

On 2026-11-08 the owner explicitly requested: “on oublie onlyoffice pour gagner
du temps […] le désinstaller de ma machine ainsi que du serveur proxmox”.
This supersedes the earlier preserve-ONLYOFFICE rule. It is not evidence that
ArtCraft already replaces every configured format.

## Verified current state

| Component | Observation |
| --- | --- |
| Proxmox ONLYOFFICE container | Container 112 no longer exists; confirmed by `pct status` and `pct list` |
| Seafile | Local login page and `/api2/ping/` each return HTTP 200 |
| Seafile configuration | No explicit ONLYOFFICE enable assignment remains; installed settings default it to False |
| Seafile rollback configuration | Pre-removal settings backup exists on the server |
| Desktop | `onlyoffice-bin 10.0.0-1` still installed at inspection; exact-package removal launched through polkit and awaits OS authentication |
| Desktop user files | No user documents, settings directories or unrelated dependencies removed |

A full container backup/restore image has not been verified. The current
absence of container 112 does not itself establish a rollback image.
Local package metadata and file inventory are retained privately under the
user's state directory. They are not a binary package backup.

The desktop command is `pkexec /usr/bin/pacman -R --noconfirm onlyoffice-bin`.
It removes only the named package, retaining unrelated dependencies and user
profiles. The password is entered in the OS dialog, never in chat. Removal is
not reported complete until the package database confirms absence.

Further development targets ArtCraft and the required document formats;
ONLYOFFICE regression work is retired. Upstream publication remains LOCKED.
