# USB Setup

How to get a finished show onto the car.

## Format the drive

- File system: **exFAT**, **FAT32**, **ext3**, or **ext4**
- **NTFS is not supported**
- A plain USB flash drive works; it does **not** need to be the TeslaCam drive.

## Folder layout

Create a single top-level folder named exactly `LightShow` and put your files in it.
The `.fseq` and audio file must share the same base name.

```
USB ROOT/
└── LightShow/
    ├── lightshow.fseq
    └── lightshow.mp3        (or .wav — optional but recommended)
```

> Multiple shows on one drive: give each a unique base name
> (`halloween.fseq` + `halloween.mp3`, `xmas.fseq` + `xmas.wav`, …). The car lists
> them by name.

## Important constraints

- The drive used for a light show **must not** contain a base-level `TeslaCam`
  folder, nor any firmware/map update files. Use a dedicated stick to be safe.
- Eject the drive cleanly before unplugging.

## Run it

1. Plug the USB into a front port.
2. Put the car in **Park**.
3. **Toybox → Light Show** → pick your show → **Activate**.

The car runs the lights (and audio, if present) once. Re-activate to repeat.
