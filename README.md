# archlinux

## Installation (2023)
1. Boot from ISO
2. `archinstall --config https://cyluss.github.io/archlinux/user_configuration.json`
3. Add user and disk config, and proceed
4. No chroot, `reboot`
5. Log in as user account

# Install AUR packages
1. `mkdir aur; cd aur`
2. Install Chrome
    1. `git clone https://aur.archlinux.org/google-chrome.git  && pushd "$_"`
    2. `makepkg --syncdeps --install; popd`
2. Install Spoqa Han Sans
    1. `git clone https://aur.archlinux.org/spoqa-han-sans.git && pushd "$_"`
    2. `makepkg --syncdeps --install; popd`
3. ssh-keygen: `ssh-keygen -t ed25519 -a 100`
