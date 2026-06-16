#!/usr/bin/env python3
import os, signal, sys, time

PATH = "/sys/class/backlight/intel_backlight/brightness"
PIDFILE = "/tmp/brightness.pid"
MAX_STEPS = 20
MAX_DURATION = 0.15

try:
    old_pid = int(open(PIDFILE).read())
    os.kill(old_pid, signal.SIGTERM)
except (FileNotFoundError, ValueError, ProcessLookupError):
    pass
open(PIDFILE, "w").write(str(os.getpid()))

cur = int(open(PATH).read())
if sys.argv[1] == "up":
    target = max(cur + 1, cur * 11 // 10)
else:
    target = max(1, cur * 10 // 11)

diff = target - cur
steps = min(MAX_STEPS, max(1, abs(diff)))
duration = MAX_DURATION * steps / MAX_STEPS
for i in range(1, steps + 1):
    v = cur + diff * i // steps
    open(PATH, "w").write(str(v))
    time.sleep(duration / steps)
