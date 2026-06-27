# Getting Started

A full walkthrough for building a Tesla light show from scratch.

## 1. Install the tools

- **xLights** — the sequencer used to design the show. Download the latest from
  <https://xlights.org/releases/>. (If a new xLights export ever fails to load in
  the car, an older build is at <https://github.com/smeighan/xLights/releases>.)
- **Python 3.7+** — already on macOS; used to run the validator.

## 2. Start from Tesla's template

Tesla ships a pre-built xLights project that already contains the car "model"
(every controllable light and closure mapped to a channel) plus a sample audio track.

1. Download `tesla_xlights_show_folder.zip` from
   <https://github.com/teslamotors/light-show>.
2. Unzip it into a new folder under [`../shows/`](../shows/), e.g. `shows/my-first-show/`.
3. Open the `.xsq` file in xLights.

> Keep the template's models/layout intact — that mapping is what makes the
> exported sequence line up with the real car. See
> [channel-reference.md](channel-reference.md) for what each channel drives.

## 3. Design the show

- Drop your music onto the timeline (44.1 kHz `.mp3` or `.wav`).
- Use xLights effects on each model element (headlights, turn signals, fog lights,
  side markers, mirrors, windows, charge port, liftgate, falcon doors, etc.).
- Lights are **on/off only** — there is no brightness ramp, so favor sharp
  on/off effects (On, Twinkle, fast fades read as on/off).
- Closures (windows/mirrors/doors/charge port/liftgate) move slowly — give them
  room; rapid toggling won't keep up.

## 4. Export the FSEQ

`File → Export Sequence…` and choose:

- **Format:** FSEQ
- **Version:** **V2 Uncompressed**

Name it `lightshow.fseq` and save it inside that show's folder. If you have audio,
keep it next to the fseq with a matching base name (`lightshow.wav` / `lightshow.mp3`).

## 5. Validate

```bash
python3 ../tools/validator.py lightshow.fseq
```

A good result prints the frame count, step time, and total duration. Any
`ValidationError` must be fixed before the car will accept the file — see the
error text (wrong channel count, compression, version, or duration).

## 6. Load it on the car

Follow [usb-setup.md](usb-setup.md), then on the touchscreen:
**Toybox → Light Show**, select the USB show, and **Activate** while parked.

## Tips

- Vehicle ignores frames faster than it can physically actuate — keep step time ≥ 20 ms.
- Test in the driveway with the music low; the show runs lights + audio through the car.
- Commit each finished show so you can iterate without losing a good version.
