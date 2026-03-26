#!/bin/bash
# Build a self-contained USB directory
# Copy the output to a Ventoy USB alongside the Arch ISO
# Usage: ./usb/build.sh
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(dirname "$DIR")"
OUT="$DIR/out"

rm -rf "$OUT"
mkdir -p "$OUT/dotfiles/.config/sway" "$OUT/dotfiles/.config/foot" "$OUT/aur"

echo "=== copying configs ==="
cp "$REPO/user_configuration.json" "$OUT/"
cp "$REPO/mbp_2015/user_configuration.json" "$OUT/mbp_2015_user_configuration.json"
cp "$REPO/dotfiles/.config/sway/config" "$OUT/dotfiles/.config/sway/"
cp "$REPO/dotfiles/.config/sway/help-bar.py" "$OUT/dotfiles/.config/sway/"
cp "$REPO/dotfiles/.config/sway/status.py" "$OUT/dotfiles/.config/sway/"
cp "$REPO/dotfiles/.config/foot/foot.ini" "$OUT/dotfiles/.config/foot/"
cp "$REPO/mbp_2015/fix_wifi.py" "$OUT/"

echo "=== downloading AUR packages ==="
cd "$OUT/aur"
for pkg in google-chrome spoqa-han-sans; do
    git clone "https://aur.archlinux.org/${pkg}.git" 2>/dev/null || true
done

echo "=== creating setup script ==="
cat > "$OUT/setup.sh" << 'SETUP'
#!/bin/bash
# Self-contained setup from USB
# Usage: mount USB, then: bash /mnt/archlinux/setup.sh
set -euo pipefail

USB="$(cd "$(dirname "$0")" && pwd)"

echo "=== dotfiles ==="
mkdir -p ~/.config/sway ~/.config/foot
cp "$USB/dotfiles/.config/sway/config"      ~/.config/sway/
cp "$USB/dotfiles/.config/sway/help-bar.py" ~/.config/sway/
cp "$USB/dotfiles/.config/sway/status.py"   ~/.config/sway/
cp "$USB/dotfiles/.config/foot/foot.ini"    ~/.config/foot/
chmod +x ~/.config/sway/help-bar.py ~/.config/sway/status.py

echo "=== AUR packages ==="
for pkg in google-chrome spoqa-han-sans; do
    if ! pacman -Q "$pkg" &>/dev/null; then
        cp -r "$USB/aur/$pkg" /tmp/
        pushd "/tmp/$pkg"
        makepkg --syncdeps --install --noconfirm
        popd
    fi
done

echo "=== SSH key ==="
if [ ! -f ~/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519 -N ""
fi

echo "=== locale ==="
sudo localectl set-locale LANG=en_US.UTF-8

echo "=== TTY light theme ==="
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="loglevel=3 quiet"/GRUB_CMDLINE_LINUX_DEFAULT="loglevel=3 quiet vt.default_red=255,204,0,128,0,128,0,0 vt.default_grn=255,0,128,128,0,0,128,0 vt.default_blu=255,0,0,0,204,128,128,0"/' /etc/default/grub
sudo grub-mkconfig -o /boot/grub/grub.cfg

echo "=== done ==="
echo "Run 'sway' to start"
SETUP

cat > "$OUT/install.sh" << 'INSTALL'
#!/bin/bash
# One-command install from USB
# Usage from live ISO: bash /mnt/archlinux/install.sh [mbp]
set -euo pipefail
USB="$(cd "$(dirname "$0")" && pwd)"

if [ "${1:-}" = "mbp" ]; then
    CONFIG="$USB/mbp_2015_user_configuration.json"
else
    CONFIG="$USB/user_configuration.json"
fi

echo "Using config: $CONFIG"
archinstall --config "$CONFIG"
INSTALL

chmod +x "$OUT/setup.sh" "$OUT/install.sh"

echo ""
echo "=== Done ==="
echo "Copy $OUT/* to your Ventoy USB under /archlinux/"
echo ""
echo "USB layout:"
find "$OUT" -type f | sort | sed "s|$OUT|/archlinux|"
echo ""
echo "From live ISO:"
echo "  mount /dev/sda1 /mnt"
echo "  bash /mnt/archlinux/install.sh       # VM"
echo "  bash /mnt/archlinux/install.sh mbp   # MBP 2015"
echo ""
echo "After reboot:"
echo "  mount /dev/sda1 /mnt"
echo "  bash /mnt/archlinux/setup.sh"
echo "  sway"
