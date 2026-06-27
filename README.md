# Tesla Light Shows

A personal collection of custom **Tesla Light Show** sequences, built with [xLights](https://xlights.org/) and validated against Tesla's official requirements.

Tesla vehicles can run choreographed shows that flash the lights and move the
windows, mirrors, charge port, and (on supported cars) the liftgate and falcon
doors in time to music. This repo is where I design, store, validate, and version
those shows.

## What's in here

| Path | What it is |
|------|------------|
| [`shows/`](shows/) | One folder per light show (xLights project + exported `.fseq` + audio) |
| [`tools/validator.py`](tools/validator.py) | Tesla's official `.fseq` validator (vendored from `teslamotors/light-show`) |
| [`templates/`](templates/) | Where the blank xLights project template lives — see [templates/README.md](templates/README.md) |
| [`docs/`](docs/) | Step-by-step guides: getting started, USB setup, and the light/closure channel map |

## Quick start

1. **Install xLights** (free): https://xlights.org/releases/
2. **Grab the template** — download `tesla_xlights_show_folder.zip` from the
   [official Tesla repo](https://github.com/teslamotors/light-show) and open it in xLights.
3. **Design your show** in xLights against the supplied model + audio.
4. **Export** as an FSEQ file (`File → Export Sequence → FSEQ`), choosing **V2 Uncompressed**.
5. **Validate** before copying to the car:
   ```bash
   python3 tools/validator.py shows/your-show/lightshow.fseq
   ```
6. **Copy to USB** following [docs/usb-setup.md](docs/usb-setup.md), then in the car:
   **Toybox → Light Show → (your USB show)**.

See [docs/getting-started.md](docs/getting-started.md) for the full walkthrough.

## Key requirements (enforced by the validator)

- **Format:** FSEQ **v2.0 (or 2.2)**, **V2 Uncompressed**
- **Channels:** **48** (closures only) or **200** (full lights + closures)
- **Frame / step time:** ≥ 15 ms (20 ms is standard)
- **Duration:** under **4 hours**
- **USB:** formatted exFAT / FAT32 / ext3 / ext4 (**not NTFS**), files in a top-level `LightShow` folder, no `TeslaCam` folder or firmware files on the same drive

## Supported vehicles

Model S (2021+), Model 3, Model X (2021+), Model Y, and Cybertruck, running
software **v11.0 (2021.44.25)** or later.

## Credits

Built on Tesla's open-source tooling: <https://github.com/teslamotors/light-show>.
The vendored `validator.py` is © Tesla, included here for convenience.
