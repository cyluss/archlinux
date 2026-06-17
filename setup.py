#!/usr/bin/env python3
"""Post-install setup for Arch Linux provisioning.

Usage:
    Online:  curl -sL cyluss.github.io/archlinux/setup.py | python3 - [sku]
    USB:     python3 /mnt/archlinux/setup.py [sku]

SKUs:  (none) = VM,  mbp = MacBook Pro 2015
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE_URL = "https://raw.githubusercontent.com/cyluss/archlinux/master"

DOTFILES = [
    ".config/sway/config",
    ".config/sway/brightness.py",
    ".config/sway/volume.py",
    ".config/sway/help-bar.py",
    ".config/sway/status.py",
    ".config/foot/foot.ini",
]

AUR_PACKAGES = ["google-chrome", "spoqa-han-sans"]


def run(cmd, check=True):
    print(f"  -> {cmd}")
    return subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)


def write_file(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    print(f"  wrote {path}")


def detect_usb_dir():
    script_dir = Path(__file__).resolve().parent
    if (script_dir / "dotfiles").is_dir():
        return script_dir
    return None


def install_dotfiles(usb_dir):
    print("\n=== dotfiles ===")
    home = Path.home()
    for f in DOTFILES:
        dest = home / f
        dest.parent.mkdir(parents=True, exist_ok=True)
        if usb_dir:
            src = usb_dir / "dotfiles" / f
            shutil.copy2(src, dest)
            print(f"  copied {f}")
        else:
            run(f'curl -sL "{BASE_URL}/dotfiles/{f}" -o "{dest}"')
    for f in DOTFILES:
        dest = home / f
        if dest.suffix == ".py":
            dest.chmod(0o755)


def install_aur(usb_dir):
    print("\n=== AUR packages ===")
    for pkg in AUR_PACKAGES:
        r = run(f"pacman -Q {pkg}", check=False)
        if r.returncode == 0:
            print(f"  {pkg} already installed")
            continue
        if usb_dir:
            build_dir = Path(f"/tmp/{pkg}")
            if build_dir.exists():
                shutil.rmtree(build_dir)
            shutil.copytree(usb_dir / "aur" / pkg, build_dir)
            run(f"cd /tmp/{pkg} && makepkg --syncdeps --install --noconfirm")
        else:
            run(f"mkdir -p ~/aur && cd ~/aur && "
                f"git clone https://aur.archlinux.org/{pkg}.git 2>/dev/null || true && "
                f"cd {pkg} && makepkg --syncdeps --install --noconfirm")


def setup_ssh():
    print("\n=== SSH key ===")
    key = Path.home() / ".ssh" / "id_ed25519"
    if key.exists():
        print("  key already exists")
    else:
        run('ssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519 -N ""')


def setup_locale():
    print("\n=== locale ===")
    run("sudo localectl set-locale LANG=en_US.UTF-8")


def setup_zram():
    print("\n=== zram swap ===")
    run("sudo pacman -S --noconfirm zram-generator", check=False)
    write_file("/tmp/zram-generator.conf", """\
[zram0]
zram-size = ram / 2
compression-algorithm = zstd
""")
    run("sudo cp /tmp/zram-generator.conf /etc/systemd/zram-generator.conf")
    run("sudo systemctl daemon-reload")
    run("sudo systemctl start systemd-zram-setup@zram0.service", check=False)


def setup_memory():
    print("\n=== memory tuning ===")
    write_file("/tmp/99-memory.conf", """\
vm.swappiness=150
vm.vfs_cache_pressure=50
""")
    run("sudo cp /tmp/99-memory.conf /etc/sysctl.d/99-memory.conf")
    run("sudo sysctl --system")


def setup_services():
    print("\n=== disable unnecessary services ===")
    run("sudo systemctl disable NetworkManager-wait-online.service", check=False)
    run("sudo systemctl disable NetworkManager-dispatcher.service", check=False)


def setup_tty_theme():
    print("\n=== TTY light theme ===")
    run("sudo sed -i "
        "'s/GRUB_CMDLINE_LINUX_DEFAULT=\"loglevel=3 quiet\"/"
        "GRUB_CMDLINE_LINUX_DEFAULT=\"loglevel=3 quiet "
        "vt.default_red=255,204,0,128,0,128,0,0 "
        "vt.default_grn=255,0,128,128,0,0,128,0 "
        "vt.default_blu=255,0,0,0,204,128,128,0 "
        "vt.cur_default=1\"/' "
        "/etc/default/grub")
    run("sudo grub-mkconfig -o /boot/grub/grub.cfg")


# --- SKU: mbp ---

def sku_mbp(usb_dir):
    print("\n=== [mbp] BCM43602 WiFi fix ===")
    if usb_dir:
        run(f"sudo python3 {usb_dir}/fix_wifi.py")
    else:
        run(f"curl -sL {BASE_URL}/mbp_2015/fix_wifi.py -o /tmp/fix_wifi.py")
        run("sudo python3 /tmp/fix_wifi.py")

    print("\n=== [mbp] GRUB HiDPI font ===")
    run("sudo grub-mkfont -s 36 -o /boot/grub/fonts/DejaVuSansMono36.pf2 "
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf")
    run("sudo sed -i 's/GRUB_GFXMODE=auto/GRUB_GFXMODE=1024x768/' /etc/default/grub")
    run("echo 'GRUB_FONT=/boot/grub/fonts/DejaVuSansMono36.pf2' | sudo tee -a /etc/default/grub")
    run("sudo grub-mkconfig -o /boot/grub/grub.cfg")

    print("\n=== [mbp] CPU base clock fix ===")
    write_file("/tmp/cpu-performance.service", """\
[Unit]
Description=Fix CPU clock to base frequency (no battery)
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor && echo 2700000 | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_min_freq && echo 1 | tee /sys/devices/system/cpu/intel_pstate/no_turbo'

[Install]
WantedBy=multi-user.target
""")
    run("sudo cp /tmp/cpu-performance.service /etc/systemd/system/")
    run("sudo systemctl daemon-reload")
    run("sudo systemctl enable cpu-performance.service")


SKU_HANDLERS = {
    "mbp": sku_mbp,
}


def main():
    parser = argparse.ArgumentParser(description="Arch Linux post-install setup")
    parser.add_argument("sku", nargs="?", default=None,
                        choices=list(SKU_HANDLERS.keys()),
                        help="hardware SKU (omit for VM)")
    args = parser.parse_args()

    usb_dir = detect_usb_dir()
    mode = "USB" if usb_dir else "online"
    print(f"setup: mode={mode}, sku={args.sku or 'vm'}")

    install_dotfiles(usb_dir)
    install_aur(usb_dir)
    setup_ssh()
    setup_locale()
    setup_zram()
    setup_memory()
    setup_services()
    setup_tty_theme()

    if args.sku and args.sku in SKU_HANDLERS:
        SKU_HANDLERS[args.sku](usb_dir)

    print("\n=== done ===")
    print("Run 'sway' to start")


if __name__ == "__main__":
    main()
