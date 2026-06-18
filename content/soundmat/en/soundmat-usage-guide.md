---
title: "SoundMat Usage Guide"
docLang: en
translationKey: soundmat-usage-guide
alternates:
  zh: /soundmat/soundmat-usage-guide/
  en: /soundmat/en/soundmat-usage-guide/
aliases:
  - /soundmat/en/soundmat-usage-guide/
---

## Checklist

- [ ] Speaker is on; battery ≥ 40% (≥ 60% recommended)
- [ ] Audio cable to speaker; POWER cable to PD 20V power
- [ ] Wait 1–2 minutes; four red positioning LEDs breathing
- [ ] Connect to `SoundMat` hotspot; browser can open the console (optional)

## 1  Wiring

Two cables: one to the speaker, one to power. The power cable is labeled **POWER**. The speaker connects via a USB-C to 3.5 mm adapter to the speaker’s audio input.

## 2  Speaker

Turn on the speaker first; it announces battery level in Chinese. Needs **≥ 40%** (≥ 60% recommended); otherwise volume is very low. Charge via Micro-USB if needed.

The speaker has two Micro-USB ports: **charging** and **audio** — don’t mix them up. A red indicator lights when charging.

Recommended: turn on the speaker and confirm battery level before connecting device power.

## 3  Power On

Connect the POWER cable to a **PD 20V** USB-C charger or power bank. The device starts automatically; allow **1–2 minutes**.

LEDs glow steady first, then breathe. When four red positioning lights appear, the music engine is ready and the device is usable.

## 4  Control Console

The device opens a **`SoundMat`** hotspot (password `soundmat2026`). After connecting your phone or computer, open in a browser:

- Phone: `http://10.42.0.1:8000`
- Computer: `http://soundmat-pi.local:8000` (or `http://10.42.0.1:8000`)

The console does not currently support changing modes.

## 5  Remote Development

Enable a phone hotspot:

| SSID | Password |
| --- | --- |
| `soundmat` | `soundmat2026` |

Connect the phone to WiFi or mobile data, unplug and replug POWER to reboot, and wait about one minute. Once the device joins this hotspot, it has internet access for remote development from anywhere.
