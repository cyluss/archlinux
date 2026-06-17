# archlinux

## Target Hardware (SKUs)

| | VM | MBP 2015 (bare metal) |
|---|---|---|
| **config** | [user_configuration.json](user_configuration.json) | [mbp_2015/user_configuration.json](mbp_2015/user_configuration.json) |
| **display** | sway (Wayland) | sway (Wayland) |
| **network** | iso | nm (NetworkManager) |
| **kernels** | linux | linux, linux-lts |
| **extra packages** | -- | iw, linux-firmware, wireless_tools |
| **post-install** | -- | [fix_wifi.py](mbp_2015/fix_wifi.py), cpu-performance.service |
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
6. `python3 /mnt/archlinux/setup.py` (or `setup.py mbp`)
7. `sway`

### Reprovision
Boot USB, repeat from step 2.

## Online Provisioning (alternative)

### VM
```bash
archinstall --config-url https://cyluss.github.io/archlinux/user_configuration.json
# reboot, then:
curl -sL cyluss.github.io/archlinux/setup.py | python3
sway
```

### MBP 2015
```bash
archinstall --config-url https://cyluss.github.io/archlinux/mbp_2015/user_configuration.json
# reboot, then:
curl -sL cyluss.github.io/archlinux/setup.py | python3 - mbp
sway
```

## Backup / Restore (restic → S3)

Daily automated backup via systemd timer. Encrypted, deduplicated, incremental.

```bash
# Manual backup
~/.config/restic/backup.sh

# List snapshots
restic snapshots  # (with env vars from backup.sh)

# Restore from archiso (USB with secrets/ and rootkey.csv)
mount /dev/sdb1 /mnt/usb
python3 /mnt/usb/archlinux/restore.py /mnt/home/kang

# Restore: list snapshots only
python3 restore.py --list

# Restore: specific snapshot
python3 restore.py --snapshot abc123 /mnt/home/kang
```

Secrets on USB: `secrets/restic-password-<hostname>`, `rootkey.csv`

## TODO
- [ ] Convert ext4 → btrfs for snapshot/revert (boot archiso, `btrfs-convert /dev/sda3`, update fstab + grub)

## Docs
- [Broadcom WiFi fix](mbp_2015/broadcom_wifi.md) -- BCM43602 stabilization, TB Ethernet debugging
