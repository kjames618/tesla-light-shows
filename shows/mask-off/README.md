# Mask Off — Future

An aggressive, hypnotic, festival-grade Tesla Light Show choreographed to
**Future – "Mask Off"**, built from code and **locked to the actual audio
waveform** — no xLights.

| | |
|---|---|
| **Tempo** | 150 BPM grid (75 BPM half-time trap), 4/4 |
| **Audio** | 3:24 (204 s), 44.1 kHz |
| **Downbeat** | detected at 1.160 s |
| **Channels** | 48 (standard) — **plays on every Tesla model** |
| **Files** | [`lightshow.fseq`](lightshow.fseq) (validated), [`build_show.py`](build_show.py), [`beatmap.json`](beatmap.json), [`sections.json`](sections.json) |

## How it's synced

`tools/build_beatmap.py` analyzes `lightshow.wav` → `beatmap.json` (per-beat time,
**energy**, **onset strength**, bar position, section). `build_show.py`
choreographs each beat off that data, so intensity tracks the real loudness and
accents land on real onsets. The 150 BPM grid (double the 75 BPM feel) gives the
resolution needed for the fast hi-hats and machine-gun strobes.

Rebuild:
```bash
python3 ../../tools/build_beatmap.py lightshow.wav beatmap.json 150 sections.json
python3 build_show.py
python3 ../../tools/validator.py lightshow.fseq
```

## The show, mapped to the real song

| Time | Section | What happens |
|------|---------|--------------|
| 0:00–0:13 | **Flute intro** | A 3-wide band of light *dances* left↔right across the whole car with the flute, growing into the drop |
| 0:13 | **Drop** | Massive full-vehicle impact — every light + windows, mirrors, charge port, liftgate, Falcon doors |
| 0:13–1:03 | Hook 1 / Verse | Kick slams, snare→brake/tail + hazard flashes, machine-gun fog strobes on the hats, alternating signatures, rhythmic turn signals, reverse accents, directional sweeps |
| 1:03–1:43 | Hook 2 | Same arsenal, denser (escalation rises continuously) |
| 1:43–1:55 | **Breakdown** | Strips back to the dancing flute wave, then an accelerating strobe **riser** into the re-drop |
| 1:55 | **Re-drop** | Bigger full-vehicle impact |
| 1:55–3:00 | Final | Most elaborate body — layered sweeps, ripples, closures, randomized bursts |
| 3:00–3:12 | **Finale** | Maximum density: machine-gun strobes alternating front/rear zones, hazards, full-vehicle hits every downbeat |
| ~3:12 | **Last hit** | One massive synchronized full-vehicle cue |
| 3:12–3:24 | Outro | Clean blackout into the fade |

Each section escalates; the finale is the peak; it ends on a perfectly timed
blackout.

## Works on every Tesla

One standard 48-channel file. Each car only actuates the channels it has — Model
Y/3/S ignore the Falcon-door cues; Model X plays them as a bonus. The core relies
on universal light channels, with windows/mirrors/charge port/liftgate/Falcon as
impact accents. Cybertruck, S/Plaid, 3/Y, X — all covered.

## Loading on the car

Copy `lightshow.fseq` + one audio file (`lightshow.mp3` or `.wav`) into a
top-level `LightShow/` folder on a USB drive with **no `TeslaCam` folder**.
See [../../docs/usb-setup.md](../../docs/usb-setup.md). Then **Toybox → Light
Show** in Park.

## Honest limits (from the brief)

Tesla light shows control **only exterior lights + closures**. So from the
requested feature list:
- ✅ Used: headlights, fog, signature, turn signals, hazards, brake, reverse,
  tail, license, side markers/repeaters, windows, mirrors, charge port, liftgate
  (trunk), Falcon doors (Model X).
- ❌ **Not possible on any Tesla light show:** interior lighting, suspension
  movement. (No channel exists for them.)
- 🚫 **Horn:** intentionally unused — it's jarring and not worth it here.
- Lights are **on/off** (no dimming); all dynamics come from movement, zones,
  strobing, and blackouts.
