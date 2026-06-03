---
title: "SoundMat (12) Software Design and Development"
docLang: en
translationKey: soundmat-12-software-design-and-development
alternates:
  zh: /soundmat/soundmat-12-software-design-and-development/
  en: /soundmat/en/soundmat-12-software-design-and-development/
aliases:
  - /soundmat/en/soundmat-12-software-design-and-development/
---




This document describes the host-software layer design and development for SoundMat. Hardware, electronics, sensor principles, ESP32 firmware, and related topics are covered in their own design docs. Here we assume hardware already delivers sensor frames over serial and focus on the Python program and SuperCollider audio engine running on the Raspberry Pi.

---

## 1. Runtime platform

The SoundMat host runs on a **Raspberry Pi 3B V1.2** with **Raspberry Pi OS Lite** (no desktop). Reasons for this stack:

- **Enough performance**. Pi 3B’s quad-core 1.2 GHz Cortex-A53 and 1 GB RAM can run the Python music logic and SuperCollider synthesis together.
- **Full I/O**. Four USB-A ports: ESP32 (serial), USB DAC (audio out), debug USB stick; Ethernet/Wi‑Fi for dev-time SSH and Web console.
- **Small and low power**. Fits inside the enclosure cavity; see the electronics design doc.
- **Mature stack**. Linux + Python + SuperCollider is a proven real-time audio combination.

Pi OS Lite frees background resources for audio. No GUI at runtime—all interaction is SSH or the Web console.

**Dev machine**: Same stack runs on macOS (`uv run soundmat`); `SOUNDMAT_SCSYNTH` overrides the scsynth path; on Mac the serial device is `/dev/cu.usbserial-*`. Deployment target remains Pi + USB DAC.

---

## 2. System overview

End-to-end data flow:

```
                                                    +-----------+
   +-------+   serial    +-----------+    OSC       |  scsynth  |
   | ESP32 |  ---------> |    Pi     |  ----------> |    (SC)   | 
   |       |   S frames  |  Python   |             |           |
   |       |  <--------- |           |        +-----+-----------+
   +-------+   L frames  +-----------+        +-> USB DAC --> speakers
       ↓
   LED strip
```

Steps:

1. **Sensor ingest**. The Pi receives S frames from the ESP32 over USB serial (256× 12-bit ADC values per frame, ~20–30 fps).
2. **Parsing**. Python turns the raw ADC matrix into a snapshot of which `(ring, slice)` cells have objects, then edge events such as place / lift.
3. **Music logic**. From sensor state and events, the logic layer decides what to play and which parameters to change. It does not output audio directly—only abstract music events.
4. **Synthesis**. Events become OSC messages to SuperCollider’s scsynth, which instantiates SynthDefs, synthesizes or plays samples, and outputs via USB DAC to external speakers.
5. **LED reverse path**. Python also builds LED color buffers from state, encodes L frames on the same serial link back to the ESP32, which drives WS2812B strips.

---

## 3. Audio engine: SuperCollider

SoundMat uses **SuperCollider** (SC)—an open real-time synthesis and algorithmic composition platform (James McCartney, 1996). Two processes:

- **scsynth**: synthesis server; OSC in, real-time audio out; hundreds of voices are feasible.
- **sclang**: SC language interpreter; defines SynthDefs, music logic, sends OSC to scsynth.

Why SC:

- **Strong real-time behavior**. scsynth is built for low-latency audio with low CPU use.
- **Samples and synthesis**. Long ambient samples and complex Jam synths both fit.
- **Native OSC**. Natural fit for driving from another language.
- **Cross-platform**. Good Linux ARM support; headless on the Pi.

---

## 4. Audio engine software architecture

### Design intent

Logic is Python’s strength; audio is SuperCollider’s. **Keep logic in Python where possible**—but that does not mean micromanaging SC from Python. Abstract well on the SC side so Python gets “sound building blocks,” not raw audio plumbing.

### Python ↔ SC integration options

| Approach | Description | Assessment |
|---|---|---|
| **Hand-written OSC** | Python sends `/s_new`, `/n_set`, etc. via `python-osc` | Flexible but verbose; node IDs and params are manual |
| **subprocess + sclang** | Python spawns sclang, text interface | Indirect, slow, brittle |
| **python supercollider library** | Library API over scsynth; OSC inside | Right abstraction level, readable |

We use the third: the **python supercollider** library. It wraps scsynth nodes, SynthDefs, buffers, etc.—higher than raw OSC, more direct than a sclang subprocess.

### sclang vs scsynth

- **sclang**: interpreter for SC language.
- **scsynth**: server that actually synthesizes.

Normally sclang compiles logic to OSC for scsynth. We can skip sclang at runtime and drive scsynth from Python because the link is OSC.

### Our architecture

```
[ Past: pure SuperCollider ]
Music logic (sclang) ──> instantiate SC Synth classes ──> drive scsynth nodes
                                ▼
                      [SynthDefs defined in sclang]


[ Now: Python + supercollider library + SC ]
Music logic (python) ──> library Synth classes ──> drive scsynth nodes
                                ▼                          ▼
                    [Python-side mirror classes]    [precompiled SynthDefs]
                                                           ▼
                                              [SynthDefs authored in sclang]
```

In short:

- **SC side**: SynthDefs still written in sclang, **precompiled to `.scsyndef`**; no sclang at runtime.
- **Python side**: library instantiates synths, sets params, starts/stops nodes; OSC to scsynth internally.
- **scsynth**: standalone service loading all `.scsyndef`, waiting for Python commands.

Benefit: **all music logic in Python** (data structures, yaml/toml, HTTP, web frameworks); **all sound from scsynth** with stable performance. Clear boundary: **Python decides when and what; SC decides how it sounds.**

Workflow: author SynthDefs → compile to `.scsyndef` → Python logic controls playback.

---

## 5. Detailed software architecture

### 5.1 Overall design

SoundMat has two playback modes:

- **Ambient**: environmental music for public installation (e.g. Kyoto Arashiyama theme)
- **Jam**: beat-driven lo-fi loop music

They look very different but share the same hardware (Pi, ESP32, USB DAC, LEDs) and one SC server. The architecture balances “each mode does what comes naturally” with “no duplicate shared resources.”

Only **hardware I/O and the SC server** are truly shared; music logic differs. We do not force one abstract “music engine”—two apps on shared `core/` services, with `ambient/` and `jam/` evolving independently.

The main program picks a mode from a manifest. One mode is active at a time; switching via the Web console without restart.

### 5.2 Ambient mode

For public installation: users place stones on the circular mat; the system generates ambient music in real time. Main loop ~20 Hz.

**Core pipeline**:

```
sensor → tracker → state → mapper → voices → engine → scsynth
```

In one line: **sensor reads stones on the mat → state computes frame deltas → mapper decides what should sound → voices diff frames and execute → engine drives scsynth via OSC**.

**Hybrid interaction model**:

- **Sustained sounds** (wind, stream, pad, etc.): **state reconcile**—mapper each frame outputs the desired set; the voices engine diffs and starts/stops voices to follow state.
- **Triggered sounds** (bells, one-shots): **event-driven**—only on place/lift edges.

**Strict separation**:

- `mapping.py`: pure “music brain”; declarations only, no OSC.
- `voices.py`: reconcile engine syncing declarations to scsynth node state.

Samples organized by ring (bass, mid, bamboo, weather, melody, events, etc.), assembled declaratively via manifest (e.g. `kyoto.toml`). SynthDefs compiled offline to `.scsyndef`; runtime loads binaries only. FX chain fixed: `sources → reverb → master`.

Modules are **flat files** (not subpackages): `tracker.py`, `state.py`, `mapping.py`, `voices.py`, `buffers.py`, `led.py`.

### 5.3 Jam mode

One sentence: **separate “what” (music content) from “how” (execution)**. Replaceable pieces are declarative config; code only schedules and interprets. New song = new data, code unchanged.

Five layers:

```
config → theory → scheduler → events → bridge → SC
```

- **Config**: BPM, key, scale, progression, melody tables, drum patterns, ring config, lo-fi curves—YAML/TOML.
- **Theory**: `DegreeParser` ("1#^"), `Tonality` (degrees → MIDI), `Tempo` (BPM → time constants).
- **Scheduler**: `Transport`, `ScanLine`, `SongPositionTracker`.
- **Events**: `HarmonyEngine`, `DrumEngine`, `EventEngine`; `SensorState` for wire→logic coords, occupied/placed/removed, R0/R1 lo-fi and control-stone active.
- **Bridge**: `NoteEvent` → OSC; ring→instrument mapping; degrees → MIDI.

**Tuning knobs**:

- **BPM**: all timing from BPM; SC only sees absolute seconds.
- **Key**: config uses degrees ("1#^", "6_"); `Tonality` maps at runtime. Change `key: "G"` to transpose.
- **Timbre**: ring→SynthDef mapping is separate config.
- **Structure**: progressions, melodies, drums are YAML—swap data to swap song.

**Example path** for one note: BPM=120, key=C, chord 2m9, scan line at slice 4, stone on R4 slice 4:

| Layer | What it holds |
|---|---|
| Config | `"2"` (string in melody table) |
| Scheduler | `slice=4` (no pitch knowledge) |
| Events | `NoteEvent(ring=4, degree="2", ...)` |
| Bridge | `parsed=(2,0,0)` → `midi=62` → `freq=293.66` |
| SC | `freq=293.66 Hz` (no name for "2", "D", or key) |

**Concrete pitch exists only at the bridge for an instant**—hence changing `key: "G"` does not touch config or the event stream.

---

### 5.4 Directory structure

```
soundmat/                                ─── repo root (src/soundmat/) ───
├── README.md
├── SETUP.md                             # deploy and calibration on device
├── pyproject.toml
├── uv.lock
│
├── manifest/
│   ├── ambient/
│   │   └── kyoto.toml
│   └── jam/
│       ├── lofi_1.toml                  # default startup manifest
│       ├── lofi_1b.toml
│       └── data/
│           ├── progressions/
│           ├── melodies/
│           ├── drums/
│           ├── rings/
│           │   └── lofi.yaml
│           └── lofi_mapping.yaml
│
├── soundmat/                            ─── Python package ───
│   ├── __init__.py
│   ├── __main__.py                      # CLI entry; start scsynth / serial / Web
│   ├── config.py                        # globals (calibration defaults, buses, Jam behavior)
│   ├── app.py                           # ModeManager + manifest load
│   │
│   ├── core/
│   │   ├── sc_server.py                 # scsynth subprocess + .scsyndef load
│   │   ├── osc.py                       # OSC client (node IDs from 100000)
│   │   ├── esp32_serial.py              # serial auto-detect, open, boot wait
│   │   ├── services.py                  # SharedServices
│   │   ├── sensor/
│   │   │   ├── reader.py                # SensorReader abstract + subscribe
│   │   │   ├── serial_reader.py         # ESP32 S-frame read
│   │   │   ├── mock_reader.py           # mock / .npz replay / Web mat inject
│   │   │   ├── frame.py                 # S-frame parse + checksum
│   │   │   ├── map.py                   # wire → logical (ring, sector) S→L
│   │   │   └── normalize.py             # wire slice column mirror (deploy tunable)
│   │   └── led/
│   │       ├── writer.py                # L-frame encode + 60 Hz send
│   │       └── offset.py                # physical LED rotation
│   │
│   ├── web/
│   │   ├── server.py                    # FastAPI: HTTP + WebSocket
│   │   └── static/
│   │       ├── index.html               # Control: mode, volume, BPM
│   │       ├── mat.html                 # Mat: heatmap, virtual mat, calibration
│   │       ├── debug.html
│   │       └── soundmat.css
│   │
│   ├── modes/
│   │   └── base.py                      # ModeApp Protocol
│   │
│   ├── ambient/
│   │   ├── app.py
│   │   ├── tracker.py
│   │   ├── state.py
│   │   ├── mapping.py
│   │   ├── voices.py
│   │   ├── buffers.py
│   │   └── led.py
│   │
│   └── jam/
│       ├── app.py                       # ~200 Hz main loop
│       ├── types.py
│       ├── config_loader.py
│       ├── ring_config.py
│       ├── theory/                      # degree, tonality, tempo
│       ├── scheduler/                   # transport, scanline, song_position, timing
│       ├── event/                       # sensor_state, harmony/drum/event_engine
│       ├── bridge/                      # synth_bridge, master_fx
│       └── led/                         # renderer, layers (palette / geometry / envelopes)
│
├── sc/
│   ├── synthdefs/
│   │   ├── core/                        # master, reverb, players
│   │   ├── ambient/                     # diapason, marimba
│   │   └── jam/
│   │       ├── 00_common.scd            # shared UGen helpers
│   │       ├── master.scd               # jam_master (three buses + Lo-Fi)
│   │       ├── sub_bass.scd, pluck_bass.scd, pad_pluck.scd, rhodes.scd, marimba.scd
│   │       ├── chord_pad.scd
│   │       └── drums/                   # kick, snare, hihat
│   ├── assets/samples/
│   ├── compiled/                        # *.scsyndef
│   └── compile.scd
│
├── scripts/
│   ├── compile_synths.py
│   └── replay_test.py
│
└── tests/                               # pytest (sensor_map, led, integration, …)
```

### 5.5 Key files

**`jam/types.py`** — Contract types: `NoteEvent`, `ChordEvent`, `ParamEvent`, `SliceTick`, `SongPosition`, etc. `NoteEvent` includes `source_slice` (LED hit flash), `when` (reserved); harmony uses `ChordEvent`, not `NoteEvent`.

**`core/sensor/map.py` + `normalize.py`** — S frames use wire `(ring, slice)`; optional column mirror + `SECTOR_OFFSET` → logical `(ring, sector)` (always 32 sectors). Inner R0/R1 map 16 active wire slices at pre-offset layer. Jam `SensorState` and Ambient `Tracker` threshold on logical coordinates.

**`core/sensor/reader.py` vs `serial_reader.py` / `mock_reader.py`** — Abstract interface + real serial / mock. `_emit()` applies wire mirror uniformly. Mode apps only use `latest()` / `subscribe()`.

**`core/esp32_serial.py`** — `pick_serial_port("auto")`, open at 921600, wait for first S frame on boot (8s).

**`config.py`** — Deploy defaults: `SENSOR_THRESHOLD=500`, `CONTROL_SUM_MIN=250`, `CONTROL_MAX=1000` (lo-fi map ceiling), `SECTOR_OFFSET=4`, `LED_OFFSET=101`, `WIRE_SLICE_MIRROR=True`; Jam place-preview volumes `JAM_IDLE_PLACE_PREVIEW_VEL=0.5`, `JAM_LOOP_PLACE_PREVIEW_VEL=0.25` (0=off); serial lost `SERIAL_LOST_EXIT_SEC=3` then exit.

**`core/services.py`** — `SharedServices` bundles sc / sensor / leds / osc plus `serial_port`, `serial_ready`.

**`modes/base.py`** — `ModeApp` Protocol (`start` / `stop` / `status` / `set_param`).

### 5.6 Manifest references

Jam manifest is an assembly list pointing at data files:

```toml
# manifest/jam/lofi_1.toml
mode = "jam"
name = "Lo-Fi Loop · Progression 1"
description = "Kyoto night rain; 2m9 → 513 → 1maj9 → 69"

[music]
bpm = 120
key = "C"
scale = "major"

[refs]
progression = "1"      # → data/progressions/1.yaml
melody_pack = "1"      # → data/melodies/1/
drums = "lofi_loop"    # → data/drums/lofi_loop.yaml
rings = "lofi"         # → data/rings/lofi.yaml
lofi_mapping = "default"
```

Flexible: one melody pack can serve progression 1 and 1B, or stay separate. Ambient manifests likewise declare sample groups and ring mapping.

---

## 6. Web console

### 6.1 Motivation

SoundMat has no physical buttons (aesthetic choice). Dev, debug, and demo still need control: mode switch, transport, parameters. A lightweight HTTP service on the Pi—phone QR access—changes nothing on the object.

The console is also **infrastructure for the whole project**:

- Live sensor heatmap (debug essential)
- Scan line visualization
- BPM / manifest changes without restart
- Record sensor data for offline replay
- CPU and SC server monitoring

### 6.2 Pages

| Path | Page | Role |
| --- | --- | --- |
| `/` | Control (`index.html`) | Mode switch, volume, Jam BPM, place-preview slider, Developer Restart/Stop |
| `/mat` | Mat (`mat.html`) | Live heatmap, calibration, mock virtual mat and LED mirror |
| `/heatmap`, `/pad` | Same as Mat | Aliases |
| `/debug` | Debug | Debug |

**Jam transport**: playback is driven by **R0/R1 control stones** (sum of pressures ≥ `CONTROL_SUM_MIN`), not Control-page Transport. Control **Restart/Stop** only restarts/stops the **current mode thread** (see Developer section).

### 6.3 HTTP / WebSocket API

```
GET  /                          # Control home
GET  /mat                       # Mat page (heatmap + calibration)
GET  /debug

GET  /api/status                # mode status + calibration + app sub-state
GET  /api/manifests             # available manifests
POST /api/mode                  # {"manifest": "…/lofi_1.toml"}
POST /api/transport             # {"action": "start"|"stop"} mode lifecycle
POST /api/params                # global or mode params (see below)

POST /api/mock/cells            # mock mode: inject {(ring,sector),…}

WS   /api/sensor_stream         # sensor matrix ~30 fps
WS   /api/event_stream          # state snapshots ~10 Hz (debug)
WS   /api/mock/view             # mock: LED buffer + status ~40 fps
```

**`POST /api/params` global keys** (`ModeManager`, reset on restart): `sector_offset`, `led_offset`, `sensor_threshold`, `control_min`, `control_max`, `control_sum_min`, `wire_slice_mirror`, `jam_loop_place_preview_vel` (0–1, 0=off). Mode keys like `bpm`, `master_volume` forward to `ModeApp.set_param`.

### 6.4 Implementation notes

- FastAPI + uvicorn, **single file** `web/server.py` (routes + WebSocket together)
- Static HTML/JS + `soundmat.css`, no frontend framework
- Holds `ModeManager` directly
- Mat calibration for sector/LED/threshold/lo-fi/control sum (**not persisted**; restart restores `config.py` defaults)

---

## 7. Startup sequence

```
$ uv run soundmat [manifest/jam/lofi_1.toml]   # default lofi_1, not kyoto
   ↓
__main__.py:
  1. Parse CLI (--mock, --port, --no-serial, --no-web, --no-sc, --list-ports)
  2. Start scsynth (-u 57110 -i 0 -o 2 -S 44100); up to 5 retries on failure
  3. load_synthdefs(sc/compiled)
  4. Open ESP32 serial (auto), wait for first S frame (8s); on failure → mock
  5. SensorReader + LEDWriter share serial; LED sends L frames at 60 Hz
  6. SharedServices → ModeManager → switch_to(initial_manifest)
  7. Web server thread (optional)
  8. Main thread waits; serial drops while running → exit after 3s and cleanup
```

scsynth **stays up**; mode switch only frees/creates SC groups. SynthDefs load once at startup.

---

## 8. Mode switch flow

```
Browser: POST /api/mode {"manifest": "jam/lofi_1.toml"}
   ↓
ModeManager.switch_to():
  1. Acquire lock
  2. current_app.stop():
       - Stop mode main-loop thread
       - Unsubscribe SensorReader
       - Clear LEDWriter data source
       - sc.free_group(my_group)  ← free all this mode’s synth nodes at once
  3. Load new manifest
  4. Pick ModeApp class from manifest.mode (AmbientApp / JamApp)
  5. new_app = ModeAppClass(manifest, services)
  6. new_app.start():
       - sc.new_group() → own group ID
       - Start mode-specific initial synths (e.g. master FX)
       - Subscribe SensorReader
       - Register LEDWriter data source
       - Start main-loop thread
  7. current_app = new_app
  8. Release lock
```

Switch is on the order of 100–300 ms. Global crossfade between stop/start is optional; not required for prototype.

**SC group isolation** is key: each mode gets a new group; all its synths spawn under it. On stop, `n_free` the whole group—all sound stops cleanly without tracking every node ID.

---

## 9. Mode main loops

The two loops differ enough that a single abstract interface would be forced.

### Ambient main loop (20 Hz, reconcile-based)

```
loop @ 20Hz:
    frame = sensor.latest()
    occ = tracker.occupied(frame.matrix)       # logical coords + threshold
    state, events = state_model.update(occ)  # placed / removed edges
    result = mapper.map(state, events)
    voices.reconcile(result); voices.pump(t)
    leds.set_buffer(render_led(t, occ))
```

Mapper declares, voices reconcile, scsynth sounds—steady 20 Hz.

### Jam main loop (~200 Hz, continuous time + scan trigger)

Jam is **not** a unified `emit(tick)` on 16th-note grid. Actual logic:

```
loop @ ~200Hz:
    frame = sensor.latest()
    delta = sensor_state.update(frame)     # occupied/placed/removed, Lo-Fi, control_active

    master_fx.set_lofi(delta.control_value)   # R0/R1 pressure sum → 0..1000, continuous

    if not control_active:               # R0/R1 sum < CONTROL_SUM_MIN (incl. 100ms release hold)
        reset transport/scanline/event (edge); idle place preview (JAM_IDLE_PLACE_PREVIEW_VEL)
        render LED (all-ring breathe 0–20); return

    transport.start() on first control      # control stones present → start transport
    if not transport.playing:             # song end: wait until R0/R1 cleared
        render LED; return

    prev_t, curr_t = transport.advance(dt)
    harmony.emit(prev_t, curr_t) → bridge   # ChordEvent, time intervals
    drum.emit(prev_t, curr_t) → bridge      # 16th-note ticks

    prev_a, curr_a, wrap = scanline.update(curr_t)
    optional: placed preview if JAM_LOOP_PLACE_PREVIEW_VEL > 0
    notes = event_engine.emit_sweep(...)    # scan line crosses sector center → melody/bass
    bridge.handle(notes); LED scan hit / preview

    leds.set_buffer(jam_led.render(...))    # playing: scan trail + slot breathe; idle: dim breathe
```

**Control stones**: `control_active = (sum of all R0+R1 cell pressures) ≥ CONTROL_SUM_MIN`, independent of per-cell threshold. Per-cell threshold (default 500) still drives occupied/placed.

**Audio buses** (`jam_master`): melody+bass → bus 2 (gain 0.9), harmony → 4 (0.4), drums → 6 (0.62) → hardware out 0.

---

## 10. Manifest parameters

### 10.1 Common (all manifests)

| Param | Type | Description |
|---|---|---|
| `mode` | string | `"ambient"` or `"jam"` |
| `name` | string | Display name in Web console |
| `description` | string | Short blurb, optional |

### 10.2 Ambient mode parameters



### 10.3 Jam mode parameters

**`[music]` block**:

| Param | Type | Description |
|---|---|---|
| `bpm` | int | Tempo; 120 default; adjustable live in Web console |
| `key` | string | Root, e.g. `"C"`, `"G"`, `"F#"`—global transpose |
| `scale` | string | e.g. `"major"`, `"natural_minor"`, `"dorian"` |
| `master_volume` | float | Master out 0.0–1.0 |

**`[refs]` block** (paths under `data/`):

| Param | Type | Description |
|---|---|---|
| `progression` | string | `data/progressions/<name>.yaml` |
| `melody_pack` | string | `data/melodies/<name>/` |
| `drums` | string | `data/drums/<name>.yaml` |
| `rings` | string | Ring roles + timbre: `data/rings/<name>.yaml` |
| `lofi_mapping` | string | Lo-fi curve name |

### 10.4 Data file fields

**`progressions/<name>.yaml`** — chord progression:

```yaml
chords:
  - {id: "2m9",   bars: 2}
  - {id: "513",   bars: 2}
  - {id: "1maj9", bars: 2}
  - {id: "69",    bars: 2}
```

**`melodies/<name>/<chord_id>.yaml`** — melody triggers per chord:

```yaml
# degree at each of 8 eighth-note positions per ring
R7: ["3^", "1^", "2^", "3^", "3^", "2^", "1^", "6"]
R6: ["1^", "5", "6", "1^", "1^", "5", "6", "3^"]
R5: ["6", "3", "4", "6", "6", "4", "3", "2"]
R4: ["4", "3", "2", "3", "4", "3", "2", "3"]
R3: ["4_", null, "6_", null, "4_", null, "6_", null]
R2: ["2_", null, "2_", null, "2_", null, "2_", null]
```

`null` = no trigger at that position.

(Notation: X=X4, X^=X5, X_=X3, X__=X2 when 1=C)

**`drums/<name>.yaml`** — patterns and sequence:

```yaml
patterns:
  A: {kick: [...], snare: [...], hihat: [...]}    # 16 sixteenth-note slots
  B: {kick: [...], snare: [...], hihat: [...]}
  C: {kick: [...], snare: [...], hihat: [...]}
  D: {kick: [...], snare: [...], hihat: [...]}
sequence: [A, B, C, C, A, D, D, A]    # 8-pass song order
```

**`rings/<name>.yaml`** — roles + SynthDef + gate/gain (lofi excerpt):

```yaml
R0: {role: control, param: lofi_amount, range: [0, 1000]}
R1: {role: control, param: lofi_amount, range: [0, 1000]}
R2: {role: bass,   instrument: jam_sub_bass,   note_sec: 0.25, tail_sec: 0.1,  gain: 2.9}
R3: {role: bass,   instrument: jam_pluck_bass, note_sec: 0.5,  tail_sec: 0.15, gain: 3.1}
R4: {role: melody, instrument: jam_pad_pluck,  note_sec: 1.28, gain: 2.75}
R5: {role: melody, instrument: jam_rhodes,     note_sec: 0.74, gain: 3.45, params: {far: 1}}
R6: {role: melody, instrument: jam_rhodes,     note_sec: 0.82, gain: 3.45, params: {far: 0}}
R7: {role: melody, instrument: jam_marimba,    note_sec: 2.012, gain: 2.75}
```

**`lofi_mapping.yaml`** — Lo-Fi 0–1000 → `jam_master` **cutoff + drive** (piecewise linear):

```yaml
master:
  cutoff: {0: 14000, 250: 9500, 500: 6447, 750: 4376, 1000: 2425}
  drive:  {0: 0.0, 250: 0.00625, 500: 0.0125, 750: 0.01875, 1000: 0.025}
```

Formulas: `cutoff = 14000·(420/14000)^(level/2000)`, `drive = level/40000`. Harmony/drum bus gains do **not** follow lo-fi.

---

## 11. Development environment

### 11.1 Package management: uv

**uv** (Astral) for Python env and deps—much faster than pip+venv with locked dependencies.

```bash
uv sync                        # install dependencies
uv add <package>
uv run soundmat                  # default manifest/jam/lofi_1.toml
```

`uv.lock` is committed so dev machine and Pi match.

### 11.2 SC compile

SynthDefs compiled with sclang:

```bash
sclang sc/compile.scd
```

Output: `sc/compiled/`, loaded once by scsynth at runtime.

### 11.3 Offline (no hardware)

```bash
uv run soundmat --mock              # manual Web mat injection
uv run soundmat --mock recording.npz
uv run soundmat --no-sc             # no audio; logic/LED only
uv run soundmat --list-ports
```

`mock_reader` + Mat `/api/mock/cells`; `--mock` sets `WIRE_SLICE_MIRROR=False` (virtual mat is already CW slices). Serial open failure also falls back to mock.

`scripts/replay_test.py` replays recorded matrices. Web “record sensor” not implemented yet.

---

## 12. Key interfaces and protocols

### 12.1 Mode protocol

Any mode implementing these four methods works with `ModeManager`:

```python
class ModeApp(Protocol):
    def __init__(self, manifest: dict, services: SharedServices): ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def status(self) -> dict: ...
    def set_param(self, key: str, value: Any) -> None: ...
```

Duck typing, not a strict ABC.

### 12.2 SharedServices

```python
@dataclass
class SharedServices:
    sc: SCServerHandle
    sensor: SensorReader
    leds: LEDWriter
    osc: OSCClient
    serial_port: str | None = None
    serial_ready: bool = False
```

### 12.3 Jam core event types

```python
@dataclass
class NoteEvent:
    ring: int
    degree: str | None = None
    voice: str | None = None       # drums: kick/snare/hihat
    velocity: float = 1.0
    sustain: float = 0.5           # seconds
    pan: float = 0.0
    when: float = 0.0
    source_slice: int | None = None  # for LED


@dataclass
class ChordEvent:
    symbol: str
    degrees: tuple[str, ...]
    hold: float
    release_first: bool = True


@dataclass
class ParamEvent:
    param: str
    value: float


@dataclass
class SliceTick:
    slice: int
    timestamp: float
    did_wrap: bool = False


@dataclass
class SongPosition:
    chord_idx: int
    bar: int
    sub_loop: int
    bar_global: int = 0
```

---

## 13. Implementation status (vs. this doc’s first draft)

Mostly shipped: full `core/`, `ambient/`, `jam/`, Web Control+Mat, `ModeManager` switching, Jam LED scan/breath/preview, S→L calibration, control-stone sum + release hold, place preview, serial disconnect 3s exit, scsynth start retry.

Still open or optional: sensor recording, Ambient on-device sample integrity checks, crossfade on mode switch, richer Debug event stream.

On-device setup and calibration: repo **`SETUP.md`**.
