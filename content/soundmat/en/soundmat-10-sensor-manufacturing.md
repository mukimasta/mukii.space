---
title: "SoundMat (10) Sensor Manufacturing"
docLang: en
translationKey: soundmat-10-sensor-manufacturing
alternates:
  zh: /soundmat/soundmat-10-sensor-manufacturing/
  en: /soundmat/en/soundmat-10-sensor-manufacturing/
aliases:
  - /soundmat/en/soundmat-10-sensor-manufacturing/
---

In [SoundMat (5) Sensor Principles and Design](/soundmat/en/soundmat-5-sensor-principles-and-design/) we covered theory and layout. This chapter covers **manufacturing**.

Stack bottom to top:

1. Board  
2. Concentric ring electrodes (Rings)  
3. Velostat (piezoresistive layer)  
4. Sector electrodes (Slices)  

That is also build order.

## 1 Laser cutting overview

Laser cutting focuses a high-energy beam on the material surface, melting/vaporizing/ablation in milliseconds. Two jobs: **cut** (through-cut) and **etch** (surface pattern).

Input is vector art (SVG, PDF, etc.) with colors/layers marking cut vs etch, plus power/speed per material.

Absorption depends on wavelength → pick the right machine. We used **CO₂** and **fiber** lasers:

| | CO₂ laser | Fiber laser |
| --- | --- | --- |
| **Wavelength** | ~10.6 μm (far IR) | ~1.06 μm (near IR) |
| **Source** | CO₂ discharge tube | Rare-earth-doped fiber |
| **Good for** | Non-metals: wood, acrylic, paper, fabric, leather | Metal, metal-coated materials |
| **Poor for** | Metal (low absorption) | Clear non-metals |
| **Precision** | Medium (larger spot) | High (smaller spot) |

## 2 Manufacturing steps
