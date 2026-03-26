# archlinux

## Target Hardware (SKUs)

| | VM | MBP 2015 (bare metal) |
|---|---|---|
| **config** | [user_configuration.json](user_configuration.json) | [mbp_2015/user_configuration.json](mbp_2015/user_configuration.json) |
| **display** | sway (Wayland) | sway (Wayland) |
| **network** | iso | nm (NetworkManager) |
| **kernels** | linux | linux, linux-lts |
| **extra packages** | -- | iw, linux-firmware, wireless_tools |
| **post-install** | -- | [fix_wifi.py](mbp_2015/fix_wifi.py) |
| **hostname** | archlinux | mbp2015 |
| **dd portable** | within same VM type | within same MBP |

## USB Provisioning (offline)

### Build USB (one-time, on Mac)
```bash
./usb/build.sh
# copy usb/out/* to Ventoy USB under /archlinux/
```

### Install
1. Boot from USB (Ventoy)
2. `mount /dev/sda1 /mnt && bash /mnt/archlinux/install.sh` (or `install.sh mbp`)
3. Disk + user config, proceed
4. No chroot, `reboot`, remove ISO
5. Login, mount USB: `mount /dev/sda1 /mnt`
6. `bash /mnt/archlinux/setup.sh`
7. `sway`

### Reprovision
Boot USB, repeat from step 2.

## Online Provisioning (alternative)

### VM
```bash
archinstall --config-url https://cyluss.github.io/archlinux/user_configuration.json
# reboot, then:
curl -sL cyluss.github.io/archlinux/setup.sh | bash
sway
```

### MBP 2015
```bash
archinstall --config-url https://cyluss.github.io/archlinux/mbp_2015/user_configuration.json
# reboot, then:
SKU_CUSTOM=mbp_2015/setup_custom.sh curl -sL cyluss.github.io/archlinux/setup.sh | bash
sway
```

## Backup / Restore
```bash
# Backup
dd if=/dev/sda bs=4M | zstd | aws s3 cp - s3://bucket/<sku>.img.zst

# Restore (from live USB)
aws s3 cp s3://bucket/<sku>.img.zst - | zstd -d | dd of=/dev/sda bs=4M
```

## Docs
- [Broadcom WiFi fix](mbp_2015/broadcom_wifi.md) -- BCM43602 stabilization, TB Ethernet debugging
