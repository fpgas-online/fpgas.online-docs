#!/usr/bin/env python3
"""Export documentation files from origin/main of sibling repositories.

Usage: export_sources.py [REPO ...]

Writes tmp/src/<repo>/<path> for every path listed for the repo below, after
fetching origin. Reads the repo's default branch on origin (main, except
where noted), never the working tree, because the local checkouts may be on
feature branches.
"""
import subprocess
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent
PARENT = DOCS.parent

REPOS = {
    # key: (directory name, origin ref, paths)
    "test-designs": ("fpgas.online-test-designs", "origin/main", [
        "README.md",
        "docs/verify-hardware.md",
        "docs/hardware/README.md",
        "docs/hardware/site-welland.md",
        "docs/hardware/site-ps1.md",
        "docs/hardware/arty-a7.md",
        "docs/hardware/arty-a7-pin-mapping.md",
        "docs/hardware/acorn.md",
        "docs/hardware/acorn-pinmap.md",
        "docs/hardware/acorn-pcie-programming.md",
        "docs/hardware/acorn-pinmap-rpi5-wiring.png",
        "docs/hardware/acorn-pinmap-computeblade-wiring.png",
        "docs/hardware/netv2.md",
        "docs/hardware/netv2-pin-mapping.md",
        "docs/hardware/fomu-evt.md",
        "docs/hardware/fomu-pin-mapping.md",
        "docs/hardware/tt-fpga.md",
        "docs/hardware/tt-fpga-pin-mapping.md",
        "docs/hardware/pmod.md",
        "docs/hardware/rpi-hat-pmod.md",
        "docs/hardware/pmod-tt.md",
        "docs/hardware/gpio-connectivity-analysis.md",
        "docs/hardware/deployment-checklist.md",
        "docs/hardware/butterstick.md",
        "docs/hardware/ulx3s.md",
    ]),
    "infra": ("fpgas.online-infra", "origin/main", [
        "README.md",
        "CLAUDE.md",
        "TECHDEBT.md",
        "notes.txt",
        "ansible/inventory/hosts",
        "ansible/inventory/host_vars/fpgas.online.yml",
        "ansible/inventory/host_vars/ps1.fpgas.online.yml",
        "ansible/inventory/group_vars/all/srv.yml",
        "ansible/roles/onpi/tasks/main.yml",
        "ansible/roles/onpi/tasks/apt.yml",
        "ansible/roles/onpi/tasks/tt.yml",
        "ansible/roles/nspawn-pi/tasks/start.yml",
        "ansible/roles/fixpi/tasks/netboot.yml",
        "ansible/roles/fixpi/tasks/tweeks.yml",
        "ansible/roles/fixpi/templates/boot/cmdline.txt.j2",
        "ansible/roles/pxe/templates/dnsmasq-base.conf.j2",
        "ansible/roles/nfs/templates/exports.j2",
        "docs/hardware/2026-08-28-orange-pi-h3-boards.md",
        "docs/rebuilds/2026-08-25-tweed-rebuild.md",
        "docs/superpowers/runbooks/2026-08-23-tweed-web-deploy.md",
        "docs/superpowers/runbooks/2026-08-28-orange-pi-netboot.md",
        "docs/superpowers/runbooks/2026-08-31-eeprom-write-protect.md",
        "docs/superpowers/specs/2026-08-14-vlan-per-port-network-design.md",
        "docs/superpowers/specs/2026-08-14-vlan-per-port-prototype-runbook.md",
        "docs/superpowers/specs/2026-08-22-tinytapeout-fpgas-online-design.md",
        "docs/superpowers/specs/2026-08-28-orange-pi-netboot-design.md",
    ]),
    "site": ("fpgas.online-site", "origin/main", ["README.md", "pib/urls.py", "pibfpgas/src/pibfpgas/urls.py", "pistat/src/pistat/urls.py", "pibup/src/pibup/urls.py", "ttsite/src/ttsite/urls.py"]),
    "tt": ("fpgas.online-tt", "origin/main", ["README.md"]),
    "tt-demos": ("tinytapeout-fpga-demos", "origin/main", ["README.md"]),
    # The fork's default branch is fpgas-online; main mirrors upstream.
    "commander": ("tt-commander-app", "origin/fpgas-online", ["README.fpgas-online.md"]),
    "gw": ("fpgas.online-gw", "origin/main", ["README.md"]),
    "setup-pi": ("fpgas.online-setup-pi", "origin/main", ["README.md", "nfpm.yaml"]),
    "cam": ("fpgas.online-cam", "origin/main", ["README.md"]),
    "poe": ("fpgas.online-poe", "origin/main", ["README.md"]),
}


def export(key: str) -> None:
    repo, ref, paths = REPOS[key]
    repo_dir = PARENT / repo
    subprocess.run(["git", "-C", str(repo_dir), "fetch", "-q", "origin"], check=True)
    for path in paths:
        out = DOCS / "tmp" / "src" / key / path
        out.parent.mkdir(parents=True, exist_ok=True)
        blob = subprocess.run(
            ["git", "-C", str(repo_dir), "show", f"{ref}:{path}"],
            check=True, capture_output=True,
        ).stdout
        out.write_bytes(blob)
        print(out.relative_to(DOCS))


def main(argv: list[str]) -> int:
    keys = argv or list(REPOS)
    for key in keys:
        export(key)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
