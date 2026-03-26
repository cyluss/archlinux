#!/usr/bin/env python3
"""Broadcom BCM43602 WiFi fix for MacBook Pro 2015 on Arch Linux.

Usage (from live ISO or installed system):
    curl -O https://cyluss.github.io/archlinux/mbp_2015/fix_wifi.py
    python fix_wifi.py          # apply all fixes
    python fix_wifi.py --debug  # start debug monitoring (requires TB ethernet + SSH)
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd, check=True):
    print(f"  -> {cmd}")
    return subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)


def write_file(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    print(f"  wrote {path}")


def remove_conflicting_drivers():
    print("\n[1/7] Removing conflicting drivers...")
    run("pacman -R --noconfirm broadcom-wl broadcom-wl-dkms 2>/dev/null || true", check=False)
    run("pacman -S --noconfirm --needed linux-firmware")


def blacklist_modules():
    print("\n[2/7] Blacklisting conflicting modules...")
    write_file("/etc/modprobe.d/broadcom-blacklist.conf", """\
blacklist bcma
blacklist b43
blacklist b43legacy
blacklist ssb
blacklist brcmsmac
blacklist ndiswrapper
""")


def configure_brcmfmac():
    print("\n[3/7] Configuring brcmfmac module parameters...")
    write_file("/etc/modprobe.d/brcmfmac.conf",
               "options brcmfmac feature_disable=0x82000 roamoff=1\n")


def disable_wifi_powersave():
    print("\n[4/7] Disabling NetworkManager WiFi power saving...")
    write_file("/etc/NetworkManager/conf.d/wifi-powersave-off.conf", """\
[connection]
wifi.powersave = 2
""")


def disable_mac_randomization():
    print("\n[5/7] Disabling MAC address randomization...")
    write_file("/etc/NetworkManager/conf.d/disable-random-mac.conf", """\
[device]
wifi.scan-rand-mac-address=no
""")


def create_powersave_service():
    print("\n[6/7] Creating iw power_save off service...")
    # detect wireless interface name
    result = run("iw dev 2>/dev/null | awk '/Interface/{print $2}' | head -1", check=False)
    iface = result.stdout.strip() or "wlp2s0"
    print(f"  detected interface: {iface}")

    write_file("/etc/systemd/system/wifi-powersave-off.service", f"""\
[Unit]
Description=Disable WiFi Power Management
After=NetworkManager.service

[Service]
Type=oneshot
ExecStart=/usr/bin/iw dev {iface} set power_save off

[Install]
WantedBy=multi-user.target
""")
    run("systemctl daemon-reload")
    run("systemctl enable wifi-powersave-off.service")


def create_suspend_services():
    print("\n[7/7] Creating suspend/resume WiFi services...")
    write_file("/etc/systemd/system/wifi-before-sleep.service", """\
[Unit]
Description=Unload brcmfmac before sleep
Before=suspend.target

[Service]
Type=oneshot
ExecStart=/usr/bin/rmmod brcmfmac

[Install]
WantedBy=suspend.target
""")
    write_file("/etc/systemd/system/wifi-after-sleep.service", """\
[Unit]
Description=Reload brcmfmac after sleep
After=suspend.target

[Service]
Type=oneshot
ExecStart=/usr/bin/modprobe brcmfmac

[Install]
WantedBy=suspend.target
""")
    run("systemctl daemon-reload")
    run("systemctl enable wifi-before-sleep.service wifi-after-sleep.service")


def rebuild_and_prompt():
    print("\nRebuilding initramfs...")
    run("mkinitcpio -P")
    print("\n--- All fixes applied. Reboot to take effect. ---")
    print("  sudo reboot")


def apply_all():
    if subprocess.os.geteuid() != 0:
        sys.exit("Error: run as root (sudo python fix_wifi.py)")

    remove_conflicting_drivers()
    blacklist_modules()
    configure_brcmfmac()
    disable_wifi_powersave()
    disable_mac_randomization()
    create_powersave_service()
    create_suspend_services()
    rebuild_and_prompt()


def debug():
    """Start WiFi debug monitoring. Use over SSH via TB Ethernet."""
    result = run("iw dev 2>/dev/null | awk '/Interface/{print $2}' | head -1", check=False)
    iface = result.stdout.strip() or "wlp2s0"

    print(f"WiFi interface: {iface}")
    print("TB Ethernet adapter (tg3 driver):")
    run("lspci | grep -i 'BCM577\\|tg3'", check=False)
    print()

    print("=== Current WiFi status ===")
    run(f"iw dev {iface} link", check=False)
    run(f"iw dev {iface} get power_save", check=False)
    print()

    print("=== Loaded modules ===")
    run("lsmod | grep -E 'brcm|wl|b43|bcma|tg3'", check=False)
    print()

    print("=== brcmfmac module parameters ===")
    run("systool -vm brcmfmac 2>/dev/null | grep -A1 'Parameters:'", check=False)
    for param in ["feature_disable", "roamoff"]:
        p = Path(f"/sys/module/brcmfmac/parameters/{param}")
        if p.exists():
            print(f"  {param} = {p.read_text().strip()}")
    print()

    print("=== Recent brcmfmac messages ===")
    run("dmesg | grep -i brcmfmac | tail -20", check=False)
    print()

    print("=== Firmware load status ===")
    run("dmesg | grep -i 'firmware\\|brcm.*pcie' | tail -10", check=False)
    print()

    print("--- Live monitoring (Ctrl+C to stop) ---")
    print(f"  journalctl -f -u NetworkManager & dmesg -w | grep brcmfmac")
    try:
        subprocess.Popen(["bash", "-c", "journalctl -f -u NetworkManager 2>/dev/null &"
                          f" dmesg -w 2>/dev/null | grep --line-buffered -i brcmfmac"])
        subprocess.run(["bash", "-c", f"iw event -f 2>/dev/null"])
    except KeyboardInterrupt:
        print("\nStopped.")


def main():
    parser = argparse.ArgumentParser(description="BCM43602 WiFi fix for MBP 2015")
    parser.add_argument("--debug", action="store_true",
                        help="Start WiFi debug monitoring (use over SSH via TB Ethernet)")
    args = parser.parse_args()

    if args.debug:
        debug()
    else:
        apply_all()


if __name__ == "__main__":
    main()
