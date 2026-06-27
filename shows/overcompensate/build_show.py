#!/usr/bin/env python3
"""
Twenty One Pilots - "Overcompensate"  |  Tesla Light Show
=========================================================
A competition-style, arena-concert choreography rendered to a Tesla-compatible
.fseq, built entirely from the 95 BPM musical grid (no xLights).

Song facts:  95 BPM, F minor, 4/4, 3:56 (≈236 s), opener of *Clancy* (2024).

Design arc (per the creative brief):
  darkness -> sudden first impact -> breathing verses -> escalating builds ->
  ever-bigger drops -> overwhelming climax with blackout contrast ->
  cinematic strip-down -> one massive full-vehicle hit -> blackout on the last note.

TUNING TO YOUR AUDIO
--------------------
Everything is laid out in BARS at 95 BPM. If your file's first downbeat isn't at
t=0, set OFFSET_S (seconds) below — the whole show shifts with it. If your ear
says a section lands a beat early/late, nudge that section's bar number. The
SECTIONS table prints with timestamps when you run this, so you can A/B against
the track quickly.

Run:  python3 build_show.py    ->  writes lightshow.fseq next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from tesla_lightshow import Show, L  # noqa: E402

BPM = 95.0
TOTAL_S = 238.0          # 3:56 + ~2s of intentional dark tail
OFFSET_S = 0.0           # <-- nudge here to align bar 0 with the first downbeat

show = Show(bpm=BPM, total_seconds=TOTAL_S, offset_s=OFFSET_S)
B = show.bar             # B(n, beat_in_bar) -> seconds
BEAT = show.beat


def snares(bar_a, bar_b, ch, dur=0.10):
    """Accent beats 2 & 4 (the backbeat) across a bar range."""
    for bar in range(bar_a, bar_b):
        show.flash(ch, B(bar, 1), dur)
        show.flash(ch, B(bar, 3), dur)


def kicks(bar_a, bar_b, ch, dur=0.10):
    """Accent beats 1 & 3 across a bar range."""
    for bar in range(bar_a, bar_b):
        show.flash(ch, B(bar, 0), dur)
        show.flash(ch, B(bar, 2), dur)


# ===========================================================================
# 0:00  INTRO — near total darkness, restrained pulses building tension
# ===========================================================================
show.mark("Intro / darkness", 0)
# A single, lonely signature blip on each downbeat, alternating sides.
for bar in range(0, 6):
    side = L.signature[:1] if bar % 2 == 0 else L.signature[1:]
    show.flash(side, B(bar, 0), 0.12)
    if bar >= 3:                                   # tension creeps in
        show.flash(L.side_marker, B(bar, 2), 0.08)
# Bars 6-7: a rising "charge" — accelerating blips climbing toward impact
for i, t in enumerate([B(6, 0), B(6, 2), B(7, 0), B(7, 1), B(7, 2), B(7, 3), B(7, 3.5)]):
    grp = L.center_out[min(i, len(L.center_out) - 1)]
    show.flash(grp, t, 0.07)

# ===========================================================================
# 0:20  FIRST IMPACT — the surprise. Full front burst, then snap to black.
# ===========================================================================
show.mark("FIRST IMPACT", 8)
show.flash(L.all_front, B(8, 0), 0.22)
show.window_dip(B(8, 0), hold=0.5)                 # windows crack on the hit
show.mirror_fold(B(8, 0.5), hold=0.6)
show.flash(L.all_rear, B(8, 0.5), 0.12)
# deliberate blackout for the rest of the bar -> drama

# ===========================================================================
# 0:23  VERSE 1 — controlled, breathing with the vocal, smooth not flashy
# ===========================================================================
show.mark("Verse 1", 9)
for bar in range(9, 24):
    # headlights "breathe" by walking across the body, alternating sides per bar
    if bar % 2 == 0:
        show.on(L.left_side[:3], B(bar, 0), B(bar, 2))
        show.on(L.right_side[:3], B(bar, 2), B(bar, 4))
    else:
        show.on(L.right_side[:3], B(bar, 0), B(bar, 2))
        show.on(L.left_side[:3], B(bar, 2), B(bar, 4))
    # soft fog accents on the off-beats follow the hi-hats
    show.flash(L.front_fog, B(bar, 1.5), 0.06)
    show.flash(L.front_fog, B(bar, 3.5), 0.06)
    # every 4th bar, a gentle symmetric pulse on the phrase turn
    if bar % 4 == 3:
        show.symmetric_out(B(bar, 3), 1.0, trail=2)

# ===========================================================================
# 1:03  PRE-CHORUS BUILD — complexity ramps, the rig wakes up
# ===========================================================================
show.mark("Pre-chorus build", 24)
for bar in range(24, 32):
    rate = 0.5 if bar < 28 else 0.25               # chase tightens as we build
    show.chase(L.front_to_back, B(bar, 0), show.spb * 4, on_frac=0.9)
    snares(bar, bar + 1, L.rear_turn, dur=0.08)
    if bar >= 28:
        show.flash(L.headlights, B(bar, 0), 0.06)  # 4-on-the-floor stabs
        show.flash(L.headlights, B(bar, 2), 0.06)
# big lift right before the drop
show.symmetric_out(B(31, 2), 1.0, trail=3)
# -- intentional blackout on the "&" before the drop for contrast --

# ===========================================================================
# 1:23  DROP 1 / CHORUS — first explosive payoff
# ===========================================================================
show.mark("DROP 1 (chorus)", 32)
show.charge_port_pop(B(32, 0), hold=0.5)
for bar in range(32, 40):
    show.flash(L.all_front, B(bar, 0), 0.10)       # downbeat slam
    show.symmetric_out(B(bar, 0.25), show.spb * 2, trail=3)
    snares(bar, bar + 1, L.brake + L.tail, dur=0.12)   # backbeat on the rear
    show.alt_lr(B(bar, 2), B(bar, 4), rate_beats=0.25) # fast cross-body strobe
    if bar % 2 == 1:
        show.wave_back(B(bar, 0), show.spb * 4, trail=2)

# ===========================================================================
# 1:43  VERSE 2 — same restraint as V1 but denser, rear now involved
# ===========================================================================
show.mark("Verse 2", 40)
for bar in range(40, 56):
    if bar % 2 == 0:
        show.on(L.left_side, B(bar, 0), B(bar, 2))
        show.on(L.right_side, B(bar, 2), B(bar, 4))
    else:
        show.on(L.right_side, B(bar, 0), B(bar, 2))
        show.on(L.left_side, B(bar, 2), B(bar, 4))
    show.flash(L.front_fog, B(bar, 1.5), 0.06)
    show.flash(L.rear_fog, B(bar, 3.5), 0.06)
    if bar % 4 == 1:
        show.wave_back(B(bar, 0), show.spb * 4, trail=2)   # traveling wave
    if bar % 8 == 7:
        show.mirror_fold(B(bar, 2), hold=0.8)              # phrase-end accent

# ===========================================================================
# 2:24  BUILD 2 — escalating, faster, the rig is fully awake
# ===========================================================================
show.mark("Build 2", 56)
for bar in range(56, 64):
    density = 0.5 - (bar - 56) * 0.05              # chase accelerates each bar
    density = max(density, 0.18)
    t = B(bar, 0)
    while t < B(bar + 1, 0):
        show.chase(L.center_out, t, density, on_frac=0.8)
        t += density
    snares(bar, bar + 1, L.headlights, dur=0.06)
show.symmetric_out(B(63, 2), 1.0, trail=4)

# ===========================================================================
# 2:44  DROP 2 — bigger than Drop 1. Full vehicle, windows, hard contrast.
# ===========================================================================
show.mark("DROP 2 (bigger)", 64)
# hard blackout on the bar 64 upbeat already (nothing scheduled) -> the slam hits harder
for bar in range(64, 72):
    show.flash(L.all_lights, B(bar, 0), 0.12)      # whole-car slam on downbeat
    show.window_dip(B(bar, 0), hold=0.4)
    show.ripple(L.front_to_back, B(bar, 0.5), show.spb * 3, trail=2)
    show.alt_lr(B(bar, 0), B(bar, 4), rate_beats=0.2)
    snares(bar, bar + 1, L.all_rear, dur=0.10)
    if bar % 2 == 0:
        show.charge_port_pop(B(bar, 2), hold=0.3)

# ===========================================================================
# 3:04  BRIDGE — fast double-time section, precise strobes, tension + blackouts
# ===========================================================================
show.mark("Bridge (fast / double-time)", 72)
for bar in range(72, 84):
    # tight 1/8 strobe on alternating zones, double-time feel (190)
    zone = L.headlights if bar % 2 == 0 else L.all_rear
    show.strobe(zone, B(bar, 0), B(bar, 3), period_s=show.spb / 2, duty=0.45)
    # beat 4 = hard blackout (schedule nothing) for a stab of silence/darkness
    if bar % 4 == 3:
        # phrase end: a single cross-body sweep instead of strobe
        show.chase(L.front_to_back, B(bar, 0), show.spb * 3, on_frac=0.6)

# ===========================================================================
# 3:30  CLIMAX — most elaborate. Overwhelming intensity vs. total darkness.
# ===========================================================================
show.mark("CLIMAX", 84)
for bar in range(84, 92):
    if bar % 2 == 0:
        # OVERWHELM: everything, layered
        show.on(L.all_lights, B(bar, 0), B(bar, 3))
        show.symmetric_out(B(bar, 0), show.spb * 2, trail=4)
        show.alt_lr(B(bar, 0), B(bar, 3), rate_beats=0.2)
        show.window_dip(B(bar, 0), hold=0.6)
        show.falcon_flare(B(bar, 0), hold=1.0)     # Model X bonus
        # beat 4 -> COMPLETE DARKNESS (nothing scheduled)
    else:
        # answer phrase: ripples racing back, rear accents, then dark
        show.ripple(L.front_to_back, B(bar, 0), show.spb * 2, trail=2, reverse=True)
        show.flash(L.all_rear, B(bar, 1), 0.12)
        show.flash(L.all_front, B(bar, 2), 0.12)
        show.mirror_fold(B(bar, 2.5), hold=0.5)

# ===========================================================================
# 3:50  FINALE — strip away to single accents, one giant hit, blackout on note
# ===========================================================================
show.mark("Finale", 92)
# Strip down: a single fading pulse train, fewer each beat
show.flash(L.headlights, B(92, 0), 0.14)
show.flash(L.signature, B(92, 1), 0.10)
show.flash(L.side_marker, B(92, 2), 0.08)
show.flash(L.tail, B(92, 3), 0.06)
# THE final full-vehicle cue on the last downbeat...
final = B(93, 0)
show.on(L.all_lights, final, final + 0.9)
show.window_dip(final, hold=0.9)
show.mirror_fold(final, hold=0.9)
show.charge_port_pop(final, hold=0.9)
show.liftgate_pop(final, hold=0.9)
show.falcon_flare(final, hold=0.9)
# ...then hard blackout. Nothing after `final + 0.9`. Silence + darkness = ending.

# ---------------------------------------------------------------------------
out = os.path.join(os.path.dirname(__file__), "lightshow.fseq")
info = show.write(out, audio_name="lightshow.wav")

print("Wrote", out)
print(info)
print("\nSection map (align these against your audio):")
print(f"{'bar':>4}  {'time':>7}  section")
for s in show.sections:
    t = show.beat(s.start_beat * 4 if False else s.start_beat * 4)  # start_beat stored as bar
    secs = OFFSET_S + s.start_beat * 4 * show.spb
    mm = int(secs // 60); ss = secs - mm * 60
    print(f"{s.start_beat:>4.0f}  {mm:01d}:{ss:05.2f}  {s.name}")
