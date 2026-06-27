#!/usr/bin/env python3
"""
build_beatmap.py — analyze a WAV and emit a per-beat "beat map" JSON that a show
script can use to choreograph directly off the waveform.

For each beat it records: time, RMS energy (loudness), onset/transient strength,
bar + beat-in-bar position, and the song section it falls in. Tempo is assumed
steady (Overcompensate is a locked 95 BPM); the downbeat phase is found by a
comb-filter search over the onset envelope.

Usage:
    python3 build_beatmap.py lightshow.wav beatmap.json [bpm] [sections.json]

Sections describe the song's structure as [start_s, name, tier] rows. Pass a
per-show sections.json (4th arg) to override; otherwise a sibling `sections.json`
next to the output is used if present, else the built-in default below.
"""
import os
import sys
import json
import wave
import numpy as np

# (start_s, name, tier)  tier: 0 dark .. 3 peak — a hint; real energy still modulates.
DEFAULT_SECTIONS = [
    (0.0,   "silence_intro", 0),
    (5.0,   "intro",         1),
    (17.0,  "verse1",        2),
    (49.0,  "drop1",         3),
    (65.0,  "lull",          1),
    (67.0,  "verse2",        2),
    (107.0, "chorus_body",   3),
    (160.0, "transition",    1),
    (162.0, "build2",        3),
    (188.0, "breakdown",     1),
    (196.0, "rebuild",       2),
    (217.0, "climax",        3),
    (238.0, "final_hit",     3),
    (239.0, "outro_silence", 0),
]

SECTIONS = DEFAULT_SECTIONS          # overridden in main() if a sections file is given


def _load_sections(out_path):
    """4th CLI arg, else sibling sections.json, else the built-in default."""
    path = None
    if len(sys.argv) > 4:
        path = sys.argv[4]
    else:
        sib = os.path.join(os.path.dirname(os.path.abspath(out_path)), "sections.json")
        if os.path.exists(sib):
            path = sib
    if path:
        rows = json.load(open(path))
        return [(float(r[0]), str(r[1]), int(r[2])) for r in rows], path
    return DEFAULT_SECTIONS, None


def section_for(t):
    name, tier = SECTIONS[0][1], SECTIONS[0][2]
    for s, n, ti in SECTIONS:
        if t >= s:
            name, tier = n, ti
        else:
            break
    return name, tier


def main():
    global SECTIONS
    wav = sys.argv[1] if len(sys.argv) > 1 else "lightshow.wav"
    out = sys.argv[2] if len(sys.argv) > 2 else "beatmap.json"
    bpm = float(sys.argv[3]) if len(sys.argv) > 3 else 95.0
    SECTIONS, secpath = _load_sections(out)
    if secpath:
        print(f"Using sections from {secpath}")

    w = wave.open(wav, "rb")
    sr = w.getframerate()
    ch = w.getnchannels()
    n = w.getnframes()
    x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float64)
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    x /= (np.abs(x).max() or 1.0)
    dur = len(x) / sr

    # onset envelope (positive RMS flux)
    hop = 256
    win = 1024
    nf = (len(x) - win) // hop
    env = np.zeros(nf)
    prev = 0.0
    for i in range(nf):
        seg = x[i * hop: i * hop + win]
        e = float(np.sqrt(np.mean(seg * seg)))
        env[i] = max(0.0, e - prev)
        prev = e
    fps = sr / hop
    env /= (env.max() or 1.0)

    P = 60.0 / bpm * fps                       # frames per beat
    # comb-filter: find beat phase that maximizes onset energy in the strong region
    def beat_score(phase):
        s = 0.0
        b = phase + int(17 * fps)
        end = int(min(120, dur) * fps)
        while b < end:
            bi = int(round(b))
            if 0 <= bi < nf:
                s += env[bi]
            b += P
        return s
    phase = max(np.arange(0, P, 0.5), key=beat_score)
    # downbeat: of 4 candidate beats, the loudest is beat 1
    def bar_score(ph0):
        s = 0.0
        b = ph0 + int(17 * fps)
        end = int(min(120, dur) * fps)
        while b < end:
            bi = int(round(b))
            if 0 <= bi < nf:
                s += env[bi]
            b += 4 * P
        return s
    downbeat = max([phase + k * P for k in range(4)], key=bar_score)
    downbeat_s = (downbeat % (4 * P)) / fps
    P_s = P / fps

    # walk beats across the whole track
    beats = []
    bar = 0
    bib = 0
    t = downbeat_s
    while t < dur:
        f = int(round(t * fps))
        # energy over this beat
        a = int(t * sr); b = int(min(len(x), (t + P_s) * sr))
        rms = float(np.sqrt(np.mean(x[a:b] ** 2))) if b > a else 0.0
        # onset strength near the beat
        w0 = max(0, f - int(0.04 * fps)); w1 = min(nf, f + int(0.10 * fps))
        onset = float(env[w0:w1].max()) if w1 > w0 else 0.0
        sec, tier = section_for(t)
        beats.append({
            "i": len(beats), "t": round(t, 4),
            "bar": bar, "beat_in_bar": bib,
            "e": round(rms, 4), "onset": round(onset, 4),
            "section": sec, "tier": tier,
        })
        bib += 1
        if bib == 4:
            bib = 0; bar += 1
        t += P_s

    # normalize energy 0..1 across the musical body
    es = np.array([b["e"] for b in beats])
    lo, hi = np.percentile(es, 5), np.percentile(es, 98)
    for b in beats:
        b["e_norm"] = round(float(min(1.0, max(0.0, (b["e"] - lo) / (hi - lo + 1e-9)))), 3)
        b["onset_norm"] = round(b["onset"], 3)

    data = {
        "source": wav, "bpm": bpm, "duration_s": round(dur, 3),
        "downbeat_s": round(downbeat_s, 4), "beat_period_s": round(P_s, 5),
        "n_beats": len(beats),
        "sections": [{"start_s": s, "name": n, "tier": ti} for s, n, ti in SECTIONS],
        "beats": beats,
    }
    with open(out, "w") as f:
        json.dump(data, f)
    print(f"Wrote {out}: {len(beats)} beats, bpm={bpm}, downbeat={downbeat_s:.3f}s, dur={dur:.1f}s")
    # quick section energy summary
    print("Section avg energy:")
    for s, n, ti in SECTIONS:
        sb = [b["e_norm"] for b in beats if b["section"] == n]
        if sb:
            print(f"  {n:16} tier{ti}  e≈{sum(sb)/len(sb):.2f}  ({len(sb)} beats)")


if __name__ == "__main__":
    main()
