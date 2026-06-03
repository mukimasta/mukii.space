---
title: "SoundMat (5) Sensor Principles and Design"
docLang: en
translationKey: soundmat-5-sensor-principles-and-design
alternates:
  zh: /soundmat/soundmat-5-sensor-principles-and-design/
  en: /soundmat/en/soundmat-5-sensor-principles-and-design/
aliases:
  - /soundmat/en/soundmat-5-sensor-principles-and-design/
---

### 1.1 Sensing principle

SoundMat sensing is based on the **piezoresistive effect**. We use **Velostat**—carbon-filled polyethylene film that looks like black paper. With no pressure, carbon particles are far apart, few conductive paths, high resistance. Under pressure the film compresses, particles move closer, more paths form, resistance drops sharply. More pressure → lower resistance.

So we sense pressure by sensing Velostat resistance. Read resistance → know where something is and roughly how heavy it is.

![](/soundmat/sensor-velostat-principle.png)  
(Fig.[^1])

A typical sensing circuit (by Nano Banana):

![](/soundmat/sensor-divider-circuit.png)

$$V_{out} = VCC × \frac{R_{sensor}}{(R_{ref} + R_{sensor})}$$

Read $V_{out}$ with an ADC to infer $R_{sensor}$, hence pressure.

For a 2D pressure array, the **sandwich structure** is classic and saves wiring:

![](/soundmat/sensor-sandwich-structure.png)  
([^2])

Top: conductive fabric strips (rows). Middle: one Velostat sheet. Bottom: conductive fabric strips perpendicular (columns). Each row–column crossing with Velostat between is one cell. M×N cells need only M+N wires.

To read each crossing: **row scanning**—drive one row HIGH, others LOW (critical to prevent ghost paths), read each column voltage, then next row.

![](/soundmat/sensor-scanning-circuit.png)

(a) Sandwich circuit: rows/columns; yellow = Velostat resistance; red = pressed (lower R).  
(b) Single press: one column shows voltage; FLOAT or GND isolation both work.  
(c) Multiple presses with inactive rows FLOAT: false positives (blue cell appears pressed).  
(d) Inactive rows GND: false positives fixed.  
(e) Inactive rows GND: crosstalk—multiple presses on one column parallel to ground, voltage lower than single press.

### 1.2 Array topology

Standard Cartesian row/column scan—but SoundMat is circular, so **polar coordinates** are natural: concentric rings as one electrode set, radial slices as the other. Same principle, polar geometry.

| | Cartesian grid | Polar |
| --- | --- | --- |
| **Fit to round form** | Wasted corners, truncated edge cells | Matches circle; every cell useful |
| **Interaction semantics** | x/y only; extra mapping to music | Radius → one parameter, angle → another; intuitive |
| **Fabrication** | Straight cuts, forgiving | Arcs/rays need precision; rings need through-board routing |
| **Crosstalk** | Uniform spacing, simpler compensation | Dense inner / sparse outer; zone-based compensation |

We chose **polar**. Fewer cells can still localize “which annular region” well; Cartesian would need much denser grid for the same effect.

![](/soundmat/sensor-polar-array.png)

**Sizing**

From the bowl planter in [SoundMat (4) Structural Design](/soundmat/en/soundmat-4-structural-design/): nominal 24", measured inner ~22.7", sensor disk **22" (55.88 cm)** (gap for LEDs). That disk is also the rigid board diameter.

**Ring and slice counts:** Each ring is a musical layer (instrument group). Four rings felt too few; beyond ten, fabrication cost rises—**8 rings**. Slices set loop “subdivision” in rhythm mode; count should be multiple of 2 or 6—**32 slices** fits a ~60 cm disk with 8 rings.

Final layout is not strict 32 slices everywhere: inner sectors shrink toward center, so **rings 1–2 use 16 slices**, aligned with outer rings.

Coordinate mapping: [SoundMat (12) Software Design and Development](/soundmat/en/soundmat-12-software-design-and-development/#55-key-files) (`core/sensor/map.py`)

Ring/slice gaps minimized for sensing area—**0.3 mm** and **0.357 mm** tested without severe crosstalk. Ring OD **54.2 cm**, slice OD **55.0 cm**. Detail:

| Ring | Active sectors | Center Ø cm | Ring width cm | Ring gap cm | Slice spacing at center cm | Effective width at center cm | Min slice gap cm | Min effective width cm | Max slice gap cm | Max effective width cm |
| ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 16 | 8.000 | 2.75 | 3.11 | 1.571 | 1.221 | 1.031 | 0.681 | 2.111 | 1.761 |
| 2 | 16 | 14.214 | 2.75 | 3.11 | 2.791 | 2.441 | 2.251 | 1.901 | 3.331 | 2.981 |
| 3 | 32 | 20.429 | 2.75 | 3.11 | 2.006 | 1.656 | 1.736 | 1.386 | 2.276 | 1.926 |
| 4 | 32 | 26.643 | 2.75 | 3.11 | 2.616 | 2.266 | 2.346 | 1.996 | 2.886 | 2.536 |
| 5 | 32 | 32.857 | 2.75 | 3.11 | 3.226 | 2.876 | 2.956 | 2.606 | 3.496 | 3.146 |
| 6 | 32 | 39.071 | 2.75 | 3.11 | 3.836 | 3.486 | 3.566 | 3.216 | 4.106 | 3.756 |
| 7 | 32 | 45.286 | 2.75 | 3.11 | 4.446 | 4.096 | 4.176 | 3.826 | 4.716 | 4.366 |
| 8 | 32 | 51.500 | 2.75 | 3.11 | 5.056 | 4.706 | 4.786 | 4.436 | 5.326 | 4.976 |

Cell size ~2.75×1 cm to 2.75×5 cm—matches pebble contact.

**Final specs**

| Parameter | Value |
| --- | --- |
| Planter nominal | 24 in |
| Rigid board diameter | 55.88 cm |
| Rings | 8 |
| Slices | 32 |
| Slice outer diameter | 55.0 cm |
| Ring outer diameter | 54.2 cm |
| Slice gap | 3.5 mm |
| Ring gap | 3.57 mm |

![](/soundmat/sensor-final-design.png)

Surface must stay flat, so electronics live **below** sensor/board. Rings use **through-board holes**: drill at ring positions, connect from below with conductive material. Slices route to the edge—no through-holes—connect from rim under the board.

In fabrication each ring gets a **tail**—conductive fabric through matching holes to the cavity. Slices use **copper foil tape** folded from edge to board underside for both electrical connection and securing the top sensor layer.

### 1.3 Automated sensor design tool

We vibe-coded a tool in Cursor: enter parameters → auto-generate laser-cutting files (SVG/PDF).

Pipeline: parameters → geometry → canvas preview / SVG, PDF export

[GitHub – mukimasta/sensor_design_tool](https://github.com/mukimasta/sensor_design_tool)

(Written May 2026)

---

[^1]: Sumana, Marius & Treciokaite, Vaiva & Čerškus, A. & Dzedzickis, Andrius & Bučinskas, Vytautas & Morkvėnaitė, Inga. (2022). Sitting Posture Monitoring Using Velostat Based Pressure Sensors Matrix. 10.1007/978-3-031-03502-9_20.

[^2]: L. Yuan, H. Qu and J. Li, "Velostat Sensor Array for Object Recognition," in IEEE Sensors Journal, vol. 22, no. 2, pp. 1692-1704, 15 Jan.15, 2022, doi: 10.1109/JSEN.2021.3132793.
