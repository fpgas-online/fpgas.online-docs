"""Render out/*.svg to PNG with headless Chromium (the same engine family the artifact is viewed in)."""
import pathlib
import subprocess
import sys

out = pathlib.Path("out").resolve()
for name in sys.argv[1:] or ["pi5", "blade"]:
    png = out / f"{name}.png"
    subprocess.run(["chromium", "--headless", "--no-sandbox", "--hide-scrollbars", "--force-device-scale-factor=2",
                    f"--screenshot={png}", "--window-size=1600,900", f"file://{out}/{name}.svg"],
                   check=True, capture_output=True)
    print(png, png.stat().st_size)
