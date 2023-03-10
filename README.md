# archlinux

## Installation (2023)
1. Boot from ISO
2. Do `archinstall`, enter user credential and save cred file to `/root`
3. `curl -O https://cyluss.github.io/archlinux/archinstall.sh | bash`
4. Review install config, and proceed
5. No chroot, `reboot`
6. Log in as user account
7. Install Chrome
    1. `mkdir aur; cd aur`
    2. `git clone https://aur.archlinux.org/google-chrome.git`
    3. `makepkg -si`
8. ssh-keygen: `ssh-keygen -t ed25519 -a 100`
