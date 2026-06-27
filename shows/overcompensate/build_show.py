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

# A concert-size vocabulary translated to the car's binary light zones.
# Short, separated hits read as much more violent than leaving everything on.
GLITCH_ZONES = [
    L.signature + L.tail,
    L.headlights + L.brake,
    L.front_turn + L.rear_turn,
    L.front_fog + L.rear_fog + L.reverse,
    L.side_marker + L.side_repeater,
]


def T(b):
    return b["t"] + NUDGE_S


def glitch_burst(t, dt, phase=0, density=4, full_rig_finish=False):
    """Fast, deterministic zone cuts: chaotic to the eye, repeatable on rebuild."""
    step = dt / density
    flash_len = min(0.075, step * 0.48)
    for i in range(density):
        zone = GLITCH_ZONES[(phase + i * 2) % len(GLITCH_ZONES)]
        show.flash(zone, t + i * step, flash_len)
    if full_rig_finish:
        show.flash(L.all_lights, t + dt * 0.78, min(0.10, dt * 0.18))


def kick_triplet(t, dt, reverse=False):
    """Front/rear/full three-hit slam for fills and section launches."""
    zones = [L.all_front, L.all_rear, L.all_lights]
    if reverse:
        zones[0], zones[1] = zones[1], zones[0]
    for i, zone in enumerate(zones):
        show.flash(zone, t + i * dt * 0.17, min(0.09, dt * 0.12))


def blackout_cut(t, dt, start=0.52, length=0.16):
    """Carves a hard pocket of darkness so the following hit feels enormous."""
    show.off(L.all_lights, t + dt * start, t + dt * (start + length))


def motif(b, nb_t):
    """Choreograph a single beat `b`. nb_t = next beat time (for hold lengths)."""
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
        # Concert opening: ominous pulse -> nervous scan -> ignition countdown.
        # Tesla has no color control, so front/rear separation stands in for the
        # arena's red wash while black frames keep the look severe.
        if db:
            show.flash(L.headlights + L.brake, t, 0.13)
        elif t < 12.0:
            side = L.left_side[:3] if b["beat_in_bar"] == 1 else L.right_side[:3]
            show.flash(side, t, 0.065)
        if 12.0 <= t < 14.5:
            glitch_burst(t, dt, phase=bar, density=2)
        elif 14.5 <= t < 16.15:
            glitch_burst(t, dt, phase=b["i"], density=4, full_rig_finish=db)
        elif t >= 16.15:
            # A false launch, then dead black immediately before the vocal entry.
            show.strobe(L.all_lights, t, t + dt * 0.62, period_s=0.075, duty=0.32)
            show.off(L.all_lights, t + dt * 0.62, t + dt)
        return

    if sec in ("verse1", "verse2"):
        # Syncopated rap pocket: retain space, but puncture it with drum flashes
        # and a larger four-bar phrase turn.
        half = L.left_side if (bar % 2 == 0) else L.right_side
        depth = 5 if sec == "verse1" else len(half)
        if db:
            show.on(half[:depth], t, t + dt * 0.72)
        if b["beat_in_bar"] == 2:
            other = L.right_side if (bar % 2 == 0) else L.left_side
            show.on(other[:depth], t, t + dt * 0.72)
        if strong and not db:
            glitch_burst(t, dt, phase=b["i"], density=3 if sec == "verse1" else 4)
        if b["beat_in_bar"] == 3 and bar % 4 == 3:
            kick_triplet(t + dt * 0.38, dt, reverse=(bar % 8 == 7))
        if sec == "verse2":
            if db and bar % 2 == 1:
                show.wave_back(t, 2 * dt, trail=1, reverse=(bar % 4 == 3))
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
        # Escalate from a moving dot to controlled visual overload before the peak.
        steps = 3 + int(e * 5)
        seg = L.center_out[:max(2, min(7, steps))]
        show.chase(seg, t, dt * 0.95, on_frac=0.8)
        if back and strong:
            glitch_burst(t, dt, phase=bar, density=3 + int(e * 3))
        if db:
            kick_triplet(t, dt, reverse=(bar % 2 == 1))
        if bar >= 84 and b["beat_in_bar"] == 3:
            show.strobe(L.all_lights, t + dt * 0.45, t + dt, period_s=0.065, duty=0.34)
        return

    # ---- tier-3 big sections: drop1 / chorus_body / build2 / climax ----
    big = e > 0.55
    if db:
        kick_triplet(t, dt, reverse=(bar % 2 == 1))
        show.symmetric_out(t + dt * 0.10, min(dt * 0.82, 0.58), trail=2)
    if back:
        show.flash(L.brake + L.tail + L.rear_turn, t, 0.10)
        glitch_burst(t + dt * 0.22, dt * 0.72, phase=b["i"], density=4 if big else 3)
    else:
        show.alt_lr(t, t + dt, rate_beats=0.25 if big else 0.5)
    if strong and not db and not back:
        glitch_burst(t, dt, phase=b["i"], density=5 if big else 3,
                     full_rig_finish=big)
    if b["beat_in_bar"] == 3 and bar % 2 == 1:
        blackout_cut(t, dt)
        show.strobe(L.all_lights, t + dt * 0.70, t + dt,
                    period_s=0.060 if big else 0.085, duty=0.35)

    if sec == "drop1":
        if db and bar == 20:
            show.charge_port_pop(t, hold=0.4)
        if db and bar % 2 == 1:
            show.wave_back(t, 2 * dt, trail=1)
    elif sec == "build2":
        if db:
            show.wave_back(t, 2 * dt, trail=1, reverse=(bar % 2 == 0))
        if db and bar % 4 == 0:
            show.window_dip(t, hold=0.4)
    elif sec == "climax":
        # Peak: frantic zone cuts and strobes, with closures only on phrase marks.
        show.strobe(L.all_lights, t + dt * 0.55, t + dt,
                    period_s=0.055, duty=0.30)
        if db:
            # Three climax dips + three build2 dips = Tesla's limit of six.
            if bar % 4 == 1:
                show.window_dip(t, hold=0.5)
            show.ripple(L.front_to_back, t, dt, trail=1,
                        reverse=(bar % 2 == 1))
            if bar % 2 == 0:
                show.falcon_flare(t, hold=0.9)
        if db and bar % 4 == 2:
            show.mirror_fold(t, hold=0.5)
    elif sec == "chorus_body":
        if db and bar % 2 == 0:
            show.wave_back(t, 2 * dt, trail=1, reverse=(bar % 4 == 2))
        if db and bar == 52:
            show.charge_port_pop(t, hold=0.3)


# ---- run the choreographer across every beat ----
for i, b in enumerate(beats):
    nb_t = beats[i + 1]["t"] if i + 1 < len(beats) else (b["t"] + DT)
    if b["section"] == "final_hit":
        continue                         # handled below
    motif(b, nb_t)

# ---- SECTION IMPACTS: the arena curtain-drop moments ----------------------
# The first vocal entrance is the show's ignition: a full-rig flash, a slash of
# darkness, then a half-second machine-gun strobe. Each major return gets a
# smaller version so the energy arc keeps climbing instead of flattening out.
for boundary, strength in ((17.0, 1), (49.0, 2), (107.0, 2),
                           (162.0, 2), (217.0, 3)):
    first = next((b for b in beats if b["t"] >= boundary), None)
    if not first:
        continue
    t = T(first)
    show.flash(L.all_lights, t, 0.14)
    show.off(L.all_lights, t + 0.14, t + 0.24)
    burst_end = t + (0.48 if strength == 1 else 0.70)
    show.strobe(L.all_lights, t + 0.24, burst_end,
                period_s=0.075 if strength < 3 else 0.055, duty=0.34)

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
