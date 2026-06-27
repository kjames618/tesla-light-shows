#!/usr/bin/env python3
"""
Future - "Mask Off"  |  Tesla Light Show  (waveform-driven, aggressive/trap)
============================================================================
Concert-grade, EDM-festival energy locked to YOUR audio via beatmap.json
(per-beat time / energy / onset / section from tools/build_beatmap.py).

Design language:
  * intro flute  -> a mesmerizing wave that "dances" left<->right across the car
  * the 0:13 drop -> a massive full-vehicle impact
  * hooks/verses -> aggressive trap: kick slams, snare/hazard backbeats,
                    machine-gun fog strobes on the hats, alternating signatures,
                    rhythmic turn signals, reverse/brake accents, sweeps + ripples
  * 1:43 breakdown -> strip to the flute, tension riser, blackout before the re-drop
  * re-drop + final -> everything, escalating; each hook denser than the last
  * final ~12s -> maximum flash density + rapid zone alternation
  * last beat   -> one massive synchronized finale, then a clean blackout

Build:
  python3 ../../tools/build_beatmap.py lightshow.wav beatmap.json 150 sections.json
  python3 build_show.py
  python3 ../../tools/validator.py lightshow.fseq

Fine alignment: set NUDGE_S (seconds) if your ears want a global shift.
"""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from tesla_lightshow import Show, L  # noqa: E402

HERE = os.path.dirname(__file__)
NUDGE_S = 0.0

bm = json.load(open(os.path.join(HERE, "beatmap.json")))
beats = bm["beats"]
N = len(beats)
DT = bm["beat_period_s"]
DUR = bm["duration_s"]
show = Show(bpm=bm["bpm"], total_seconds=DUR + 0.4)


def T(b):
    return b["t"] + NUDGE_S


def rnd(i):
    """Deterministic pseudo-random in [0,1) — for 'randomized' bursts."""
    return ((i * 2654435761) % 100000) / 100000.0


# Each chorus/section is explicitly more intense than the previous one, so the
# escalation reads visually (not just via the randomized bursts).
SECTION_INTENSITY = {
    "hook1": 0.55, "verse1": 0.50, "hook2": 0.72, "final": 0.90,
}


# Left->right sweep chain across the whole car (single channels) for wave effects.
WAVE = list(reversed(L.left_side)) + L.right_side
HAZARD = L.front_turn + L.rear_turn        # all four corners = hazards


def flute_wave(b, t, dt, intensity=1.0):
    """A 3-wide lit band that ping-pongs across the car, dancing with the flute."""
    n = len(WAVE)
    period = 8                              # beats per full there-and-back sweep
    ph = (b["i"] % period) / period
    pos = ph * 2
    if pos > 1:
        pos = 2 - pos                       # ping-pong 0..1..0
    center = int(pos * (n - 1))
    width = 1 + int(intensity)             # band gets wider as it grows
    for k in range(-width, width + 1):
        idx = center + k
        if 0 <= idx < n:
            show.flash([WAVE[idx]], t, dt * 0.9)
    if b["beat_in_bar"] == 0:               # soft breathing pulse on downbeats
        show.flash(L.signature, t, dt * 0.8)


def big(b, t, dt, g):
    """Aggressive trap choreography for the high-energy sections.
    g = global escalation 0..1 (everything denser/faster as the show builds)."""
    e = b["e_norm"]
    onset = b["onset_norm"]
    db = b["beat_in_bar"] == 0
    back = b["beat_in_bar"] in (1, 3)
    bar = b["bar"]
    strong = onset > 0.20

    # --- sustained underglow that GROWS each chorus, so escalation reads visually ---
    if g > 0.60:
        show.on(L.side_marker, t, t + dt)
    if g > 0.78:
        show.on(L.aux_park, t, t + dt)
    if g > 0.88:
        show.on(L.tail, t, t + dt)

    # --- constant movement: alternating signature on every beat (no dead space) ---
    show.flash(L.signature[:1] if b["i"] % 2 == 0 else L.signature[1:], t, dt * 0.45)

    # --- KICK / downbeat slam, scaled by loudness ---
    if db or onset > 0.34:
        show.flash(L.all_lights if e > 0.6 else L.all_front, t, 0.10)
        show.symmetric_out(t + 0.02, min(dt * 2, 0.7), trail=3)

    # --- SNARE backbeat: rear hit + hazard flash when it slaps ---
    if back:
        show.flash(L.brake + L.tail, t, 0.12)
        if e > 0.5:
            show.flash(HAZARD, t, 0.08)

    # --- HI-HAT machine-gun fog strobes; fire more often as we escalate ---
    if strong and (db or rnd(b["i"]) < 0.35 + 0.55 * g):
        period = max(0.05, 0.10 - 0.04 * g)       # 10Hz -> ~16Hz toward the end
        show.strobe(L.front_fog, t, t + dt, period_s=period, duty=0.5)

    # --- rhythmic turn signals + reverse-light accents ---
    if b["i"] % 4 == 2:
        show.flash(L.reverse, t, 0.10)
    if b["i"] % 8 in (1, 5):
        show.flash(L.front_turn[:1] if b["i"] % 16 < 8 else L.front_turn[1:], t, dt * 0.4)

    # --- per-bar directional sweep, alternating L->R / R->L ---
    if db:
        chain = L.front_to_back if bar % 2 == 0 else list(reversed(L.front_to_back))
        show.chase(chain, t, dt * 4, on_frac=0.6)

    # --- big closure accents on strong downbeats ---
    if db and e > 0.5 and bar % 4 == 0:
        show.window_dip(t, hold=0.35)
    if db and bar % 8 == 0:
        show.charge_port_pop(t, 0.3)
        show.mirror_fold(t, 0.5)

    # --- randomized bursts for chaos (grows with g) ---
    if rnd(b["i"] * 7) < 0.10 + 0.15 * g:
        show.flash(L.headlights, t, 0.05)


def impact(t):
    """A maximum full-vehicle hit: every light + every closure fires."""
    show.flash(L.all_lights, t, 0.16)
    show.symmetric_out(t + 0.02, 0.8, trail=4)
    show.window_dip(t, hold=0.5)
    show.mirror_fold(t, hold=0.6)
    show.charge_port_pop(t, hold=0.4)
    show.liftgate_pop(t, hold=0.5)
    show.falcon_flare(t, hold=0.8)           # Model X bonus


# ---------------------------------------------------------------------------
for i, b in enumerate(beats):
    t = T(b)
    nb_t = (beats[i + 1]["t"] + NUDGE_S) if i + 1 < N else (t + DT)
    dt = max(0.05, nb_t - t)
    g = i / N
    sec = b["section"]

    if sec == "outro":
        continue                                     # darkness/silence

    if sec == "intro_flute":
        # the flute "dances" — grows subtly across the 13s into the drop
        flute_wave(b, t, dt, intensity=min(2.0, 0.3 + 1.7 * (t / 13.0)))
        continue

    if sec == "drop1":
        impact(t)                                    # the 0:13 slam
        continue

    if sec == "breakdown":
        # strip HARD to the flute for max contrast; build tension; riser into re-drop
        if t < 112.0:
            flute_wave(b, t, dt, intensity=0.3)        # sparse single-dot wave
            if b["beat_in_bar"] == 0 and b["bar"] % 2 == 0:
                show.mirror_fold(t, hold=0.5)
        else:
            # accelerating strobe riser into the 1:55 re-drop
            ramp = (t - 112.0) / 3.0                 # 0..1
            period = max(0.05, 0.14 - 0.09 * ramp)
            show.strobe(L.all_front, t, t + dt, period_s=period, duty=0.5)
        continue

    if sec == "redrop":
        impact(t)                                    # bigger re-entry
        continue

    if sec == "finale_build":
        # FINAL ~12s: maximum density, machine-gun across alternating zones
        zoneA = L.all_front
        zoneB = L.all_rear
        show.strobe(zoneA if b["i"] % 2 == 0 else zoneB, t, t + dt,
                    period_s=0.05, duty=0.5)
        show.flash(L.signature if b["i"] % 2 else L.headlights, t, dt * 0.5)
        if b["beat_in_bar"] == 0:
            impact(t)
        if b["i"] % 2 == 0:
            show.flash(HAZARD, t, 0.05)
        continue

    # all remaining high-energy sections: hook1 / verse1 / hook2 / final.
    # Escalate by the LATER of (time-based g) and (this section's intensity),
    # so every chorus is denser than the one before it.
    si = SECTION_INTENSITY.get(sec, 0.5)
    big(b, t, dt, max(g, si))

# ---- FINALE: one massive synchronized hit on the last musical beat, then black ----
last = None
for b in beats:
    if b["t"] < 193.0 and b["e_norm"] > 0.2:
        last = b
final_t = T(last) if last else (DUR - 6.0)
impact(final_t)
show.on(L.all_lights, final_t, final_t + 0.9)
# nothing after final_t + ~0.9s  ->  perfectly timed blackout into the outro

# ---------------------------------------------------------------------------
out = os.path.join(HERE, "lightshow.fseq")
info = show.write(out, audio_name="lightshow.wav")
print("Wrote", out)
print(info)
print(f"Locked to audio: bpm={bm['bpm']}, downbeat={bm['downbeat_s']}s, "
      f"{N} beats, final hit @ {final_t:.1f}s")
