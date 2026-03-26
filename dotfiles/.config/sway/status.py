#!/usr/bin/env python3
import json, time, sys, subprocess, os

def get_status():
    items = []

    # Network
    try:
        ip = subprocess.check_output(["ip", "-4", "-o", "addr", "show", "scope", "global"], text=True).strip()
        if ip:
            iface, addr = ip.split()[1], ip.split()[3].split("/")[0]
            items.append({"full_text": f"{iface}: {addr}", "color": "#0055aa"})
        else:
            items.append({"full_text": "no network", "color": "#990000"})
    except:
        items.append({"full_text": "no network", "color": "#990000"})

    # Disk
    st = os.statvfs("/")
    free_gb = (st.f_bavail * st.f_frsize) / (1024**3)
    items.append({"full_text": f"disk: {free_gb:.1f}G"})

    # Load
    load = os.getloadavg()[0]
    items.append({"full_text": f"load: {load:.2f}"})

    # Memory
    with open("/proc/meminfo") as f:
        mem = {}
        for line in f:
            k, v = line.split(":")[0], int(line.split(":")[1].strip().split()[0])
            mem[k] = v
    used = (mem["MemTotal"] - mem["MemAvailable"]) / 1024
    total = mem["MemTotal"] / 1024
    items.append({"full_text": f"mem: {used:.0f}/{total:.0f}M"})

    # Time
    items.append({"full_text": time.strftime("%Y-%m-%d %H:%M:%S")})

    # Right margin
    items.append({"full_text": " "})

    return items

print(json.dumps({"version": 1}))
print("[")
print("[]")
sys.stdout.flush()

while True:
    print("," + json.dumps(get_status()))
    sys.stdout.flush()
    time.sleep(5)
