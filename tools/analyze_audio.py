#!/usr/bin/env python3
"""
analyze_audio.py — detect duration, tempo, and the first-downbeat offset of an
audio file, so a show can be auto-aligned to it.

WAV is read with the standard library (no installs). MP3/M4A is supported only
if `ffmpeg` is available (it's decoded to a temp WAV first).

Usage:
    python3 analyze_audio.py path/to/lightshow.wav
    python3 analyze_audio.py path/to/song.mp3        # needs ffmpeg

Prints: duration, estimated BPM, and a suggested OFFSET_S (seconds until the
first strong onset / likely downbeat). Use OFFSET_S in a show's build script.
"""
import sys
import os
import wave
import struct
import subprocess
import tempfile
import numpy as np


def _load_wav(path):
    with wave.open(path, "rb") as w:
        n = w.getnframes()
        sr = w.getframerate()
        ch = w.getnchannels()
        sw = w.getsampwidth()
        raw = w.readframes(n)
    dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(sw)
    if dtype is None:
        raise SystemExit(f"Unsupported WAV sample width: {sw} bytes")
    data = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    if ch > 1:
        data = data.reshape(-1, ch).mean(axis=1)   # downmix to mono
    if data.size:
        data /= (np.abs(data).max() or 1.0)
    return data, sr


def _load_any(path):
    if path.lower().endswith(".wav"):
        return _load_wav(path)
    # try ffmpeg -> temp wav
    from shutil import which
    if which("ffmpeg") is None:
        raise SystemExit(
            "This is not a WAV and ffmpeg is not installed.\n"
            "Either provide a .wav, or install ffmpeg (e.g. `brew install ffmpeg`)."
        )
    tmp = os.path.join(tempfile.gettempdir(), "_aa_tmp.wav")
    subprocess.run(
        ["ffmpeg", "-y", "-i", path, "-ac", "1", "-ar", "22050", tmp],
        check=True, capture_output=True,
    )
    return _load_wav(tmp)


def analyze(path):
    x, sr = _load_any(path)
    dur = len(x) / sr

    # --- onset envelope: positive spectral/energy flux over short frames ---
    hop = 512
    win = 1024
    frames = max(1, (len(x) - win) // hop)
    env = np.empty(frames)
    prev = 0.0
    for i in range(frames):
        seg = x[i * hop: i * hop + win]
        e = float(np.sqrt(np.mean(seg * seg)))   # RMS energy
        env[i] = max(0.0, e - prev)               # positive flux = onset-ish
        prev = e
    fps = sr / hop
    if env.max() > 0:
        env /= env.max()

    # --- tempo via autocorrelation of the onset envelope ---
    e = env - env.mean()
    ac = np.correlate(e, e, mode="full")[len(e) - 1:]
    bpm_lo, bpm_hi = 60, 200
    lag_lo = int(fps * 60.0 / bpm_hi)
    lag_hi = int(fps * 60.0 / bpm_lo)
    lag_hi = min(lag_hi, len(ac) - 1)
    best_lag = lag_lo + int(np.argmax(ac[lag_lo:lag_hi])) if lag_hi > lag_lo else lag_lo
    bpm = 60.0 * fps / best_lag if best_lag else 0.0
    # fold into a sane musical range
    while bpm > 180:
        bpm /= 2
    while bpm and bpm < 70:
        bpm *= 2

    # --- first strong onset (suggested downbeat offset) ---
    thresh = 0.35
    idx = np.argmax(env > thresh) if (env > thresh).any() else 0
    offset_s = idx / fps

    return {"duration_s": dur, "sr": sr, "bpm": round(bpm, 2),
            "offset_s": round(offset_s, 3)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python3 analyze_audio.py <audio file>")
    info = analyze(sys.argv[1])
    print("Audio analysis")
    print(f"  file        : {sys.argv[1]}")
    print(f"  duration    : {int(info['duration_s']//60)}:{info['duration_s']%60:05.2f}"
          f"  ({info['duration_s']:.2f} s)")
    print(f"  sample rate : {info['sr']} Hz")
    print(f"  est. tempo  : {info['bpm']} BPM")
    print(f"  first onset : {info['offset_s']} s   <-- try this as OFFSET_S")
    print("\nNext: set OFFSET_S in the show's build_show.py, then re-run it.")
