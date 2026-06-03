---
title: "SoundMat (15) Network Solution"
docLang: en
translationKey: soundmat-15-network-solution
alternates:
  zh: /soundmat/soundmat-15-network-solution/
  en: /soundmat/en/soundmat-15-network-solution/
aliases:
  - /soundmat/en/soundmat-15-network-solution/
---

The last stage of software design is the Raspberry Pi **network solution**.

Requirements:

1. Deploy developed code to the Pi and communicate with it—**SSH** must work  
2. During use, control modes and parameters via **Web**—real-time LAN communication  
3. One optional Ambient-mode feature needs live internet  

On boot, NetworkManager tries known WiFi networks in priority order. **60 s timeout**: if connected, normal STA operation; if no IP after 60 s, activate AP config—a hotspot named `SoundMat`, fixed IP `10.42.0.1`.

Whether STA or AP, the console URL is always **`http://soundmat-pi.local:8000`** via **avahi-daemon** (mDNS).

In STA mode, any phone on the same WiFi can use that URL. In AP mode, connect to the `SoundMat` hotspot and use the same URL.

**WiFi configuration**

**STA mode (join known WiFi)**

| Priority | SSID | Password | Notes |
| --- | --- | --- | --- |
| 100 | `soundmat` | `soundmat2026` | Your phone hotspot |
| | | | |

**AP mode (Pi as hotspot)**

| Field | Value |
| --- | --- |
| SSID | `SoundMat` |
| Password | `soundmat2026` |
| Band | 2.4 GHz |
| Pi IP | `10.42.0.1` |
| Console | `http://soundmat-pi.local:8000` |
