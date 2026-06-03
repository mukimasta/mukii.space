---
title: "SoundMat (8) Interaction and Sonification Design"
docLang: en
translationKey: soundmat-8-interaction-and-sonification
alternates:
  zh: /soundmat/soundmat-8-interaction-and-sonification/
  en: /soundmat/en/soundmat-8-interaction-and-sonification/
aliases:
  - /soundmat/en/soundmat-8-interaction-and-sonification/
---




Sonification design is the soul of SoundMat. We have already settled the product philosophy and designed the structure, appearance, sensors, hardware, and so on—but those are only the foundation, the places where imperfection arises. Sonification design—how stones and the audience’s touch and pressure become music, in line with the musical art installation we imagine—is the trickiest part, and the easiest to make mediocre.

Beyond that is LED interaction design. That part is relatively the finishing touch; it serves two functions: cueing and feedback. Through LED cues, users can tell which stage the music has reached and feel the current mood; feedback means that after interacting with SoundMat, besides auditory response, they also get visual LED feedback, which strengthens the sense of participation and artistry.

Real hardware is not ideal. There is error and imprecision. In earlier hardware manufacturing, we gained a fuller picture of how “object placement sensing” behaves in practice:
- SoundMat sensing resolution is 8 rings × 16/32 slices—224 small regions. We can tell which region has an object, but not how many objects are in that region, not where within the small region, and not whether activation in adjacent regions comes from two small objects or one large one. For our stone sizes we can keep a reasonable correspondence between stones and regions, but for design, overly fine granularity makes the interaction experience worse.



We will complete interaction and sonification design under these constraints.

## 1  Generating Music: The Tension Between Freedom and Feedback

From the design philosophy onward, we keep stressing that interaction should be simple and intuitive—sounds good however you place things—yet still feel participatory / responsive.

“Sounds good however you place” vs. “participation / feedback” is really a tension. “Sounds good however you place” means less variation and more system intervention; feedback comes from feeling that *I* influenced the whole system—that *I* am in control, not that the system is helping me.

So there are two poles of freedom:
- **Low freedom**: sounds good however you place, strong immersion; but less variation, weak sense of control, easy to bore
- **High freedom**: strong feedback, more variation; but easy to go wrong, break immersion, requires musical knowledge

Push to the extreme and it’s clear: maximum freedom is an instrument. Piano, guitar—enormously rich variation but hard to learn; minimum freedom is a mixer—only controlling which instruments play, easy to bore.

One idea is different modes for different contexts. Two modes:
- **Ambient mode**: low freedom, hotel lobby, provides atmosphere
- **Jam mode**: high freedom, allows dissonance, active multi-person participation, more like an instrument

## 2  Control Approaches: Mixing vs. Generation

This section discusses two control approaches for musical installations.

**Mixing** adjusts parameters of existing music—volume, timbre, EQ, tempo, and so on.

**Generation** creates elements in real time for each action—notes, percussion, harmony, musical fragments, and so on.

In SoundMat, generation is absolutely dominant. Users are not adjusting someone else’s existing music; they are creating their own.

## 3  Interaction Methods: Rotating Scan and Sound Pool

For SoundMat, there are two interaction approaches.

**Rotating scan**: a virtual pointer rotates around the center; when it hits an object, it triggers music generation. One full circle naturally forms a loop; different angles represent different times within that loop. Placing a stone is like writing a musical element on the score.

**Sound pool**: once an object is placed, the music-generation mechanism at that position keeps firing; when the object is lifted, it stops.

## 4  Brief Overview of Music Types

[SoundMat (2) Product Design Philosophy](/soundmat/en/soundmat-2-philosophy/) briefly discusses music types suited to SoundMat. Here we expand on the types we chose.

**Ambient / Soundscape**: as public art installation, Ambient-style music lets the piece be noticed and listened to, or ignored.

Roughly two kinds: musical elements and soundscape elements. Musical elements have definite pitch—they come from instruments or synthesis and obey a tonal system; soundscapes are field recordings, sound fragments, not bound by tonality.

**Lo-Fi**: Lo-fi is warm, grainy, imperfect texture—often loop-based, strongly rhythmic, very suited to our rhythmic mode (rotating scan). Lo-Fi also gives strong immersion.

**Minimal**: generative minimal music is represented by Steve Reich and Philip Glass. Music often rests on extremely simple elements—a few notes, chords, motifs. Classic techniques include phasing and phase-shifting: the same fragment at different speeds across voices, or phase shifts within the piece, weaving new, staggered rhythms that eventually resynchronize—strange and wonderful to hear. A classic is *Clapping Music*.


## 5  Ambient Mode Design: Narrative in Sound

Ambient mode aims for music that can be noticed and listened to, or ignored. However many stones are on the surface, music always exists as atmosphere—not jarring, not empty—like a background color for the environment.

In our Ambient demo we had a basic prototype. Inside to outside maps low to high frequency—eight musical elements total. Sectors within a ring don’t differ; stone count on the same ring controls that layer’s musical content.

The demo’s choice of eight elements was the most basic: pentatonic drone, pad, synthetic notes, synthetic rain, synthetic water drops—it sounded okay and met our minimum bar.

But the problem: it’s too ordinary. Add a low layer, some notes, bird calls, bells. After playing I think “nice”—and then what?

I want *art*. So I wondered: could we make a “narrative environment”? Previous elements had no connection; but with environmental narrative—a coherent, logical set of musical elements—it wouldn’t be ordinary.

Environmental narrative lets the user unfold a scene gradually as they place stones. The narrative I most want is a Japanese temple. A cosmic environment also fits—the device shape is literally concentric rings.



**Environmental music mode — *Arashiyama, Kyoto***

Foundation

[Locus Sonus – Locustream – sound map](https://locusonus.org/soundmap/): yamanashi — yamanakako (Japan)


**Key:**

 C major pentatonic


**Ring 0 / Ring 1: bass**

- Trigger: heavy drum + large temple bell
- Sustain: synthetic organ drone + breath-like texture


**Ring 2: mid-low**

- Sustain: harmonic fragments, transposed to the key


**Ring 3: bamboo grove train**

- One stone
	- Trigger: footsteps
	- Sustain: bamboo wind + stream
- Two stones
	- Trigger: railway crossing bell / ding-ding-ding
	- Sustain: stronger bamboo wind + stream
- Three stones
	- Trigger: crossing bell + railway sound fragment
	- Sustain: stronger bamboo wind + stream

**Ring 4: weather — rain, thunder**

- One stone
	- Sustain: light rain
		- If Ring 3 active: rain on bamboo leaves + rain on water
- Two stones
	- Sustain: moderate rain + strong wind
- Three stones
	- Sustain: heavy rain + howling wind
	- Effect: wide-scene spatial reverb
- Four stones
	- Sustain: heavy rain + thunder
	- Effect: wide-scene spatial reverb

**Ring 5: [mid-high pitch generation]**

- Trigger: synthetic marimba
- Sustain: random marimba
- Sector angle maps to pitch; split in half: 0–15, 31–16 symmetric


**Ring 6: melodic fragment loop**

- Sustain: material



**Ring 7: events**

- Trigger: material
- Sustain: random trigger material



**Special pattern:**

- Stones chained across rings: riding the Arashiyama scenic railway
- 



## 6  Jam Mode – Lo-Fi Loop

Harmony and drums loop fixed; only mix, not generate.
Melody (including bass) uses rotating scan.


### 6.1  Meter

| Option | Time sig. | Chord progression loop length | Each chord lasts | SoundMat one revolution | 32-slice resolution | Grids per bar | Quantized grids per bar |
| ------ | --------- | ------------------------------- | ---------------- | ------------------------- | ------------------- | ------------- | ----------------------- |
| Option 1 | 4/4 | 4 bars | 1 bar | 4 bars | 8th notes | 8 | 8 |
| Option 2 | 4/4 | 8 bars | 2 bars (repeat once) | 8 bars | quarter notes | 4 | 4 |
| **Option 3** | **4/4** | **8 bars** | **2 bars (repeat once)** | **2 bars** | **16th notes** | **16** | **8** |
| Option 4 | 4/4 | 4 bars | 1 bar | 2 bars | 16th notes | 16 | 8 |

After comparison, we chose Option 3. Reason: balance of repetition and contrast. Same trigger timing → repetition; different trigger pitch → contrast.

Default tempo is provisionally 120 bpm. (Designed as an adjustable parameter.)

Thus slice 0–15 is the first bar of each chord; slice 16–31 is the second bar.

Example:

**Bar 1 — Slice 0–15**

|Beat|1|e|&|a|2|e|&|a|3|e|&|a|4|e|&|a|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|**Slice**|0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|

**Bar 2 — Slice 16–31**

|Beat|1|e|&|a|2|e|&|a|3|e|&|a|4|e|&|a|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|**Slice**|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|

0° is slice 0, 90° is slice 8, 180° is slice 16

Quantization is handled later; see below.

### 6.2  Ring Interaction Design

**Ring 0/1**  No angle—start/stop control and global Lo-Fi mix

Treat R0/R1 as one unit. Sum of pressure on all R0+R1 cells (raw ADC) determines control state; per-cell threshold (default 500) decides whether that cell has a stone.

- No control stones (pressure sum < `control_sum_min`, default 250): scan line stationary, global reset; placing stones on R2–R7 immediately previews one hit (default volume 50%) and lights LED preview
- Control stones present (pressure sum ≥ 250): transport starts automatically, scan line advances
- Control stones briefly disappear (ADC glitch): within 100 ms release hold still treated as control stones, avoiding false reset
- Pressure sum maps Lo-Fi 0–1000 (default sum ≤0 → 0, sum ≥ 1000 → 1000); higher → duller, warmer, stronger tape grain
- Lo-Fi adjusted continuously in real time, unaffected by scan line (`cutoff` + `drive` → `jam_master`)
- Placing stones on outer rings during loop playback: optional immediate preview (Control page Place preview slider, default 25%; drag to 0 to disable)
- At end of piece (after 8 drum-sequence passes): must clear R0/R1 and place again to restart

Deployment defaults match Mat page Calibration: `threshold=500`, `control_sum_min=250`, Lo-Fi sum max 1000 (defaults restored on reboot, not persisted).



**Ring 4–6**  Melody

Different instruments per ring


> **Forward legato (deprecated; not implemented)**
> 
> One beat divided into a group of four trigger notes. Each cell stores only one trigger; when the scan line hits a cell, not only that cell sounds—a random forward burst from that cell within the group (so hitting one cell may produce 1–4 notes), legato.
> 
> Burst must not cross the current group boundary. If downstream in the same ring and group there is another stone, burst stops before that stone.
> 
> In practice, forward legato could be a parameter: max legato count, range 1–4; 1 means no legato.



Melody quantized to 8 eighth-note trigger positions per bar (2× quantization, merge pairs: eighth notes; odd slices merge down to even, trigger timing merges to even—e.g. slice 1 functionally equals slice 0, triggers at slice 0).


**Ring 2/3**  Bass melody

Bass voice also quantized to 8 trigger positions (2× quantization, eighth-note merge).


**Ring names and roles**

| Ring | Role | Timbre |
| ---- | ---- | ------ |
| R7 (outermost) | Melody | Marimba |
| R6 | Melody | Lo-Fi electric piano |
| R5 | Melody | Lo-Fi electric piano |
| R4 | Melody | Pad-Pluck |
| R3 | Bass | Pluck bass |
| R2 (innermost) | BASS | Sub bass |


### 6.3  Harmony / Chord Progression


**Pitch notation**

Digits 1–7 are scale degrees in the current key (movable do, not fixed pitch).

**Accidentals** after the digit: `#` half step up, `b` half step down.  
**Octave** at the end: `^` up one octave, `_` down one octave, stackable (`^^` / `__`). No octave mark = 4th octave.  
**Fixed order**: digit → accidental → octave, e.g. `1#^`.  
**null** = same as previous.

Examples (C major):

|Notation|Actual pitch|
|---|---|
|`1`|C4|
|`1#`|C#4|
|`1^`|C5|
|`1#^`|C#5|
|`6__`|A2|
|`4b_`|E3|

**Transposition**: change manifest `[music].key`; all notation shifts with the key root. E.g. `1^` is C5 in C major; after key → B it becomes B4. Entire piece—melody, bass, chord voicing—transposes consistently.




| **No.** | **Degrees / chord cycle** |
| ------- | ------------------------- |
| **1** | 2m9 → 513 → 1maj9 → 69 |
| **1B** | 2m9 → 2m9/5, 57b9 → 1maj9 → 16, 1#dim |
| **1C** | 2m9 → 59 → 3m7 → 67 |

Harmony 1 voicing
```
2m9: 2_ · 4_ · 6_ · 1 · 3
513: 5__ · 2_ · 4_ · 7_ · 3
1maj9: 1_ · 3_ · 5_ · 7_ · 2
69: 6__ · 3_ · 5_ · 7_ · 1#
```


Prototype implements harmony 1 first.

### 6.4  Melody Trigger Notes

Design approach:

Beats 1 and 3: same—chord tones minus root, placed in melody; adjacent chords on the same ring link.
BASS uses root.

Beats 2 and 4



Harmony 1 trigger notes:


**Chord 1: 2m9**

(2 4 6 1^ 3^)

| Ring | 1 | & | 2 | & | 3 | & | 4 | & |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sector | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| **R7** | 3^ | 1^ | 2^ | 3^ | 3^ | 2^ | 1^ | 6 |
| **R6** | 1^ | 5 | 6 | 1^ | 1^ | 5 | 6 | 3^ |
| **R5** | 6 | 3 | 4 | 6 | 6 | 4 | 3 | 2 |
| **R4** | 4 | 3 | 2 | 3 | 4 | 3 | 2 | 3 |
| **R3** bass | 4_ | 4_ | 6_ | 6_ | 4_ | 4_ | 6_ | 6_ |
| **R2** BASS | 2_ | 2_ | 2_ | 2_ | 2_ | 2_ | 2_ | 2_ |

**Chord 2: 513**

(5_ 7_ 2 4 6 1^ 3^)

| Ring | 1 | & | 2 | & | 3 | & | 4 | & |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sector | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| **R7** | 3^ | 1^ | 2^ | 3^ | 3^ | 2^ | 1^ | 5 |
| **R6** | 7 | 5 | 6 | 7 | 7 | 5 | 6 | 5 |
| **R5** | 5 | 2 | 3 | 5 | 5 | 3 | 2 | 7_ |
| **R4** | 2 | 3 | 1 | 2 | 2 | 3 | 7_ | 1 |
| **R3** bass | 4_ | 4_ | 5_ | 5_ | 4_ | 4_ | 5_ | 5_ |
| **R2** BASS | 5__ | 5__ | 5__ | 5__ | 5__ | 5__ | 5__ | 5_ |

**Chord 3: 1maj9**

(1 3 5 7 2^)

| Ring | 1 | & | 2 | & | 3 | & | 4 | & |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sector | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| **R7** | 2^ | 7 | 1^ | 2^ | 2^ | 1^ | 3^ | 5 |
| **R6** | 7 | 6 | 5 | 6 | 7 | 6 | 5 | 3 |
| **R5** | 5 | 2 | 3 | 5 | 5 | 3 | 2 | 1 |
| **R4** | 3 | 2 | 1 | 3 | 3 | 1 | 7_ | 1 |
| **R3** bass | 3_ | 3_ | 5_ | 5_ | 3_ | 3_ | 5_ | 5_ |
| **R2** BASS | 1_ | 1_ | 1_ | 1_ | 1_ | 1_ | 1_ | 1_ |

**Chord 4: 69**

(6_ 1# 3 5 7)

| Ring | 1 | & | 2 | & | 3 | & | 4 | & |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sector | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| **R7** | 1#^ | 2^ | 3^ | 2^ | 1#^ | 2^ | 3^ | 1#^ |
| **R6** | 6 | 3 | 5 | 6 | 6 | 5 | 3 | 6_ |
| **R5** | 5 | 2 | 3 | 5 | 5 | 3 | 2 | 1# |
| **R4** | 3 | 2 | 1# | 2 | 3 | 2 | 1# | 3 |
| **R3** bass | 3_ | 3_ | 5_ | 5_ | 3_ | 3_ | 5_ | 5_ |
| **R2** BASS | 6__ | 6__ | 6__ | 6__ | 6__ | 6__ | 6__ | 6__ |

### 6.5  Drums

`X` = accent hit, `x` = ghost / light hit.

**Loop A: empty**

**Loop B**

| Instrument | 1 | e | & | a | 2 | e | & | a | 3 | e | & | a | 4 | e | & | a |
| ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Kick** | X | | | | | | | | | | | | | | | |
| **Snare** | | | | | | | | | | | | | | | | |
| **Hi-hat** | X | | X | | X | | X | | X | | X | | X | | X | |

**Loop C**

| Instrument | 1 | e | & | a | 2 | e | & | a | 3 | e | & | a | 4 | e | & | a |
| ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Kick** | X | | | | | | | | | | X | | | | | |
| **Snare** | | | | | X | | | | | | | | X | | | |
| **Hi-hat** | X | | X | | X | | X | | X | | X | | X | | X | |

**Loop D**

| Instrument | 1 | e | & | a | 2 | e | & | a | 3 | e | & | a | 4 | e | & | a |
| ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Kick** | X | | | x | | | | x | | | X | | | | | |
| **Snare** | | | | | X | | | | | | | | X | | | |
| **Hi-hat** | X | | X | | X | | X | | X | x | X | | X | | X | x |

Two approaches:
1. Fixed number of passes
	- Option 1 meter (4 bar): A×1→B×1→C×2→A×2→D×2→A×2
	- Option 3 meter (2 bar): A×1→B×1→C×2→A×1→D×1→A×1
2. ABCD determined by object count

We use fixed passes: **A×1→B×1→C×2→A×1→D×2→A×1**

After that, scan stops and harmony/drums no longer advance; must clear R0/R1 to restart.

Harmony and drums are both synthesized in real time (not samples); multiple stones in one sector attenuate velocity by 1/√N.


### 6.6  Jam LED Scheme

108 LEDs evenly around the ring, aligned with 32 melody sectors. This section describes on/off and color only—not implementation.

#### Layout

- **#0** at 12 o’clock; indices increase **clockwise** (0 → 107 → 0).
- Sector `n` center LED: `round(n ÷ 32 × 108) mod 108`.
- Recommended refresh **≥ 60 Hz**, 108-channel RGB per frame.

#### Colors (RGB 0–255)

| Name | R | G | B | Used for |
| ---- | --- | --- | --- | -------- |
| White | 255 | 255 | 255 | Idle breathing, scan trail |
| True red | 255 | 48 | 48 | 12 o’clock marker #0 |
| Light red | 255 | 140 | 140 | E/S/W markers #27 #54 #81 |
| R0 | 100 | 108 | 128 | Transport (preview/hit/marker generally unused) |
| R1 | 148 | 112 | 88 | Transport |
| R2 | 88 | 72 | 210 | Bass |
| R3 | 32 | 188 | 148 | Bass |
| R4 | 48 | 152 | 255 | Melody |
| R5 | 200 | 72 | 168 | Melody |
| R6 | 218 | 158 | 48 | Melody |
| R7 | 255 | 108 | 32 | Melody |

#### Cardinal markers

Fixed LEDs **#0, #27, #54, #81** (N/E/S/W). Breathing period ~ **4.6 s** (`sin(t×1.35)`).

- **#0**: true red; **#27 / #54 / #81**: light red
- **All states** (idle, playing, finished): four markers share red breathing, opacity **75%–100%** (relative to color peak)
- **Non-markers**: only in **idle**—full-ring dim white breathing **0–20** (RGB); no ambient white field while playing / finished

**Logic ↔ physical alignment** (Mat page Calibration, defaults): `sector_offset=4` (S→L logical sector rotation), `led_offset=101` (strip physical rotation, applied uniformly in `set_buffer`), `wire_slice_mirror=on` (column mirror—aligns physical CW with software CW sector). LED #0 and slice 0 align via these offsets—not “unmeasured.”

#### Modes

Priority top to bottom; first match wins.

- **Finished** — Piece ended and not playing: all off except four markers; markers still true/light red breathing. Clear R0/R1 or reset to exit.
- **Playing** — Active playback: no full-ring ambient breathing; LEDs with no effect **off**; only white scan trail, R2–R7 stone dim markers, marker red breathing. Placing R0/R1 **starts transport** automatically.
- **Idle** — Not playing and not finished: non-markers full-ring dim white breathing **0–20**; four markers red breathing **75%–100%** (including melody stones only, control sum not yet reached).

#### During playback

**Scan (white)**

- Only **behind** the scan head lit, not ahead; head advances clockwise.
- Brightness ratios for 0–10 LEDs trailing the head: **1.00 · 0.75 · 0.40 · 0.30 · 0.22 · 0.15 · 0.10 · 0.06 · 0.03 · 0.01 · 0**.
- No scan, no stones, not a marker: **off**.

**Stone markers (R2–R7)**

- Per stone: sector center LED plus one each side (~3 LEDs), ring color overlaid (~ **22% opacity × 55% mix** on white base)

#### Short effects

**Preview** (stone placed on R2–R7)

- **Idle**: sector center ±2 LEDs, ring color, **100%** brightness, **1000 ms** cosine fade; corresponding single-note preview (default **50%** volume)
- **During loop** (Place preview > 0): same LED preview + immediate one hit (default **25%** volume), marked triggered to avoid scan duplicate

**Scan hit** (scan passes stone while playing)

- Sector center and clockwise indices **+1, 0, −1, −2**—**4 LEDs** total (excludes **+2**), ring color, **180 ms** total (~10 ms rise, hold to 50 ms, then squared decay).
- Brightness: **100%** (center) · **82%** (±1) · **52%** (−2).
- Composited with scan white by **brighter** of the two—no dimming, no punching hole in trail; independent of whether mat shows scan line.

Finished state: no preview overlay; no hit flash when not playing.

## Synthesis order

Per LED per frame: mode base → preview overlay (if any) → hit overlay (if any, brighter-wins with base). Markers in playing and finished states still override same index per red-breathing rules.


## Timbre and effects table

See Web Demo

src/soundmat/jam/synths



---

Initial trigger notes (deprecated)

> | Beat | 1 | 2 | 3 | 4 |
> | ---- | --- | --- | --- | --- |
> | **Chord** | 2m9 | 513 | 1maj9 | 69 |
> | 1 | 3 4 6 1^ 3^ | 3 4 6 7 3^ | 2 3 6 7 2^ | 3 5 7 1#^ 2 |
> | 1& | 2 1^ 2^ 3^ 4^ | 1 2 5 1^ 4^ | 3 4 7 1^ 3^ | 1# 3 6 2^ 3^ |
> | 2 | 1 4 6 1^ 3^ | 4 5 7 2^ 3^ | 2 5 6 7 2^ | 7_ 4 5 7 1#^ |
> | 2& | 2 6 1^ 3^ 4^ | 2 3 5 1^ 4^ | 3 4 7 2^ 3^ | 1# 3 6 1#^ 2^ |
> | 3 | 3 4 6 1^ 3^ | 3 4 6 7 3^ | 2 3 6 7 2^ | 3 5 7 1#^ 2 |
> | 3& | 5 6 1^ 6 2^ | 1 3 5 1^ 2^ | 1 2 5 6 1^ | 1# 3 5 6 1#^ |
> | 4 | 3 4 6 1^ 1^ | 7_ 2 4 7 1^ | 7_ 1 3 5 7 | 6_ 3 6 1#^ 3^ |
> | 4& | 1 3 4 3^ 6 | 5_ 1 2 4 5 | 1 7_ 2 3 5 | 5_ 1# 3 6 1#^ |
> 
> Each group of five numbers in the table is the trigger note for rings 3–7 at that beat
