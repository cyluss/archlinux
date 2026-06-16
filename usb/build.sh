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
cp "$REPO/setup.py" "$OUT/"

echo "=== downloading AUR packages ==="
cd "$OUT/aur"
for pkg in google-chrome spoqa-han-sans; do
    git clone "https://aur.archlinux.org/${pkg}.git" 2>/dev/null || true
done

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

chmod +x "$OUT/setup.py" "$OUT/install.sh"

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
echo "  python3 /mnt/archlinux/setup.py        # VM"
echo "  python3 /mnt/archlinux/setup.py mbp    # MBP 2015"
echo "  sway"
