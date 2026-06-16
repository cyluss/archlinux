#!/usr/bin/env python3
import subprocess, sys

STEP_RATIO = 1.1

out = subprocess.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
                     capture_output=True, text=True).stdout
cur = float(out.split()[1])

if sys.argv[1] == "up":
    target = min(1.0, max(cur + 0.01, cur * STEP_RATIO))
else:
    target = max(0.0, min(cur - 0.01, cur / STEP_RATIO))

subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{target:.3f}"])
