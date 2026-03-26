# archlinux

## VM (VirtualBox)

### Provisioning
1. Boot from ISO
2. `archinstall --config-url https://cyluss.github.io/archlinux/user_configuration.json`
3. Add user and disk config, and proceed
4. No chroot, `reboot`
5. Log in as user account

### AUR packages
1. `mkdir aur; cd aur`
2. Install Chrome
    1. `git clone https://aur.archlinux.org/google-chrome.git  && pushd "$_"`
    2. `makepkg --syncdeps --install; popd`
2. Install Spoqa Han Sans
    1. `git clone https://aur.archlinux.org/spoqa-han-sans.git && pushd "$_"`
    2. `makepkg --syncdeps --install; popd`
3. ssh-keygen: `ssh-keygen -t ed25519 -a 100`

## MBP 2015 (bare metal)

### Provisioning
1. Boot from ISO (use [Ventoy](https://www.ventoy.net) or `dd`)
2. Connect TB-to-Ethernet adapter for stable network, or direct cable to macOS:
   ```bash
   ip addr add 192.168.2.2/24 dev enp0s20f0
   curl -O http://192.168.2.1:8000/fix_wifi.py
   ```
3. `archinstall --config-url https://cyluss.github.io/archlinux/mbp_2015/user_configuration.json`
4. No chroot, `reboot`
5. Fix WiFi:
   ```bash
   curl -O https://cyluss.github.io/archlinux/mbp_2015/fix_wifi.py
   sudo python fix_wifi.py
   ```

### Docs
- [Broadcom WiFi fix](mbp_2015/broadcom_wifi.md) -- BCM43602 stabilization, TB Ethernet debugging
