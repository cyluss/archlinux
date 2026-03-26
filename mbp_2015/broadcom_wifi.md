# Broadcom WiFi - MacBook Pro 2015 (BCM43602)

MBP 2015 (11,4 / 11,5) uses the **Broadcom BCM43602 802.11ac** chip (PCI ID: `14e4:43ba`).
WiFi drops after ~1 minute are caused by power management, driver conflicts, and wpa_supplicant bugs.

## Quick Fix (script)

### Online (WiFi or internet available)

```bash
curl -O https://cyluss.github.io/archlinux/mbp_2015/fix_wifi.py
sudo python fix_wifi.py          # apply all fixes
sudo python fix_wifi.py --debug  # monitor WiFi over SSH via TB Ethernet
```

### Offline (direct cable, no internet)

Connect the MBP (Arch) and another Mac (macOS) with a direct Ethernet cable using TB-to-Ethernet adapters on both sides. No router or switch needed -- modern NICs auto-detect crossover.

On **macOS** (the server):
```bash
# Set static IP: System Preferences > Network > Thunderbolt Ethernet
#   IP: 192.168.2.1, Subnet: 255.255.255.0

# Serve the script
cd /path/to/archlinux/mbp_2015
python3 -m http.server 8000
```

On **Arch** (the MBP):
```bash
# Find the wired interface name
ip link

# Set static IP
ip addr add 192.168.2.2/24 dev enp0s20f0   # replace with your interface

# Pull and run
curl -O http://192.168.2.1:8000/fix_wifi.py
sudo python fix_wifi.py
```

## Diagnosis

```bash
lspci -vnn | grep -i net              # identify chip
lspci -k | grep -A3 Network           # check loaded driver
iw dev                                # list wireless interfaces
dmesg | grep -i brcmfmac              # check for errors
lsmod | grep -E "brcm|wl|b43|bcma"   # check loaded modules
```

## Fix: Step by Step

### 1. Use brcmfmac driver (NOT broadcom-wl)

Remove the proprietary driver if installed. It does not work reliably with BCM43602.

```bash
sudo pacman -R broadcom-wl broadcom-wl-dkms   # remove if installed
sudo pacman -S linux-firmware                   # provides brcmfmac firmware
```

### 2. Blacklist conflicting modules

Create `/etc/modprobe.d/broadcom-blacklist.conf`:

```
blacklist bcma
blacklist b43
blacklist b43legacy
blacklist ssb
blacklist brcmsmac
blacklist ndiswrapper
```

`bcma` is the most critical one -- it interferes with brcmfmac device initialization.

### 3. Configure brcmfmac module parameters

Create `/etc/modprobe.d/brcmfmac.conf`:

```
options brcmfmac feature_disable=0x82000 roamoff=1
```

- **`feature_disable=0x82000`** -- Disables SAE handshake offloading and SWSUP. Fixes a known incompatibility between brcmfmac and wpa_supplicant 2.11+ that causes authentication timeouts and disconnects.
- **`roamoff=1`** -- Disables internal roaming engine. Prevents the driver from constantly disconnecting/reconnecting when multiple APs share an SSID.

This can also be passed as a kernel parameter: `brcmfmac.feature_disable=0x82000 brcmfmac.roamoff=1`

### 4. Disable NetworkManager WiFi power saving

Create `/etc/NetworkManager/conf.d/wifi-powersave-off.conf`:

```ini
[connection]
wifi.powersave = 2
```

Values: `0`=default, `1`=ignore, **`2`=disable**, `3`=enable.

### 5. Disable MAC address randomization

Create `/etc/NetworkManager/conf.d/disable-random-mac.conf`:

```ini
[device]
wifi.scan-rand-mac-address=no
```

BCM43602 can produce errors when MAC randomization is enabled during scanning.

### 6. Disable power management via iw

Create `/etc/systemd/system/wifi-powersave-off.service`:

```ini
[Unit]
Description=Disable WiFi Power Management
After=NetworkManager.service

[Service]
Type=oneshot
ExecStart=/usr/bin/iw dev wlp2s0 set power_save off

[Install]
WantedBy=multi-user.target
```

> Replace `wlp2s0` with your actual interface name (check `ip link`).

```bash
sudo systemctl enable wifi-powersave-off.service
```

Verify:

```bash
iw dev wlp2s0 get power_save
```

### 7. Rebuild initramfs and reboot

```bash
sudo mkinitcpio -P
sudo reboot
```

## Fix: Suspend/Resume WiFi Drops

BCM43602 fails to enter/exit D3 power state during suspend, producing:
```
brcmfmac: brcmf_pcie_pm_enter_D3: Timeout on response for entering D3 substate
```

**Option A: Unload/reload brcmfmac around suspend**

Create `/etc/systemd/system/wifi-before-sleep.service`:

```ini
[Unit]
Description=Unload brcmfmac before sleep
Before=suspend.target

[Service]
Type=oneshot
ExecStart=/usr/bin/rmmod brcmfmac

[Install]
WantedBy=suspend.target
```

Create `/etc/systemd/system/wifi-after-sleep.service`:

```ini
[Unit]
Description=Reload brcmfmac after sleep
After=suspend.target

[Service]
Type=oneshot
ExecStart=/usr/bin/modprobe brcmfmac

[Install]
WantedBy=suspend.target
```

```bash
sudo systemctl enable wifi-before-sleep.service wifi-after-sleep.service
```

Or install the AUR package: `yay -S brcmfmac-suspend`

**Option B: Use s2idle instead of deep sleep**

Edit `/etc/systemd/sleep.conf`:

```ini
[Sleep]
SuspendState=freeze
MemorySleepMode=s2idle
```

Add kernel parameter: `mem_sleep_default=s2idle`

## Fix: wpa_supplicant Compatibility

If `feature_disable=0x82000` (step 3) does not resolve authentication failures, downgrade wpa_supplicant:

```bash
sudo pacman -U https://archive.archlinux.org/packages/w/wpa_supplicant/wpa_supplicant-2%3A2.10-8-x86_64.pkg.tar.zst
```

Pin it in `/etc/pacman.conf`:

```
IgnorePkg = wpa_supplicant
```

## Alternative: Try iwd backend

If wpa_supplicant remains problematic, switch NetworkManager to iwd:

```bash
sudo pacman -S iwd
sudo systemctl enable --now iwd
```

Create `/etc/NetworkManager/conf.d/wifi_backend.conf`:

```ini
[device]
wifi.backend=iwd
```

```bash
sudo systemctl restart NetworkManager
```

## Kernel Considerations

- **linux-lts** may be more stable than mainline for BCM43602. Try `sudo pacman -S linux-lts linux-lts-headers` if issues persist.
- Kernel 6.10.7+ includes a patch for brcmfmac PMKSA handling that may help without `feature_disable`.

## Firmware Files

brcmfmac looks for files in `/lib/firmware/brcm/`:

| File | Status |
|------|--------|
| `brcmfmac43602-pcie.bin` | Provided by `linux-firmware` |
| `brcmfmac43602-pcie.txt` | Often missing (not redistributable) |
| `brcmfmac43602-pcie.clm_blob` | Often missing |
| `brcmfmac43602-pcie.Apple Inc.-MacBookPro11,4.txt` | Model-specific config |

Missing `.txt` / `.clm_blob` produce warnings in dmesg but the driver works without them. They can be extracted from macOS.

## Debugging via Thunderbolt Ethernet + SSH

Use an **Apple A1433** (or compatible) TB-to-Ethernet adapter for a stable wired connection while debugging WiFi. The adapter uses the **`tg3`** driver (Broadcom BCM57762) -- plug-and-play, very stable. No Thunderbolt authorization needed on MBP 2015.

### Direct cable setup (no router needed)

Connect the MBP (Arch) and macOS machine with a direct Ethernet cable via TB adapters on each side.

On **macOS**:
```bash
# Set static IP: System Preferences > Network > Thunderbolt Ethernet
#   IP: 192.168.2.1, Subnet: 255.255.255.0
```

On **Arch** (MBP):
```bash
ip link                                        # find wired interface
ip addr add 192.168.2.2/24 dev enp0s20f0       # replace with your interface

sudo pacman -S openssh
sudo systemctl enable --now sshd
```

From **macOS**, SSH in and serve scripts:
```bash
# Terminal 1: serve the script
cd /path/to/archlinux/mbp_2015
python3 -m http.server 8000

# Terminal 2: SSH into Arch
ssh root@192.168.2.2

# On the Arch side via SSH:
curl -O http://192.168.2.1:8000/fix_wifi.py
python fix_wifi.py --debug
```

> After suspend/resume, the TB adapter may need a replug.

## Quick Checklist

1. Remove `broadcom-wl` / `broadcom-wl-dkms`
2. Install `linux-firmware`
3. Blacklist `bcma`, `b43`, `b43legacy`, `ssb`, `brcmsmac`, `ndiswrapper`
4. Set `options brcmfmac feature_disable=0x82000 roamoff=1`
5. Disable NetworkManager WiFi powersave (`wifi.powersave = 2`)
6. Disable MAC randomization
7. Disable `iw` power_save via systemd service
8. Set up suspend/resume services if using suspend
9. `sudo mkinitcpio -P && sudo reboot`
