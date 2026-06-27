"""
tesla_lightshow.py  —  A from-scratch Tesla Light Show (.fseq) engine.

Generates Tesla-compatible FSEQ v2.0 *uncompressed* sequences WITHOUT xLights.
The channel map, value ranges, and binary layout were reverse-engineered directly
from Tesla's official xLights project and a real example .fseq in
https://github.com/teslamotors/light-show :

  * Format ........ FSEQ v2.0, V2 Uncompressed, header @ offset, 48 channels
  * Frame step .... 20 ms (50 fps)  [validator minimum 15 ms]
  * Lights ........ binary: 0 = off, 255 = on
  * Closures ...... partial-range: 0 = rest, MAX = fully actuated (per channel)

A single 48-channel file plays on EVERY Tesla — each car only actuates the
channels it physically has, so model-specific channels (e.g. Falcon doors) are
simply ignored by cars that lack them.  That makes every show cross-model.

Usage (see shows/<name>/build_show.py for a full example):

    from tesla_lightshow import Show, L
    show = Show(bpm=95, total_seconds=238)
    show.on(L.headlights, t0=10.0, t1=10.5)        # seconds
    show.flash(L.all_front, beat=8)                 # musical beats
    show.write("lightshow.fseq")
"""

import struct
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# CHANNEL MAP  (0-indexed; order verified against Tesla's model + a real fseq)
# ---------------------------------------------------------------------------
CHANNELS = {
    "left_outer_main": 0,  "right_outer_main": 1,
    "left_inner_main": 2,  "right_inner_main": 3,
    "left_signature": 4,   "right_signature": 5,
    "left_ch4": 6,         "right_ch4": 7,
    "left_ch5": 8,         "right_ch5": 9,
    "left_ch6": 10,        "right_ch6": 11,
    "left_front_turn": 12, "right_front_turn": 13,
    "left_front_fog": 14,  "right_front_fog": 15,
    "left_aux_park": 16,   "right_aux_park": 17,
    "left_side_marker": 18,"right_side_marker": 19,
    "left_side_repeater": 20, "right_side_repeater": 21,
    "left_rear_turn": 22,  "right_rear_turn": 23,
    "brake": 24,
    "left_tail": 25,       "right_tail": 26,
    "reverse": 27,
    "rear_fog": 28,
    "license": 29,
    # --- Closures (partial-range; MAX = fully actuated) ---
    "left_falcon": 30,     "right_falcon": 31,       # Model X only
    "left_front_door": 32, "right_front_door": 33,
    "left_mirror": 34,     "right_mirror": 35,
    "left_front_window": 36, "left_rear_window": 37,
    "right_front_window": 38, "right_rear_window": 39,
    "liftgate": 40,
    "left_front_handle": 41, "left_rear_handle": 42,
    "right_front_handle": 43, "right_rear_handle": 44,
    "charge_port": 45,
}
CHANNEL_COUNT = 48          # Tesla pads the 46 real channels to 48
STEP_MS = 20                # 50 fps

# Full-actuation value per closure channel (extracted from a real Tesla fseq).
# Lights default to 255 (binary on/off).
CLOSURE_MAX = {
    30: 127, 31: 127,          # falcon doors
    32: 63,  33: 63,           # front doors
    34: 191, 35: 191,          # mirrors (fold)
    36: 127, 37: 127, 38: 127, 39: 127,   # windows (down)
    40: 127,                   # liftgate
    41: 191, 42: 191, 43: 191, 44: 191,   # door handles
    45: 127,                   # charge port
}


def _full_value(ch):
    return CLOSURE_MAX.get(ch, 255)


# ---------------------------------------------------------------------------
# NAMED GROUPS & ORDERED SEQUENCES  (for choreography)
# ---------------------------------------------------------------------------
def _c(*names):
    return [CHANNELS[n] for n in names]


class L:
    """Light/closure groups. Reference these from show scripts."""
    # symmetric pairs (left, right) — useful for mirror-image choreography
    outer_main   = _c("left_outer_main", "right_outer_main")
    inner_main   = _c("left_inner_main", "right_inner_main")
    signature    = _c("left_signature", "right_signature")
    ch456        = _c("left_ch4","right_ch4","left_ch5","right_ch5","left_ch6","right_ch6")
    front_turn   = _c("left_front_turn", "right_front_turn")
    front_fog    = _c("left_front_fog", "right_front_fog")
    aux_park     = _c("left_aux_park", "right_aux_park")
    side_marker  = _c("left_side_marker", "right_side_marker")
    side_repeater= _c("left_side_repeater", "right_side_repeater")
    rear_turn    = _c("left_rear_turn", "right_rear_turn")
    tail         = _c("left_tail", "right_tail")
    brake        = _c("brake")
    reverse      = _c("reverse")
    rear_fog     = _c("rear_fog")
    license      = _c("license")

    headlights   = outer_main + inner_main
    drl          = signature + aux_park

    # zone rollups
    all_front    = (outer_main + inner_main + signature + ch456 + front_turn +
                    front_fog + aux_park)
    all_rear     = (rear_turn + tail + brake + reverse + rear_fog + license)
    all_sides    = side_marker + side_repeater
    all_lights   = all_front + all_sides + all_rear

    # closures
    windows      = _c("left_front_window","left_rear_window","right_front_window","right_rear_window")
    mirrors      = _c("left_mirror", "right_mirror")
    charge_port  = _c("charge_port")
    liftgate     = _c("liftgate")
    falcon       = _c("left_falcon", "right_falcon")   # Model X bonus
    front_doors  = _c("left_front_door", "right_front_door")
    handles      = _c("left_front_handle","left_rear_handle","right_front_handle","right_rear_handle")

    # left half / right half (for cross-body sweeps)
    left_side    = _c("left_outer_main","left_inner_main","left_signature","left_front_turn",
                      "left_front_fog","left_side_marker","left_side_repeater","left_rear_turn","left_tail")
    right_side   = _c("right_outer_main","right_inner_main","right_signature","right_front_turn",
                      "right_front_fog","right_side_marker","right_side_repeater","right_rear_turn","right_tail")

    # Ordered front -> back chain (each step is a L/R pair) for traveling waves
    front_to_back = [
        outer_main + inner_main,    # nose
        signature + aux_park,
        front_fog,
        front_turn,
        side_marker,
        side_repeater,
        rear_turn,
        tail + brake,
        reverse + rear_fog + license,  # tail-most
    ]
    # Ordered center -> edge (expanding pulse / ripple)
    center_out = [
        inner_main,
        signature,
        outer_main,
        front_turn,
        front_fog,
        side_marker,
        side_repeater,
    ]


# ---------------------------------------------------------------------------
# SHOW  — a frame buffer plus high-level, musically-aware choreography
# ---------------------------------------------------------------------------
@dataclass
class Section:
    name: str
    start_beat: float


class Show:
    def __init__(self, bpm=120.0, total_seconds=60.0, offset_s=0.0):
        self.bpm = float(bpm)
        self.spb = 60.0 / self.bpm           # seconds per beat
        self.offset_s = offset_s             # global nudge to align to audio
        self.nframes = int(round(total_seconds / (STEP_MS / 1000.0)))
        self.buf = [bytearray(CHANNEL_COUNT) for _ in range(self.nframes)]
        self.sections = []

    # --- time helpers --------------------------------------------------------
    def beat(self, b):
        """Beat number -> seconds (with global offset)."""
        return self.offset_s + b * self.spb

    def bar(self, n, beat_in_bar=0.0):
        return self.beat(n * 4 + beat_in_bar)

    def _frame(self, t):
        return int(round(t / (STEP_MS / 1000.0)))

    def mark(self, name, start_beat):
        self.sections.append(Section(name, start_beat))

    # --- core writer ---------------------------------------------------------
    def _set(self, channels, t0, t1, value):
        f0 = max(0, self._frame(t0))
        f1 = min(self.nframes, self._frame(t1))
        if isinstance(channels, int):
            channels = [channels]
        for f in range(f0, f1):
            row = self.buf[f]
            for ch in channels:
                v = value if value is not None else _full_value(ch)
                # never exceed a closure's mechanical max
                row[ch] = min(v, _full_value(ch))

    # --- primitives (times in SECONDS) --------------------------------------
    def on(self, channels, t0, t1, value=None):
        """Hold channels on across [t0, t1) seconds."""
        self._set(channels, t0, t1, value)

    def flash(self, channels, t, dur=0.08, value=None):
        """Sharp accent flash."""
        self._set(channels, t, t + dur, value)

    def strobe(self, channels, t0, t1, period_s, duty=0.5, value=None):
        """Rapid on/off between t0 and t1."""
        t = t0
        while t < t1:
            self._set(channels, t, t + period_s * duty, value)
            t += period_s

    def chase(self, seq, t0, dur, on_frac=1.0, value=None, reverse=False):
        """Light each element of `seq` in turn across `dur` seconds.
        on_frac=1.0 holds (cumulative look handled by caller); <1 = moving dot."""
        steps = list(seq)
        if reverse:
            steps = list(reversed(steps))
        n = len(steps)
        slot = dur / n
        for i, el in enumerate(steps):
            s = t0 + i * slot
            self._set(el, s, s + slot * on_frac, value)

    def ripple(self, rings, t0, dur, trail=1, value=None, reverse=False):
        """Expanding pulse: ring i lights then fades as the wave moves out.
        trail = how many rings stay lit behind the leading edge."""
        rings = list(rings)
        if reverse:
            rings = list(reversed(rings))
        n = len(rings)
        slot = dur / n
        for i, ring in enumerate(rings):
            s = t0 + i * slot
            e = t0 + min(n, i + trail) * slot
            self._set(ring, s, e, value)

    def alt_lr(self, t0, t1, rate_beats, left=None, right=None, value=None):
        """Alternate left/right groups every `rate_beats`."""
        left = left if left is not None else L.left_side
        right = right if right is not None else L.right_side
        step = rate_beats * self.spb
        t = t0
        i = 0
        while t < t1:
            self._set(left if i % 2 == 0 else right, t, min(t + step, t1), value)
            t += step
            i += 1

    def symmetric_out(self, t0, dur, value=None, trail=2):
        """Mirror-image expanding pulse from car center outward."""
        self.ripple(L.center_out, t0, dur, trail=trail, value=value)

    def wave_back(self, t0, dur, value=None, trail=2, reverse=False):
        """Traveling wave front -> back (or reverse)."""
        self.ripple(L.front_to_back, t0, dur, trail=trail, value=value, reverse=reverse)

    # --- closure moves (slow; give them room) -------------------------------
    def window_dip(self, t, hold=0.6, which=None):
        which = which if which is not None else L.windows
        self._set(which, t, t + hold, None)        # None -> each channel's max

    def mirror_fold(self, t, hold=0.8):
        self._set(L.mirrors, t, t + hold, None)

    def charge_port_pop(self, t, hold=0.5):
        self._set(L.charge_port, t, t + hold, None)

    def liftgate_pop(self, t, hold=0.8):
        self._set(L.liftgate, t, t + hold, None)

    def falcon_flare(self, t, hold=1.0):
        """Model X bonus — ignored by other models."""
        self._set(L.falcon, t, t + hold, None)

    # --- output --------------------------------------------------------------
    def write(self, path, audio_name="lightshow.wav"):
        body = bytearray()
        for row in self.buf:
            body += row

        def varheader(code, text):
            data = text.encode("utf-8") + b"\x00"
            length = 4 + len(data)          # length field counts itself(2)+code(2)+data
            return struct.pack("<H", length) + code + data

        var = varheader(b"mf", audio_name) + varheader(b"sp", "Tesla LightShow Generator")
        fixed = 32
        data_off = fixed + len(var)
        pad = (-data_off) % 4
        data_off += pad

        h = bytearray()
        h += b"PSEQ"
        h += struct.pack("<H", data_off)
        h += bytes([0, 2])                  # minor, major  -> v2.0
        h += struct.pack("<H", fixed)       # offset to variable headers
        h += struct.pack("<I", CHANNEL_COUNT)
        h += struct.pack("<I", self.nframes)
        h += bytes([STEP_MS, 0, 0, 0, 0, 0])  # step, flags, compression, blocks, sparse, flags2
        h += struct.pack("<Q", 0x0005EF8F2802D637)  # fixed unique id
        assert len(h) == 32, len(h)
        h += var
        h += b"\x00" * pad

        with open(path, "wb") as f:
            f.write(bytes(h) + bytes(body))
        return {
            "frames": self.nframes,
            "channels": CHANNEL_COUNT,
            "step_ms": STEP_MS,
            "duration_s": round(self.nframes * STEP_MS / 1000.0, 2),
            "bytes": len(h) + len(body),
        }


if __name__ == "__main__":
    # tiny smoke test
    s = Show(bpm=95, total_seconds=4)
    s.flash(L.all_front, s.beat(0))
    s.symmetric_out(s.beat(1), 1.0)
    info = s.write("/tmp/_smoke.fseq")
    print("wrote", info)
