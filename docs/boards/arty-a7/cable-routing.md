# Arty A7: PMOD cable routing, HAT to Arty

**You want to know which Pmod HAT pin reaches which Arty PMOD pin on each host, as measured.**

## PMOD Cable Routing: HAT ↔ Arty

Ribbon cables connect straight through: **HAT JA → Arty JA**, **HAT JB → Arty
JB**, **HAT JC → Arty JC**. Arty JD is not connected (the HAT has only 3 ports).

Verified using the [`pmod-pin-id` design](../pin-id.md), which transmits each FPGA
pin's ball name as 1200-baud UART on every PMOD pin. Two independent scans (PMOD
names and FPGA pin names) cross-validated.

:::{note}
These scans are from the 2026-03-17 survey and name their hosts by the flat
`piNN` names used before the 2026-08-23 renumbering, and they have not been
re-probed since. Which site they were run from is not settled — see
[the todo below](#which-site-were-these-hosts-at). If these are Welland hosts,
the addresses quoted below no longer resolve and the current name of a host has
to be derived from its switch port using the
[Arty A7-35T host table](../../sites/welland.md#arty-a7-35t); if they are PS1
hosts, pi3, pi5 and pi9 are still at exactly these addresses in the
[Arty A7 hosts table](../../sites/ps1.md#arty-a7-hosts). The routing itself is a
property of the cables and the board, not of the host, so it is recorded here
rather than on a site page.
:::

### Pi9 (21 of 24 unique GPIOs scanned)

Scanned 2026-03-17.

This is the one host that produced a full scan, and it is also the host whose
site is in question — see [Which site were these hosts at?](#which-site-were-these-hosts-at)
before using the name `pi9` to find the board.

**HAT JA → Arty JA**

| HAT Pin | RPi GPIO | Scanned FPGA Pin | Expected (Arty JA) | Match |
| ------- | -------- | ---------------- | ------------------ | ----- |
| 1       | GPIO8    | G13              | G13                | yes   |
| 2       | GPIO10   | E16              | B11 (but shared\*) | (\*)  |
| 3       | GPIO9    | D15              | A11 (but shared\*) | (\*)  |
| 4       | GPIO11   | C15              | D12 (but shared\*) | (\*)  |
| 7       | GPIO19   | D13              | D13                | yes   |
| 8       | GPIO21   | B18              | B18                | yes   |
| 9       | GPIO20   | A18              | A18                | yes   |
| 10      | GPIO18   | K16              | K16                | yes   |

(\*) Pins 2-4 share GPIOs with JB pins 2-4. The scan reads Arty JB's pins (E16,
D15, C15) because both cables drive the same GPIO lines. Arty JA pins 2-4 (B11,
A11, D12) cannot be independently verified.

**HAT JB → Arty JB** (all 8 pins verified)

| HAT Pin | RPi GPIO | Scanned FPGA Pin | Expected (Arty JB) | Match |
| ------- | -------- | ---------------- | ------------------ | ----- |
| 1       | GPIO7    | E15              | E15                | yes   |
| 2       | GPIO10   | E16              | E16                | yes   |
| 3       | GPIO9    | D15              | D15                | yes   |
| 4       | GPIO11   | C15              | C15                | yes   |
| 7       | GPIO26   | J17              | J17                | yes   |
| 8       | GPIO13   | J18              | J18                | yes   |
| 9       | GPIO3    | K15              | K15                | yes   |
| 10      | GPIO2    | J15              | J15                | yes   |

**HAT JC → Arty JC** (pins 1↔2 swapped in cable)

| HAT Pin | RPi GPIO | Scanned FPGA Pin | Expected (Arty JC) | Match |
| ------- | -------- | ---------------- | ------------------ | ----- |
| 1       | GPIO16   | V12              | U12                | SWAP  |
| 2       | GPIO14   | U12              | V12                | SWAP  |
| 3       | GPIO15   | V10              | V10                | yes   |
| 4       | GPIO17   | V11              | V11                | yes   |
| 7       | GPIO4    | U14              | U14                | yes   |
| 8       | GPIO12   | V14              | V14                | yes   |
| 9       | GPIO5    | T13              | T13                | yes   |
| 10      | GPIO6    | U13              | U13                | yes   |

HAT JC pins 1 and 2 are swapped relative to Arty JC pins 1 and 2. This is a
physical cable crossover — GPIO16 connects to Arty JC pin 2 (V12) and GPIO14
connects to Arty JC pin 1 (U12). All other pins match 1:1.

### Pi3

Scanned 2026-03-17.

Pi3 detected fewer pins (12 of 21 unique GPIOs). All detected pins match pi9's
results exactly, confirming the same cable routing. HAT JC top-row and some
JA/JB pins showed no signal — likely loose cables or missing connections on this
host.

### Pi5 (offline)

Scanned 2026-03-17.

Pi5 (10.21.0.105) was unreachable during scanning — host appears powered off.

(unproven-lanes)=

### Unproven lanes

:::{todo}
Three lanes of the HAT ↔ Arty routing cannot be proven from the Pi, one whole
connector was never scanned, and one crossover is known (JC pins 1 and 2):

- Arty JA pins 2, 3 and 4 (B11, A11, D12) cannot be verified from the Pi,
  because HAT JA pins 2-4 and HAT JB pins 2-4 are the same three GPIO lines and
  the scan always reads the JB end (E16, D15, C15). Proving them needs a
  gateware-side scan, or JB unplugged while JA is scanned.
- Arty JD has no HAT port and was never scanned at all.
- HAT JC pins 1 and 2 are crossed on pi9. Whether that crossover is in that one
  cable or in every cable of the batch is unknown, because pi3 saw no signal on
  the JC top row and pi5 was off. Any design using JC1/JC2 must either account
  for the swap or be checked per host.

Re-run the [`pmod-pin-id`](../pin-id.md) scan on the current Arty hosts at both
sites, record the date, and say per host whether JC is crossed.
:::

(which-site-were-these-hosts-at)=

### Which site were these hosts at?

:::{todo}
The 2026-03-17 scans record only the flat names pi3, pi5 and pi9, and both sites
used flat `10.21.0.0/24` addressing at the time, so the addresses do not say
which site was scanned. The evidence:

- Welland's [Known faults](../../sites/welland.md#known-faults) carry a `pi9` Arty
  from this same survey whose FTDI is disconnected, so that board could not be
  programmed or tested on 2026-03-17. The `pmod-pin-id` scan needs the FTDI JTAG
  channel to load its bitstream, and pi9 produced a successful 21-of-24 scan
  that day. That argues **against** these being the Welland hosts.
- The [PS1 Arty table](../../sites/ps1.md#arty-a7-hosts) has pi3, pi5 and pi9 at
  exactly 10.21.0.103, 10.21.0.105 and 10.21.0.109. It records pi9 online with a
  working FTDI, but that column has no date or provenance.
- The [Welland Arty table](../../sites/welland.md#arty-a7-35t) has pi7, pi9, pi11,
  pi13 and pi26 — no pi3 and no pi5.
- `verify_hardware.py` in the test-designs repository defines **both** sets at
  identical addresses, and names pi11, not pi9, as the FTDI-disconnected Welland
  board, contradicting the Welland site notes:

  ```text
  "welland-pi3": {... "gateway": "welland", "target": "10.21.0.103", "board": "arty"},
  "welland-pi5": {... "gateway": "welland", "target": "10.21.0.105", "board": "arty"},
  "welland-pi9": {... "gateway": "welland", "target": "10.21.0.109", "board": "arty"},
  # welland-pi11: arty - FTDI disconnected, cannot program/test
  ...
  "ps1-pi3":     {... "gateway": "ps1",     "target": "10.21.0.103", "board": "arty"},
  "ps1-pi5":     {... "gateway": "ps1",     "target": "10.21.0.105", "board": "arty"},
  "ps1-pi9":     {... "gateway": "ps1",     "target": "10.21.0.109", "board": "arty"},
  ```

- The test-designs `plan.md` groups "Arty A7 (pi3/5/9)" with hosts that are
  otherwise Welland's, but names no site.
- The survey found 10.21.0.105 unreachable, which fits either site: PS1 records
  pi5 as online, but with no date or provenance for that column, and Welland has
  no host at .105 at all.

The balance favours PS1, but it is not settled. Ask the operator which site the
2026-03-17 `pmod-pin-id` run was made from, then either move the per-host detail
to that site page or say so here — and while doing it, settle whether pi9 or
pi11 is the Welland board with the disconnected FTDI.
:::
