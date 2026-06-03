---
title: "SoundMat Presentation"
docLang: en
translationKey: soundmat-presentation
alternates:
  zh: /soundmat/soundmat-presentation/
  en: /soundmat/en/soundmat-presentation/
aliases:
  - /soundmat/en/soundmat-presentation/
---




## I. Design philosophy

The deck is not one visual style all the way through—it mixes three slide types for rhythm:

**Hero Slide** — Pure typography, one full-screen line, e.g. “Place stones. Make music.” Use for section openers, key claims, emotional turns.

**Bento Slide** — Multi-card grid, 4–6 features on one screen. Use to show several facets of one module (e.g. sensor: “design principle / product photo / spec numbers / comparison decision” as a quartet).

**Zoom Slide** — One full-screen image or one big number. Use for system architecture, wow metrics, sensor close-ups.

Alternate the three types so you avoid fatigue from “all dense grids” or emptiness from “all huge type.” The visual rhythm should feel like a recent Apple keynote—big type opener → bento for detail → zoom on a highlight → back to bento to advance → big type to close.

## II. Visual system

**Color** follows Apple’s recent light-keynote direction, not early black-stage decks:

- Main background: white `#FFFFFF` or near-white `#F5F5F7`
- Bento card fills: flexible by content—light gray `#FAFAFA`, dark emphasis `#1D1D1F`, occasional warm orange-yellow `#F5A623` (few cards, tied to the installation and LED look)
- Text: black `#1D1D1F` (primary) / gray `#86868B` (secondary)

**Type**

- Latin headlines/body: SF Pro Display + SF Pro Text; open substitute Inter
- Chinese: PingFang SC; web substitute Noto Sans SC
- Numbers / specs: SF Mono or JetBrains Mono

**Size scale** (for 1080p height)

- Hero title: 120–160px
- Bento card title: 28–36px
- Bento card body: 18–22px
- Wow number: 80–120px (extra large)
- Caption / footnote: 14–16px

**Corners**: uniform 20px on cards, images, and video frames—a core Apple detail.

**Whitespace**: card gap 24–32px, slide padding 64–96px. **More white than content.**

## III. Slide list and type assignment

~13–14 slides for a 10-minute pace:

|#|Type|Content|Time|
|---|---|---|---|
|1|Hero|"SoundMat" + subtitle|20s|
|2|Hero|"Place stones. Make music." (two-beat reveal)|30s|
|3|Bento|Idea → Constraints bridge (4 cards: render + 3 engineering constraint cards)|60s|
|4|Zoom|Full system architecture, full screen|60s|
|5|Bento|Sensor (5 cards: polar plot, comparison table, photo, sandwich structure, “224 zones”)|90s|
|6|Bento|Electronics (5 cards: power chain, perfboard photo, module roles, USB DAC decision, PD 20V number)|90s|
|7|Bento|Firmware + serial protocol (3 cards: scan timing, S/L frame format, performance numbers)|45s|
|8|Hero|"Logic in Python. Sound in SuperCollider." (antithesis)|15s|
|9|Bento|Software architecture (4 cards: diagram, mode switch, Web console screenshot, SC group isolation)|60s|
|10|Bento|Jam mode sonification (4 cards: 8-ring roles, scan line + quantization, chord progression table, Lo-Fi control)|90s|
|11|Zoom|Ambient mode one image + line “Still iterating.”|20s|
|12|Bento|Challenges and iteration (3 cards: PD trigger rework, Micro USB → breakout, Lo-Fi freedom paradox)|45s|
|13|Hero|"Live Demo" full screen|5s|
|14|Closing|Thanks / Q&A|—|

## IV. Bento slide internal rules

Every Bento needs **one hero card** (~40–50% of area); the rest are supporting (~20% medium, ~10% small). That hierarchy—not a uniform grid—is how Apple bento works.

**Card content modes** (only three):

1. **Image-dominant**: full-card image (photo, render, diagram), caption small at bottom or corner
2. **Number-dominant**: huge number + one line, e.g. “`224` sensing zones”
3. **Text-dominant**: title + short paragraph, no image

**Avoid**:

- Too much text on one card (over ~30 characters → split)
- Bullets inside a card (breaks “one card, one idea”)
- Emoji decoration (Apple keynotes don’t use emoji)

**Layout templates** (by card count):

- 4 cards: 1 large + 3 medium (large left full height, 3 stacked right)
- 5 cards: 1 large + 2 medium + 2 small
- 6 cards: 2 medium + 4 small
- 3 cards: 1 large + 2 medium in a row

Never more than 6 cards—split into two slides.

## V. Motion system

**Only three animations** for the whole deck:

- **Stagger fade up**: elements from y=20px to y=0, stagger 80–120ms. Hero text, bento card entrance.
- **Scale fade**: scale 0.96 → 1.0 + opacity 0 → 1. Zoom slide hero elements.
- **Count up**: number rolls 0 → target over 800–1200ms. Only on wow-number slides (224, 32, 921600, 20Hz, &lt;50ms, etc.).

**Global params**:

- Duration: 700ms (default), 900ms (hero text)
- Easing: `cubic-bezier(0.22, 1, 0.36, 1)` (Apple-style ease-out-quart)
- No linear, ease, or ease-in-out defaults

**Per-slide entrance order**:

Back to front by z-order. Bento: large → medium → small → caption. Total entrance under 1.5s or you drag the talk.

**Avoid**:

- Parallax (keyboard paging, not scroll)
- Card hover (no one hovers in a talk)
- Looping motion (rare LED “breathing” only; else static)
- Slide / flip / cube transitions—**fade only**

## VI. Technical implementation

**Framework**: Reveal.js 5.x—keyboard, speaker notes, PDF export, fragments built in; bento layout is custom CSS Grid, not framework-dependent.

**Project structure**:

```
soundmat-deck/
├── index.html              # Main entry, all slides
├── css/
│   ├── reveal-base.css     # Reveal.js bundled
│   ├── theme-apple.css     # Custom Apple-style theme (core)
│   └── slides.css          # Per-slide layout overrides
├── fonts/                  # Local fonts (required)
│   ├── SF-Pro-Display.woff2
│   ├── Inter-*.woff2
│   └── PingFang-SC.woff2
├── images/                 # Existing project images
│   ├── hero-installation.jpg
│   ├── sensor-polar-layout.png
│   ├── pcb-perfboard.jpg
│   └── ...
└── js/
    ├── countup.js          # Number roll animation
    └── stagger.js          # Staggered card entrance
```

**Technical notes**:

1. **Local fonts** — All `.woff2` under `fonts/`, `@font-face` in CSS. **No** Google Fonts CDN; demo Wi‑Fi may fail.
2. **Image preload** — On slide 1, preload all images to avoid flashes later.
3. **Bento via CSS Grid** — `grid-template-columns: repeat(12, 1fr)` plus per-card `grid-column` / `grid-row` span. Not flexbox hacks.
4. **CSS @keyframes + JS class toggle** — Reveal fires classes on slide enter; no Framer Motion / GSAP required.
5. **Viewport scaling** — Sizes in `vw` or `clamp()` for projector resolution drift.

## VII. Content inventory

Assets you can use directly (from project docs):

- Installation renders (Gemini + ChatGPT-edited pair)
- Sensor polar design (`stitched-side-by-side.png`)
- Electronics architecture (four module diagrams)
- Perfboard layout photo
- PD trigger / buck converter photos
- Schematics (sandwich structure, ghost path parsing, etc.)
- BOM
- Key numbers (224 zones, 32 slices, 8 rings, 921600 baud, 20Hz, 108 LEDs, etc.)

**Worth adding if possible**:

- Final installation photo (stones on mat, LEDs on, top-down)—the hero “face”
- After live demo is ready, a ~5s video clip for hero background motion

**Per your constraint**: no new graphics. Existing assets are enough.

## VIII. Motion + pacing rules

The deck “breathes” through hero / bento alternation:

- Two bentos in a row tires the audience—insert hero or zoom between
- Two heroes in a row feels thin—insert bento between
- Each module (sensor / electronics / software) should open with a “announcement”—hero or zoom, not straight into bento

**Speaking time**:

- Hero: 5–30s (one line, move on)
- Bento: 45–90s (~10–15s per card)
- Zoom: 20–60s

**Speaker notes**: In Reveal’s notes per slide—what to emphasize, what to skip, approximate time. Example:

> Slide 5 - Sensor (60s)
>
> - Focus: why polar coordinates—the design reasoning
> - Wow number: 224 zones
> - Don’t expand: ghost path in depth (one sentence max)

## IX. Fallback plan

**Must do**:

1. **PDF export** — Reveal `?print-pdf`, Chrome print to PDF. Last resort if the browser misbehaves.
2. **Offline test** — Copy the whole project to a USB stick, run on another machine with no network; confirm fonts, images, animations are local.
3. **Room rehearsal** — At least one day early in the demo room with the same laptop and projector; check resolution, type size, color on the wall.
4. **Minimal keyboard** — Space to advance, arrows to change slide, Esc for overview. No custom shortcuts—you’ll mis-press under stress.

**Contingency**:

- Web deck fails on demo day → switch to PDF
- Animation stutters → `data-transition="none"` per slide in Reveal
- Short on time → skip slide 7 (Firmware) and slide 12 (Challenges); protect the live demo

## X. Deliverables

Final handoff:

1. `index.html` + CSS + JS + fonts + images — complete web slide deck
2. `soundmat-deck.pdf` — exported PDF backup
3. `speaker-notes.md` — per-slide outline (print or second screen)
4. `README-demo.md` — field guide (launch browser, F11 fullscreen, keys, what to do when things break)
