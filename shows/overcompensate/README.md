# Overcompensate — Twenty One Pilots

A competition-style Tesla Light Show choreographed to **Twenty One Pilots –
"Overcompensate"**, built entirely from code and **locked to the actual audio
waveform** — no xLights.

| | |
|---|---|
| **Tempo** | 95 BPM, 4/4, F minor |
| **Audio used** | "Official Video" rip, **4:15 (255 s)** — longer than the 3:56 single |
| **Downbeat** | detected at **1.906 s** (steady 95 BPM grid) |
| **Channels** | 48 (standard) — **plays on every Tesla model** |
| **Files** | [`lightshow.fseq`](lightshow.fseq) (validated), [`build_show.py`](build_show.py), [`beatmap.json`](beatmap.json) |

## How it's synced (waveform-driven)

This isn't flashing to a guessed tempo. The pipeline analyzes **your real file**:

1. **`tools/build_beatmap.py`** reads `lightshow.wav`, finds the downbeat via a
   comb-filter over the onset envelope, and emits **`beatmap.json`** — every beat's
   time, **energy (loudness)**, **onset/transient strength**, bar position, and
   which song section it falls in (sections derived from the real energy envelope).
2. **`build_show.py`** choreographs each beat *off that data*: intensity scales
   with real loudness, accents fire on real onsets, and each section gets its own
   motif. The light-energy arc provably tracks the audio-energy arc (including the
   breakdown crater and the climax peak).

Regenerate after any audio change:
```bash
python3 ../../tools/build_beatmap.py lightshow.wav beatmap.json 95
python3 build_show.py
python3 ../../tools/validator.py lightshow.fseq
```

## Works on every Tesla

One standard 48-channel file. Each car only actuates the channels it has — a
Model Y/3/S ignores the Falcon-door cues; a Model X plays them as a bonus. The
choreography leans on universal light channels (head/signature/turn/fog/
side-marker/tail/brake/reverse/license), with windows, mirrors, charge port,
liftgate and Falcon doors as accents. Cybertruck, S/Plaid, 3/Y, X — all covered.

## The show, mapped to the real song

| Time | Section | Energy | What happens |
|------|---------|:------:|--------------|
| 0:00–0:05 | silence | ▁ | dark |
| 0:05–0:17 | intro | ▂ | lone alternating signature blips, tension build |
| 0:17–0:49 | verse 1 | ▄ | controlled L↔R body walk, fog accents on real hi-hats |
| 0:49–1:05 | **drop 1** | █ | downbeat slams, symmetric pulses, charge-port pop, cross-body strobe |
| 1:05–1:07 | lull | ▂ | hard pullback for contrast |
| 1:07–1:47 | verse 2 | ▆ | denser walk, traveling waves, mirror folds at phrase ends |
| 1:47–2:40 | chorus body | █ | sustained big choreography, waves + charge-port accents |
| 2:40–2:42 | transition | ▃ | dip |
| 2:42–3:08 | **build 2** | █ | reversing waves, window dips — the rig roars |
| 3:08–3:16 | **breakdown** | ▁ | strips to near-darkness; slow tension pulses + mirror fold |
| 3:16–3:37 | rebuild | ▃→▆ | accelerating riser chase climbing into the peak |
| 3:37–3:58 | **climax** | █ | most elaborate: layered ripples, windows, Falcon flare, alternating with darkness |
| ~3:58 | **final hit** | █ | one massive full-vehicle cue (lights + all closures) |
| 3:58–4:15 | outro | ▁ | blackout into the silence |

Each drop is bigger than the last; the climax is the peak; it ends in darkness
with no lingering lights.

## Loading it on the car

1. Your audio is already here as `lightshow.wav` (converted from your MP3, 44.1 kHz).
   The car also accepts `.mp3` — either works as long as the base name matches.
2. Copy **both** `lightshow.fseq` and your audio into a top-level `LightShow/`
   folder on a USB drive — see [../../docs/usb-setup.md](../../docs/usb-setup.md).
3. In the car: **Toybox → Light Show**, pick the show, **Activate** (in Park).

> The audio (`lightshow.wav` and `lightshow.mp3`) is committed to this repo with
> the owner's permission. On your USB, put only **one** audio file next to the
> `.fseq` (same base name) — the `.mp3` is smaller; the `.wav` is highest quality.

## Fine-tuning

The show is already locked to your file. If your ears want a tiny global shift,
set `NUDGE_S` (seconds) at the top of `build_show.py` and re-run it. To reshape a
section, edit its motif in `build_show.py` (each section has its own block).

## Honest limits

- **Lights are on/off** (no dimming) — dynamics come from movement, zones, chases,
  and blackouts, exactly how an arena rig reads.
- **Not controllable by any Tesla light show:** interior lights, suspension, horn
  (horn exists but is intentionally unused).
