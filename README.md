# archlinux

## Target Hardware (SKUs)

| | VM | MBP 2015 (bare metal) | kang-pc-arch (bare metal) |
|---|---|---|---|
| **config** | [user_configuration.json](user_configuration.json) | [mbp_2015/user_configuration.json](mbp_2015/user_configuration.json) | [user_configuration.json](user_configuration.json) |
| **display** | sway (Wayland) | sway (Wayland) | sway (Wayland) |
| **network** | iso | nm (NetworkManager) | nm + iwd (NetworkManager) |
| **kernels** | linux | linux, linux-lts | linux |
| **extra packages** | -- | iw, linux-firmware, wireless_tools | os-prober, networkmanager |
| **post-install** | -- | [fix_wifi.py](mbp_2015/fix_wifi.py), cpu-performance.service | see WiFi quirks below |
| **hostname** | archlinux | mbp2015 | kang-pc-arch |
| **dd portable** | within same VM type | within same MBP | -- |

### kang-pc-arch Hardware

| 항목 | 값 |
|---|---|
| CPU | AMD Ryzen 5 5600 (6코어 12스레드) |
| RAM | 32GB DDR4 |
| GPU | AMD Radeon RX 6600 XT (VRAM 8GB) |
| Disk | TOSHIBA SSD 119.2G (`/dev/sdd`) — Arch 전용 |
| Other disks | Samsung SSD 870 EVO 500G (Windows 11, `sdc`), WD HDD 1TB (data, `sda`), Samsung SSD 850 EVO 250G (data, `sdb`) |
| Display | Dell P2319H (1920×1080, DP-3), scale 1.0 |
| WiFi | Intel WiFi (wlan0), iwd backend |
| Ethernet | enp4s0 (static 192.168.0.17) |

### kang-pc-arch WiFi Quirks

WiFi IP가 재부팅마다 바뀌는 문제가 있었음. 원인과 해결:

1. **MAC 주소 랜덤화** — NetworkManager가 기본으로 MAC을 랜덤화해 DHCP에서 매번 다른 IP 부여.
   ```bash
   # /etc/NetworkManager/conf.d/stable-mac.conf
   [device]
   wifi.scan-rand-mac-address=no
   [connection]
   wifi.cloned-mac-address=permanent
   ```

2. **wpa_supplicant / iwd 충돌** — 두 WiFi 백엔드가 동시에 실행되어 연결이 불안정.
   ```bash
   # iwd를 백엔드로 고정, wpa_supplicant 비활성화
   # /etc/NetworkManager/conf.d/wifi-backend.conf
   [device]
   wifi.backend=iwd

   sudo systemctl mask wpa_supplicant
   sudo systemctl disable --now systemd-networkd systemd-resolved
   ```

3. **고정 IP 설정** (이더넷 권장, WiFi는 불안정 가능성 있음):
   ```bash
   nmcli con mod "SSID" wifi.cloned-mac-address permanent \
     ipv4.method manual ipv4.addresses 192.168.0.X/24 \
     ipv4.gateway 192.168.0.1 ipv4.dns "8.8.8.8,1.1.1.1"
   ```

> 이더넷(`enp4s0`, static 192.168.0.17)이 더 안정적. SSH 접속은 이더넷 권장.

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
