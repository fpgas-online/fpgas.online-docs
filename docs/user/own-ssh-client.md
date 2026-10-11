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

Whatever you write on a host is gone after its next reset.

## Steps

1. On the board's page, find the section **Accessing directly**. It names the user, the host and the port of
   this board.
2. Copy the `ssh` command under it and run it on your machine. On welland it has this form, with your board's
   port in place of `PORT`:

   ```console
   $ ssh -4 -p PORT pi@welland.fpgas.online
   ```

   Keep the `-4`: on welland, board `ssh` is offered over IPv4 only. The ps1 command has no `-4`.
3. The first time you connect, `ssh` asks whether to continue connecting. Type `yes`.
4. Give the password. On welland the page shows it next to the command. On ps1, `ssh` prints it in a banner
   before it asks for it.
5. To copy files to the host, put only those files in one folder on your machine. In that folder, run the
   `scp` command from the same section. The `*` sends every file in the folder into `Uploads` in the host's
   home folder:

   ```console
   $ scp -4 -P PORT * pi@welland.fpgas.online:Uploads
   ```

## Check

After step 4, a command runs on the host and prints its name:

```console
$ hostname
```

After step 5, `ls Uploads` on the host lists the files you copied.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| `Connection refused`, or no answer | the host is not up, for example after a reset | wait a few minutes, then connect again |
| `Permission denied` | the password was mistyped | copy it again from the page or the banner |

## Next

Reaching a board by its own name, with no port number, is planned:
[infra issue #191](https://github.com/fpgas-online/fpgas.online-infra/issues/191).
A Compute Blade at ps1 has no board page; it has its own login:
[How to log in to a host at ps1](../setup/ps1-login.md).
