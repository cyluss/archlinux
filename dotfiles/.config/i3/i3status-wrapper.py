#!/usr/bin/env python3
import sys, json

for line in sys.stdin:
    if line.startswith(","):
        data = json.loads(line[1:])
        data.append({"full_text": " "})
        print("," + json.dumps(data), flush=True)
    elif line.strip().startswith("[{"):
        data = json.loads(line)
        data.append({"full_text": " "})
        print(json.dumps(data), flush=True)
    else:
        print(line, end="", flush=True)
