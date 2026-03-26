#!/usr/bin/env python3
import json, time, sys

print(json.dumps({"version": 1}))
print("[")
print("[]")
sys.stdout.flush()

while True:
    print("," + json.dumps([{
        "full_text": "term:Mod+Enter  run:Mod+d  split:Mod+h/v  full:Mod+f  kill:Mod+Shift+q  reload:Mod+Shift+r  exit:Mod+Shift+e  ",
        "color": "#888888"
    }]))
    sys.stdout.flush()
    time.sleep(60)
