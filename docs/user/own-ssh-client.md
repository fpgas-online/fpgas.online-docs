---
type: how-to
owner: documentation maintainers
reader: someone using a board through a site who wants their own ssh client
review: 2026-11-10
---

# How to reach a board with your own ssh client

**You have a board's page open on welland.fpgas.online or ps1.fpgas.online. You want a shell on its host from
your own machine, or to copy files to it**. The terminal in the page needs nothing of this. The Tiny Tapeout site's
board pages offer no `ssh`.

## What you need

- A machine with `ssh` and `scp`.
- The board's page, from the site's list of boards.

## Steps

1. On the board's page, find the section **Accessing directly**. It names the user, the host and the port of
   this board.
2. Copy the `ssh` command under it and run it on your machine. On welland it reads like this, with the board's
   own port:

   ```console
   $ ssh -4 -p 24622 pi@welland.fpgas.online
   ```

   On welland the `-4` is needed: board `ssh` is offered over IPv4 only. The ps1 command has no `-4`.
3. Give the password. On welland the page shows it next to the command. On ps1 the login banner prints it.
4. To copy files to the host, run the `scp` command from the same section in the folder that holds them. It
   copies them into `Uploads` in the home folder:

   ```console
   $ scp -4 -P 24622 * pi@welland.fpgas.online:Uploads
   ```

## Check

The prompt is the host's own shell, and `ls Uploads` lists the files you copied.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| no answer, on welland | the command ran without `-4`, and board `ssh` is offered over IPv4 only | run it again with `-4` |
| `Connection refused`, or no answer | the host is restarting after a reset, or is off | wait a few minutes, then connect again |
| `Permission denied` | the password was mistyped | copy it again from the page or the banner |
| your files are gone | the host was reset | copy them again: a reset clears what the host held |

Whatever you write on a host is gone after its next reset.

## Next

Reaching a board by its own name, with no port number, is planned:
[infra issue #191](https://github.com/fpgas-online/fpgas.online-infra/issues/191).
A Compute Blade at ps1 has no board page; it has its own login:
[How to log in to a host at ps1](../setup/ps1-login.md).
