#!/bin/bash
# MBP 2015 SKU-specific setup
set -euo pipefail

echo "=== BCM43602 WiFi fix ==="
curl -sL https://raw.githubusercontent.com/cyluss/archlinux/master/mbp_2015/fix_wifi.py -o /tmp/fix_wifi.py
sudo python /tmp/fix_wifi.py

echo "=== CPU base clock fix (no battery) ==="
sudo tee /etc/systemd/system/cpu-performance.service > /dev/null << 'SVC'
[Unit]
Description=Fix CPU clock to base frequency (no battery)
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor && echo 2700000 | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_min_freq && echo 1 | tee /sys/devices/system/cpu/intel_pstate/no_turbo'

[Install]
WantedBy=multi-user.target
SVC
sudo systemctl daemon-reload
sudo systemctl enable cpu-performance.service
