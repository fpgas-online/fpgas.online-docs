---
type: reference
owner: documentation maintainers
reader: someone running the pin-id scanner who wants to limit or change what it scans
review: 2026-11-10
---

# Pin-id scanner options

**The options of the pin-id host scanner `host/identify_pmod_pins.py`**. The options are run from `designs/pmod-pin-id` on the Raspberry Pi. How to run a whole scan is on [How to scan a board's wiring with the pin-id design](scan.md).

The Option column is the flag, the Command column is a full command that uses it, and What it does is the effect.

| Option | Command | What it does |
|---|---|---|
| none | `uv run python host/identify_pmod_pins.py` | Scans all PMOD HAT GPIOs (the default) |
| `--gpios` | `uv run python host/identify_pmod_pins.py --gpios 8 19 21` | Scans the listed GPIOs |
| `--hat-port` | `uv run python host/identify_pmod_pins.py --hat-port JA` | Scans a single HAT port |
| `--no-unload` | `uv run python host/identify_pmod_pins.py --no-unload` | Skips kernel module unloading, for when it is already done |
