#!/usr/bin/env python3
"""
Twenty One Pilots - "Overcompensate"  |  Tesla Light Show  (waveform-driven)
============================================================================
This build reads beatmap.json — a per-beat analysis of YOUR actual audio file
(time, energy, onset strength, bar position, song section) produced by
tools/build_beatmap.py — and choreographs every cue directly off the waveform.

So the show is locked to the real recording: hits land on real onsets, intensity
tracks real loudness, and the structural sections (intro / verse / drops /
breakdown / climax / finale) come from the song's true energy envelope.

Regenerate the beat map any time your audio changes:
    python3 ../../tools/build_beatmap.py lightshow.wav beatmap.json 95
Then run this:
    python3 build_show.py

Fine alignment: if your ears say everything is a hair early/late, set NUDGE_S.
"""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from tesla_lightshow import Show, L  # noqa: E402

HERE = os.path.dirname(__file__)
NUDGE_S = 0.0          # global fine-tune (seconds) if needed against your ears

bm = json.load(open(os.path.join(HERE, "beatmap.json")))
BPM = bm["bpm"]
DT = bm["beat_period_s"]                 # seconds per beat
DUR = bm["duration_s"]
beats = bm["beats"]

show = Show(bpm=BPM, total_seconds=DUR + 0.3)


def T(b):
    return b["t"] + NUDGE_S


# track phrase position for variety
phrase = 0


def motif(b, nb_t):
    """Choreograph a single beat `b`. nb_t = next beat time (for hold lengths)."""
    global phrase
    t = T(b)
    dt = max(0.05, (nb_t + NUDGE_S) - t)
    e = b["e_norm"]
    onset = b["onset_norm"]
    db = b["beat_in_bar"] == 0          # downbeat
    back = b["beat_in_bar"] in (1, 3)   # backbeat (snare)
    sec = b["section"]
    bar = b["bar"]
    strong = onset > 0.22               # real transient present

    if sec in ("silence_intro", "outro_silence"):
        return                          # darkness

    if sec == "intro":
        # lone alternating signature blips; tension grows with energy
        if db:
            side = L.signature[:1] if (bar % 2 == 0) else L.signature[1:]
            show.flash(side, t, 0.12)
        if b["beat_in_bar"] == 2 and e > 0.12:
            show.flash(L.side_marker, t, 0.08)
        if e > 0.20:                    # the lift just before verse
            show.flash([L.center_out[min(b["i"] % 7, 6)][0]], t, 0.07)
        return

    if sec in ("verse1", "verse2"):
        # controlled body "walk", alternating sides per bar; breathes with vocal
        half = L.left_side if (bar % 2 == 0) else L.right_side
        depth = 3 if sec == "verse1" else len(half)      # verse2 is denser
        if db:
            show.on(half[:depth], t, t + 2 * dt)
        if b["beat_in_bar"] == 2:
            other = L.right_side if (bar % 2 == 0) else L.left_side
            show.on(other[:depth], t, t + 2 * dt)
        # hi-hat-ish fog accents on the offbeats, gated by real onsets
        if strong and not db:
            show.flash(L.front_fog if b["beat_in_bar"] < 2 else L.rear_fog, t, 0.06)
        # verse2: a traveling wave once per phrase, mirror fold at phrase ends
        if sec == "verse2":
            if db and bar % 2 == 1:
                show.wave_back(t, 4 * dt, trail=2)
            if db and bar % 8 == 7:
                show.mirror_fold(t, hold=0.8)
        return

    if sec in ("lull", "transition"):
        # pull back hard for contrast — a single accent, mostly dark
        if db:
            show.flash(L.headlights, t, 0.10)
        return

    if sec == "breakdown":
        # the quiet bridge: strip to near-darkness, slow tension pulses
        if db:
            show.symmetric_out(t, min(1.4, 2 * dt), trail=2)
        if bar % 2 == 1 and db:
            show.mirror_fold(t, hold=0.7)
        return

    if sec == "rebuild":
        # escalate: chase density climbs with energy heading into the climax
        steps = 3 + int(e * 5)
        seg = L.center_out[:max(2, min(7, steps))]
        show.chase(seg, t, dt * 0.95, on_frac=0.8)
        if back and strong:
            show.flash(L.rear_turn, t, 0.08)
        if db:
            show.flash(L.all_front, t, 0.07)
        return

    # ---- tier-3 big sections: drop1 / chorus_body / build2 / climax ----
    big = e > 0.55
    if db:
        # downbeat slam scaled by energy
        show.flash(L.all_front if not big else L.all_lights, t, 0.12)
        show.symmetric_out(t + 0.02, min(2 * dt, 1.3), trail=3 if big else 2)
    if back:
        show.flash(L.brake + L.tail, t, 0.12)        # backbeat on the rear
    # fast cross-body fill, denser when louder
    rate = 0.2 if big else 0.33
    show.alt_lr(t, t + dt, rate_beats=rate)
    if strong and not db:
        show.flash(L.headlights, t, 0.06)            # punch real transients

    if sec == "drop1":
        if db and bar % 2 == 0:
            show.charge_port_pop(t, hold=0.4)
        if db and bar % 2 == 1:
            show.wave_back(t, 4 * dt, trail=2)
    elif sec == "build2":
        if db:
            show.wave_back(t, 4 * dt, trail=2, reverse=(bar % 2 == 0))
        if db and bar % 4 == 0:
            show.window_dip(t, hold=0.4)
    elif sec == "climax":
        # most elaborate: layer everything, Model X falcon flare, big closures
        if db:
            show.window_dip(t, hold=0.5)
            show.ripple(L.front_to_back, t, 2 * dt, trail=3)
            if bar % 2 == 0:
                show.falcon_flare(t, hold=0.9)
        if db and bar % 4 == 2:
            show.mirror_fold(t, hold=0.5)
    elif sec == "chorus_body":
        if db and bar % 4 == 0:
            show.wave_back(t, 4 * dt, trail=2)
        if db and bar % 8 == 4:
            show.charge_port_pop(t, hold=0.3)


# ---- run the choreographer across every beat ----
for i, b in enumerate(beats):
    nb_t = beats[i + 1]["t"] if i + 1 < len(beats) else (b["t"] + DT)
    if b["section"] == "final_hit":
        continue                         # handled below
    motif(b, nb_t)

# ---- FINALE: one massive full-vehicle cue on the last musical hit, then black ----
# Find the last beat that still carries energy (the song's final accent).
last = None
for b in beats:
    if b["t"] < 239.0 and b["e_norm"] > 0.18:
        last = b
final_t = T(last) if last else (DUR - 4.0)
# brief dramatic dark gap right before it is already there (energy has dropped)
show.on(L.all_lights, final_t, final_t + 1.0)
show.window_dip(final_t, hold=1.0)
show.mirror_fold(final_t, hold=1.0)
show.charge_port_pop(final_t, hold=1.0)
show.liftgate_pop(final_t, hold=1.0)
show.falcon_flare(final_t, hold=1.0)
# nothing scheduled after final_t + 1.0  ->  blackout into the silence

# ---------------------------------------------------------------------------
out = os.path.join(HERE, "lightshow.fseq")
info = show.write(out, audio_name="lightshow.wav")
print("Wrote", out)
print(info)
print(f"Locked to audio: bpm={BPM}, downbeat={bm['downbeat_s']}s, "
      f"{len(beats)} beats, final hit @ {final_t:.1f}s")
