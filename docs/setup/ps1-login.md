---
type: how-to
owner: documentation maintainers
reader: someone who wants a shell on a Compute Blade at ps1
review: 2026-11-10
---

# How to log in to a host at ps1

This page shows how to open a shell on a Compute Blade at ps1 from your own machine. It is for a visitor or a
maintainer. It does not cover the welland hosts: their board pages give the command.

## What you need

- A machine with `ssh`.
- The number in the blade's name, such as 16 for pi16 at ps1.

## Steps

```{include} ../sites/ps1-login.inc
```

## Next

To check a board from the blade, install the packages first:
[How to install the Acorn packages](../boards/acorn/setup/packages.md). Then run the check:
[How to run the Acorn check on a Compute Blade](../boards/acorn/checks/compute-blade.md).
