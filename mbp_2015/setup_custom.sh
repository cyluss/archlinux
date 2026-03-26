#!/bin/bash
# MBP 2015 SKU-specific setup
set -euo pipefail

echo "=== BCM43602 WiFi fix ==="
curl -sL https://raw.githubusercontent.com/cyluss/archlinux/master/mbp_2015/fix_wifi.py -o /tmp/fix_wifi.py
sudo python /tmp/fix_wifi.py
