# Example Show (placeholder)

This folder shows the expected layout for a single light show. Replace it with a
real one (or copy it as a starting point).

Each show folder should contain:

```
example-show/
├── README.md            ← notes: song, length, which model, status
├── lightshow.xsq        ← the xLights project (commit this)
├── lightshow.fseq       ← exported sequence, FSEQ V2 Uncompressed (commit this)
└── lightshow.mp3        ← audio (optional; .wav is .gitignored by default)
```

## Per-show notes (fill in)

- **Song / artist:**
- **Duration:**
- **Channel mode:** 48 (closures) / 200 (full)
- **Target model:** Model 3 / Y / S / X / Cybertruck
- **Status:** draft / validated / tested on car
- **Validated?** Run: `python3 ../../tools/validator.py lightshow.fseq`
