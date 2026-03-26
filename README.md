# archlinux

## Target Hardware (SKUs)

| | VM (VirtualBox) | MBP 2015 (bare metal) |
|---|---|---|
| **config** | [user_configuration.json](user_configuration.json) | [mbp_2015/user_configuration.json](mbp_2015/user_configuration.json) |
| **display** | sway (Wayland) | sway (Wayland) |
| **network** | iso | nm (NetworkManager) |
| **kernels** | linux | linux, linux-lts |
| **extra packages** | -- | iw, linux-firmware, openssh, wireless_tools |
| **post-install** | -- | [fix_wifi.py](mbp_2015/fix_wifi.py) |
| **hostname** | archlinux | mbp2015 |
| **dd portable** | within same VM type | within same MBP |

## VM (VirtualBox)

### Provisioning
1. Boot from ISO
2. `archinstall --config-url https://cyluss.github.io/archlinux/user_configuration.json`
3. Add user and disk config, and proceed
4. No chroot, `reboot`
5. Log in as user account
6. `curl -sL https://cyluss.github.io/archlinux/setup.sh | bash`
7. `sway`

### Backup / Restore
```bash
# Backup (from host)
dd if=/dev/sda bs=4M | zstd | aws s3 cp - s3://bucket/archlinux-vm.img.zst

# Restore
aws s3 cp s3://bucket/archlinux-vm.img.zst - | zstd -d | dd of=/dev/sda bs=4M
```

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

### Backup / Restore
```bash
# Backup (via TB Ethernet SSH)
dd if=/dev/sda bs=4M | zstd | aws s3 cp - s3://bucket/mbp2015-full.img.zst

# Restore (from Arch live USB)
aws s3 cp s3://bucket/mbp2015-full.img.zst - | zstd -d | dd of=/dev/sda bs=4M
```

### Docs
- [Broadcom WiFi fix](mbp_2015/broadcom_wifi.md) -- BCM43602 stabilization, TB Ethernet debugging
