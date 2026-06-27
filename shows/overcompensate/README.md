# Overcompensate — Twenty One Pilots

A competition-style Tesla Light Show choreographed to **Twenty One Pilots –
"Overcompensate"** (opener of *Clancy*, 2024). Built entirely from code on the
song's 95 BPM grid — no xLights required.

| | |
|---|---|
| **Tempo** | 95 BPM, 4/4, F minor |
| **Length** | 3:58 render (song ≈ 3:56 + a short dark tail) |
| **Channels** | 48 (standard) — **plays on every Tesla model** |
| **File** | [`lightshow.fseq`](lightshow.fseq) — validated, ready for USB |
| **Source** | [`build_show.py`](build_show.py) — regenerate any time |

## Works on every Tesla

This is a single standard 48-channel show. Each car only actuates the channels it
physically has — a Model Y/3/S ignores the Falcon-door cues, a Model X plays them
as bonus. The choreography leans on **universal light channels** (head/signature/
turn/fog/side-marker/tail/brake/reverse/license) that exist on *all* models, with
closures (windows, mirrors, charge port, liftgate) and Falcon doors layered as
accents. Cybertruck, Model S/Plaid, Model 3/Y, Model X — all covered.

## The show, section by section

| Bar | Time | Section | What happens |
|----:|------|---------|--------------|
| 0   | 0:00 | Intro / darkness | Lone alternating signature blips, a rising "charge" |
| 8   | 0:20 | **First impact** | Full-front burst + windows crack + mirror fold, snap to black |
| 9   | 0:23 | Verse 1 | Controlled L↔R body walk, fog hi-hat accents, phrase-end pulses |
| 24  | 1:01 | Pre-chorus build | Front→back chase tightens, 4-on-the-floor head stabs |
| 32  | 1:21 | **Drop 1** | Charge-port pop, symmetric pulses, backbeat on brake/tail, cross-body strobe |
| 40  | 1:41 | Verse 2 | Denser than V1, traveling waves, mirror folds at phrase ends |
| 56  | 2:21 | Build 2 | Accelerating center-out chase — the rig fully wakes up |
| 64  | 2:42 | **Drop 2** | Bigger: whole-car slams, windows down, ripples, rapid alternation |
| 72  | 3:02 | Bridge | Double-time 1/8 strobes, hard blackouts between phrases |
| 84  | 3:32 | **Climax** | Overwhelming all-zones + Falcon flare, alternating with total darkness |
| 92  | 3:52 | Finale | Strip to single accents → one massive full-vehicle hit → blackout |

Each drop is larger than the one before; the climax is the energy peak; the show
ends in silence and darkness with no lingering lights.

## Add your audio (required)

The `.fseq` is the light data only. For the car you also need the song as audio,
which you must supply yourself (copyright — it's not in this repo):

1. Get **`lightshow.wav`** (or `.mp3`), 44.1 kHz, from your own copy of the track.
2. Put it in this folder next to `lightshow.fseq` (same base name).
3. Copy **both** files into a top-level `LightShow/` folder on a USB drive
   (see [../../docs/usb-setup.md](../../docs/usb-setup.md)).

> `.wav` files are git-ignored on purpose, so your audio never gets committed.

## Tuning it to your exact track

The whole show is laid out in **bars at 95 BPM**, so it's already musically tight.
To lock it to your specific audio file:

1. Open [`build_show.py`](build_show.py).
2. If the first downbeat isn't at t=0, set **`OFFSET_S`** (seconds) near the top —
   the entire show shifts to match.
3. Run `python3 build_show.py`. It prints a **section/timestamp table**; play your
   track and check each section lands. If one is early/late, nudge that section's
   bar number.
4. Re-run and re-validate:
   ```bash
   python3 build_show.py
   python3 ../../tools/validator.py lightshow.fseq
   ```

## What a Tesla can and can't do (so expectations are right)

- **Lights are on/off** — no dimming. Dynamics come from movement, zones, chases,
  and blackouts (exactly how a real arena rig reads).
- **Controllable:** all exterior lights + closures (windows, mirrors, charge port,
  liftgate, door handles, front doors, Falcon doors).
- **Not controllable by any light show:** interior lights, suspension, horn
  (horn is technically available but intentionally unused here).
