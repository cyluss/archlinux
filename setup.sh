#!/bin/bash
# Post-install setup: dotfiles + AUR packages
# Usage: curl -sL https://cyluss.github.io/archlinux/setup.sh | bash
set -euo pipefail

BASE_URL="https://raw.githubusercontent.com/cyluss/archlinux/master"

echo "=== dotfiles ==="
mkdir -p ~/.config/sway ~/.config/foot
curl -sL "$BASE_URL/dotfiles/.config/sway/config"              -o ~/.config/sway/config
curl -sL "$BASE_URL/dotfiles/.config/sway/help-bar.py"         -o ~/.config/sway/help-bar.py
curl -sL "$BASE_URL/dotfiles/.config/sway/i3status-wrapper.py" -o ~/.config/sway/i3status-wrapper.py
curl -sL "$BASE_URL/dotfiles/.config/foot/foot.ini"            -o ~/.config/foot/foot.ini
chmod +x ~/.config/sway/help-bar.py ~/.config/sway/i3status-wrapper.py

echo "=== AUR packages ==="
mkdir -p ~/aur && cd ~/aur
for pkg in google-chrome spoqa-han-sans; do
    if ! pacman -Q "$pkg" &>/dev/null; then
        git clone "https://aur.archlinux.org/${pkg}.git" 2>/dev/null || true
        pushd "$pkg"
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

echo "=== done ==="
echo "Run 'sway' to start"
