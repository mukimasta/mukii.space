---
title: "SoundMat (16) Software Deployment Performance Optimization"
docLang: en
translationKey: soundmat-16-software-deployment-performance
alternates:
  zh: /soundmat/soundmat-16-software-deployment-performance/
  en: /soundmat/en/soundmat-16-software-deployment-performance/
aliases:
  - /soundmat/en/soundmat-16-software-deployment-performance/
---




## Background

On a Pi 4 in Jam mock mode with 50 stones and playback running, scsynth sat at 99.9% and the jam loop at ~90%, with continuous JACK XRuns and audio stuttering to the point of being unlistenable. The same scenario on a Mac was fine (roughly 5–10× CPU headroom). Goal: stable performance on the Pi with anywhere from 10 to 50 stones.

---

## Optimization checklist (by layer)

### A. Frontend (mat.html)

| Change | File | Benefit |
|------|------|------|
| **Pi mode toggle** | `web/static/mat.html` | Heatmap 30 fps → 10 fps (numbers kept); LED 40 fps → 20 fps, SVG `feGaussianBlur` glow off; button + `localStorage` persistence |

> Enable when viewing `/mat` in Chromium on the Pi itself—saves ~50% GPU/CPU in the browser.
> Remote access or not opening the mat page: zero impact.

---

### B. Jam main loop (Python)

| Change | File | Benefit |
|------|------|------|
| **LOOP_HZ 200 → 60** | `jam/app.py`, `jam/bridge/master_fx.py` (α recalc) | Jam-loop CPU drops ~60% directly; Lo-Fi smoothing coefficients adjusted to keep the same feel |
| **`emit_sweep` inverted index** | `jam/event/event_engine.py` | Maintain `merged_sector → set[(ring, slc)]` incrementally; each frame only test scan-arc crossings for **sectors that have stones**; O(N) → O(crossed sectors) |
| **LED markers inverted index** | `jam/led/renderer.py` | One pass builds `led_idx → [ring]`; each stone affects only ±1 (3 LEDs total); O(108×N) → O(N) |

> Verified with micro-bench: 30 stones 1.0 ms/frame → 0.21 ms (×4.6), 50 stones 1.6 ms → 0.27 ms (×6.0).
> `emit_sweep` hit set + LED buffer **byte-identical** to the old implementation (300 frames × 5 scales all pass).

---

### C. SuperCollider (equivalent timbre)

| Change | File | Benefit |
|------|------|------|
| **Reverb send / shared reverb** | `sc/synthdefs/jam/reverb_bus.scd` (new) + `marimba.scd` send change | Each marimba voice used its own reverb (4 CombC + 3 Allpass + 2 LPF ≈ 17 UGens); 50 voices = 50 copies → one shared reverb bus. **Per-voice CPU −45%**. Sonically equivalent (standard send/return practice) |
| **chord_pad multi-frequency merge** | `sc/synthdefs/jam/chord_pad.scd` → `freq0..freq4` five channels; `SynthBridge.handle_chord` fires one synth | Was five SynthDef instances per chord (each running envelope/LPF/vibrato); now one instance with `Mix.fill(5, ...)` internally; **×0.2** SynthDef instances per chord |
| **scsynth `-z` parameterized** | `core/sc_server.py` adds `-z $SC_BLOCK_SIZE`; `config.SC_BLOCK_SIZE` (env `SOUNDMAT_BLOCK_SIZE`) | Tunable block size (**default still 64**; the old “align JACK period with 4096” idea is withdrawn—see section E) |

---

### D. Voice management

| Change | File | Benefit |
|------|------|------|
| **Polyphony cap + voice stealing** | `jam/bridge/synth_bridge.py` + `config.JAM_MAX_MELODIC_VOICES = 12` | When alive melody/bass voices exceed cap, free oldest → hard ceiling on scsynth load. On Pi 4, cap=12 brings scsynth from 99.9% → 87% with 50 stones |
| **Per-instrument `done_at` estimate** | Same | `done_at` from real envelope length per SynthDef (marimba fixed 2.012 s; rhodes/pad_pluck etc. = `sustain + release`); cap triggers skip `/n_free` for voices already naturally done—eliminates most server warnings |
| **Web tunable** | `app.py.set_param("jam_max_melodic_voices")` + `mat.html` Calibration `Max voices` | Live adjustment; 0 = unlimited |

---

### E. Profile-driven second pass (after A–D, targeted via cProfile)

After A–D, cProfile on jam-loop showed:

```
ncalls    cumtime   percall   function
2444      4.679s    1.92ms    JamApp._tick
2444      3.082s    1.26ms    JamApp._render_led
2444      2.972s    1.22ms    JamLedRenderer.render
```

**`_render_led` is 65.9% of `_tick`**; 96.4% of that is the 108-LED loop body in `JamLedRenderer.render`. `emit_sweep` / `SensorState.update` never hit the top 40 (section B inverted indexes flattened those). Conclusion: remaining jam-loop bottleneck is LED synthesis, not the event layer.

| Change | File | Benefit |
|------|------|------|
| **LED render 60 Hz → 30 Hz throttle** | `jam/app.py` (`LED_HZ = 30.0` + gate at `_render_led` entry) | Physical strip at 30 Hz is already above perception; `on_scan_hit` / `on_preview` still inject every frame—only skip 108-LED compose + serial write. **Jam-loop at 50 stones: 80% → 60% (measured)** |
| **Withdraw `-z 4096`** | `config.py` default stays 64; `SETUP.md` drops Pi 4096 recommendation | `-z` is also the step size for `EnvGen.kr` / `Lag.kr` / LFOs. `-z 4096` ≈ 93 ms kr steps—drum attacks (10–30 ms) collapse to 1–2 samples → stairsteps / mush. CPU “savings” are just fewer inner ticks; DSP work unchanged—a bad trade. **`-p` and `-z` are decoupled**: `-p` = latency, `-z` = kr precision |

> Conclusion: keep `SOUNDMAT_BLOCK_SIZE` at default 64. If CPU is still tight, prefer section D voice cap, then consider raising `-p`.

---

## Performance ledger (Pi 4 + JACK `-p2048`)

| Scenario | Before (initial) | After A–D | After A–E (current) |
|------|--------------|--------|------------------|
| **Empty mat** | scsynth ~3% / jam-loop **86%** | scsynth ~3% / jam ~30% | — |
| **10 stones, normal** | scsynth ~50% / jam ~60% (estimated) | scsynth 52% / jam 54% | — |
| **50 stones, stress** | scsynth **99.9%** / jam 82%, continuous XRun | scsynth 87% / jam 80%, occasional XRun | **scsynth 79% / jam-loop 60%**, fewer XRuns |

> 50-stone measurement (`top` screenshot): `scsynth 79.1%` / main thread `soundmat 59.8%` + worker `20.9%` (uvicorn / led-writer).
> From initial 99.9% / 90% to 79% / 60%: scsynth has ~21% headroom, jam-loop ~40%.
> XRun trend: initial “constant” → after A–D “occasional” → after E “rare”. Spikes can still trigger XRun—accepted as “a kind of lo-fi.” `/n_free Node not found` warnings are rare and harmless.

---

## Tunable parameters

### Environment variables

| Variable | Default | Pi recommendation | Notes |
|------|------|---------|------|
| `SOUNDMAT_SAMPLE_RATE` | `44100` | 44100 | scsynth `-S` |
| `SOUNDMAT_BLOCK_SIZE` | `64` | **`64`** (keep default) | scsynth `-z`, kr UGen step size. **Do not** inflate to “match JACK period”—drum attacks stairstep (see section E). |

### Web console (Mat page Calibration)

- `Max voices` — polyphony cap (0 = unlimited; Pi recommends **12**, very dense mats 8–10)
- `Sector / LED offset`, `Threshold`, Lo-Fi sum min/max, `Control sum min` — calibration
- Top bar `Pi mode` — browser frame-rate reduction (only when using a browser on the Pi itself)

### JACK (Pi deployment)

`-p` controls latency + XRun tolerance; `-z` (`SOUNDMAT_BLOCK_SIZE`) controls kr precision—**decoupled**:

```bash
jackd -P75 -t2000 -dalsa -dhw:Audio -r44100 -p2048 -n2
# SOUNDMAT_BLOCK_SIZE stays default 64; no export needed
```

`-p` tuning (@44.1 kHz):

- `-p 1024` (23 ms latency): best responsiveness; 50 stones may XRun
- **`-p 2048` (46 ms): current recommended starting point**—more scheduling margin; 1–2 m to the mat, latency is inaudible
- `-p 4096` (93 ms): only if 2048 still XRuns constantly—stone hit to sound feels noticeably late

CPU pressure priority (by payoff):

1. Lower `Max voices` (Web Calibration; Pi 12, dense 8–10)
2. Close Chromium on the Pi / don’t open `/mat` (remote access unaffected)
3. Raise `-p` to 4096 (last resort—hurts immediacy)
