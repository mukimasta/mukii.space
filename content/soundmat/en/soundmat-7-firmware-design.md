---
title: "SoundMat (7) Firmware Design"
docLang: en
translationKey: soundmat-7-firmware-design
alternates:
  zh: /soundmat/soundmat-7-firmware-design/
  en: /soundmat/en/soundmat-7-firmware-design/
aliases:
  - /soundmat/en/soundmat-7-firmware-design/
---

Firmware here means software on the ESP32 MCU. It bridges sensor/electronics and sonification: raw sensor readings go to the host computer for music generation; LED commands from the host drive the strip on SoundMat.

Firmware architecture splits into four modules:

```c
loop() {
  scan_sensors();      // Sensor scan module
  send_sensor_data();  // Sensor data transmit module
  receive_led_data();  // LED data receive module
  update_leds();       // LED refresh module
}
```

```
Initialization (pins, ADC, Serial, LEDs)

Main loop:
  1. Scan sensor array → pressure_matrix[ring][slice]
  2. Send pressure_matrix to host
  3. Receive LED state from host
  4. Update LED display
```


## Sensor scan module

Detection principles are in [SoundMat (5) Sensor Principles and Design](/soundmat/en/soundmat-5-sensor-principles-and-design/). To read coordinate `(ring, slice)`, drive the active ring HIGH and all others LOW, configure the MUX to route that slice, then read slice-side voltage.

Decisions:

1. ADC can be averaged over multiple samples for noise reduction; for now we use a **single sample** per cell and results are acceptable.

Pseudocode:

```c
scan_sensors() {
    // Clear pressure matrix; -1 = not sampled
    for all [ring][slice] {
        pressure[ring][slice] = -1
	}

    for ring in 0..NUM_RINGS-1 {
        // Activate current ring, others LOW (prevent ghost paths)
        set_all_rings(LOW)
        set_ring(ring, HIGH)
        delay_ms(RING_SETTLE_MS)  // Wait for ring line to settle

        for slice in 0..NUM_SLICES-1 {
            // Set MUX address lines for current slice channel
            mux_select(slice)
            delay_ms(MUX_SETTLE_MS)  // Wait for MUX to settle

            // Read ADC
            raw = adc_read(SIG_PIN)
			pressure[ring][slice] = raw
		}
        // Done with this ring; drive LOW before next ring
        set_ring(ring, LOW)
	}
	return pressure
}
```

We use **CD4067B**; enable is **active low**.


## Serial data module

The ESP32 sends raw ADC values to the host (no calibration on-device). The host sends per-LED control data.

### Basic settings

| Item | Setting |
| --- | ---------- |
| Baud rate | 921600 |
| Encoding | ASCII text |

### Frame format

All frames share:

```
TYPE:PAYLOAD*XX\n
```

| Field | Description |
| --------- | ------------ |
| `TYPE` | Single-character frame type |
| `:` | Separator |
| `PAYLOAD` | Payload; format depends on type |
| `*` | Checksum separator |
| `XX` | 2-digit hex checksum |
| `\n` | Frame terminator |

**Checksum:** XOR all bytes from `TYPE` through the character before `*` (inclusive of `TYPE` and `:`). Encode result as 2 uppercase hex digits.

### Frame types

| Direction | Header | Purpose |
|---|---|---|
| ESP32 → Pi | `S` | Sensor data |
| Pi → ESP32 | `L` | LED control |
| Both | `#` | Comment/debug (receiver ignores) |

#### S frame: sensor data (ESP32 → Pi)

```
S:v0,v1,v2,...,v255*XX\n
```

256 decimal integers, comma-separated, range **-1–4095** (12-bit ADC raw; **-1** = invalid). **Ring-major** order:

```
index = ring × 32 + slice
```

Indices 0–31 are Ring 0 slices 0–31; 32–63 Ring 1; and so on. Inner rings 0–1 have only 16 physical zones but still send 32 values; merging is done on the Pi.

**Frame size:** ~1.2 KB (≈3–4 chars per value + commas + header/footer).

**Example:**

```
S:4095,4093,4090,2031,...,3500,3498*A7\n
```

#### L frame: LED control (Pi → ESP32)

```
L:RRGGBB,RRGGBB,...,RRGGBB*XX\n
```

108 six-digit hex RGB values, comma-separated, in physical strip order (index 0 = first LED).

**Frame size:** ~760 bytes.

**Example:**

```
L:000000,0A0500,1A0F00,...,000000*3E\n
```

Value range 0–4095 (ESP32 12-bit ADC raw). Inner rings 0–1 have 16 effective zones but still send 32 values (adjacent slices may cover the same physical region); merge logic stays on the Pi so firmware stays simple.

#### # frame: debug (bidirectional)

```
# any text\n
```

Lines starting with `#` have no checksum; discard or log. On boot the ESP32 may send:

```
# SoundMat firmware v1.0 ready\n
```

#### Timing

Both sides send asynchronously without blocking.

After each scan the ESP32 sends an S frame without waiting for the Pi. The Pi computes audio/LED asynchronously and sends L frames when ready. Each loop iteration the ESP32 **non-blocking** checks Serial; a complete L frame updates the LED buffer, otherwise the previous frame persists.

Right after USB connect, during ESP32 boot, LED commands are ineffective—wait until the link is stable before relying on traffic.

> **Claude:**
>
> #### Robustness and engineering constraints
>
> **Buffer sizing:** ESP32 Serial RX buffer must be **2048** bytes (default 256 cannot hold a full ~760-byte L frame). Pi `pyserial` default RX is sufficient.
>
> **Partial frames:** Read strictly by line. Process only after `\n`; leave incomplete data in the buffer for the next loop.
>
> **Checksum failures:** Drop the frame; no retry. For ambient music, losing one frame is imperceptible; retries add latency and complexity—not worth it for this prototype.
>
> **Frame-rate budget:** 921600 baud ≈ 92 KB/s. Full duplex ~2 KB/frame → theoretical ~46 fps. With scan + processing overhead, expect **20–30 fps**, ample for responsive ambient music.


### LED refresh module

Write RGB values from the LED buffer to the WS2812B strip.

**Driver:** WS2812B needs an 800 kHz one-wire protocol. We use ESP-IDF `led_strip.h`, which uses the **RMT** peripheral for timing.


## ESP32 program layout

```
firmware/
├── main/
│   ├── main.c
│   ├── config.h
│   ├── sensor.h / sensor.c
│   ├── serial_comm.h / serial_comm.c
│   └── led_ctrl.h / led_ctrl.c
```

```c
// ========== Variables ==========
pressure_matrix[NUM_RINGS][NUM_SLICES]
led_buffer[NUM_LEDS]

app_main():
	// ========== Initialization ==========
	serial_init()
	uart_write("# SoundMat firmware v1.0 booting\n")
	sensor_init()
	led_init()
	uart_write("# init complete, entering main loop\n")
	
	while true:
		sensor_scan()
		serial_send_sensor_data(pressure_matrix)
		serial_try_receive_led_data(led_buffer) // non-blocking
		led_update()
		vTaskDelay(pdMS_TO_TICKS(LOOP_DELAY_MS)) // feed watchdog
	
```


## Constant table

| Constant | Value | Meaning |
| ------------------ | ------ | -------------------------- |
| `NUM_RINGS` | 8 | Ring electrode count |
| `NUM_SLICES` | 32 | Slice electrode count |
| `NUM_LEDS` | 108 | LED count |
| `ADC_SAMPLES` | 1 | Samples per point for averaging; 1 = single sample |
| `ADC_BIT` | 12 | ADC resolution (bits) |
| `UART_BAUD` | 921600 | Serial baud rate |
| `UART_RX_BUF_SIZE` | 2048 | RX buffer; must fit full L frame |
| `UART_TX_BUF_SIZE` | 0 | TX buffer; blocking send for complete frames |
| `RING_SETTLE_US` | 20 | Delay after ring select (µs) |
| `MUX_SETTLE_US` | 50 | Delay after MUX address change (µs) |
| `LOOP_DELAY_MS` | 1 | Min delay at end of main loop; watchdog + yield CPU |
| `LED_COLOR_ORDER` | GRB | WS2812B color order |


## Latency analysis



## Pin map

Pin assignments match [SoundMat (11) Electronics Manufacturing](/soundmat/en/soundmat-11-electronics-manufacturing/).

**Rings**

| Ring  | MCU IO |
| ----- | ------ |
| Ring0 | D19    |
| Ring1 | D5     |
| Ring2 | D21    |
| Ring3 | TX2    |
| Ring4 | D22    |
| Ring5 | D4     |
| Ring6 | D23    |
| Ring7 | D2     |

**MUX**

| Slice       | MUX PINS      |     |
| ----------- | ------------- | --- |
| Slice 0-15  | MUX 0, C0-C15 |     |
| Slice 16-31 | MUX 1, C0-C15 |     |

| MUX PINS | MCU IO | TYPE   |
| -------- | ------ | ------ |
| S0       | D26    | OUTPUT |
| S1       | D25    | OUTPUT |
| S2       | D33    | OUTPUT |
| S3       | D32    | OUTPUT |
| EN0      | D14    | OUTPUT |
| EN1      | D27    | OUTPUT |
| **SIG**  | VP     | INPUT  |

**LED**

| PINS    | MCU IO |     |
| ------- | ------ | --- |
| LED DIN | D13    |     |
