import numpy as np, wave
SR = 44100
BPM = 140
BEAT = 60 / BPM
BAR = BEAT * 4
S16 = BEAT / 4
DUR = BAR * 20.5 + 0.2
N = int(DUR * SR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(93)

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[:N - i]
    l = gain * np.cos((pan + 1) * np.pi / 4) * np.sqrt(2)
    r = gain * np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)
    L[i:i + len(sig)] += sig * l; R[i:i + len(sig)] += sig * r

def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    at = int(a * SR)
    if at > 0: e[:at] *= np.linspace(0, 1, at)
    return e

def smooth(x, k):
    if k <= 1: return x
    return np.convolve(x, np.ones(k) / k, mode='same')

def hp(x, k=6): return x - smooth(x, k)

def note(n): return 440 * 2 ** ((n - 69) / 12)

# ---------------- instruments ----------------
def kick():
    n = int(0.25 * SR); t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t / 0.03)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.tanh(2.2 * np.sin(ph) * np.exp(-t / 0.12))

def b808(freqs_t, length):
    n = int(length * SR); t = np.arange(n) / SR
    f = freqs_t(t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    e = np.minimum(1, t / 0.004) * np.exp(-t / max(0.35, length * 0.9))
    s = np.sin(ph) + 0.25 * np.sin(2 * ph)
    rel = int(0.03 * SR)
    e[-rel:] *= np.linspace(1, 0, rel)
    return np.tanh(2.6 * s * e) * 0.9

def snare():
    n = int(0.3 * SR); t = np.arange(n) / SR
    nz = hp(rng.standard_normal(n), 3) * np.exp(-t / 0.07)
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.05)
    clap = np.zeros(n)
    for k, o in enumerate([0, 0.011, 0.022]):
        i = int(o * SR); m = n - i
        clap[i:] += hp(rng.standard_normal(m), 4) * np.exp(-np.arange(m) / SR / (0.012 if k < 2 else 0.09))
    return 0.55 * nz + 0.35 * tone + 0.45 * clap

def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR); t = np.arange(n) / SR
    x = hp(hp(rng.standard_normal(n), 2), 2)
    return x * np.exp(-t / (0.08 if open_ else 0.014)) * 0.5

def piano(f, length=1.6):
    n = int(length * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for k, a in [(1, 1), (2, 0.45), (3, 0.22), (4, 0.12), (5, 0.06)]:
        s += a * np.sin(2 * np.pi * f * k * t * (1 + 0.0004 * k)) * np.exp(-t / (0.9 / k ** 0.7))
    return s * np.minimum(1, t / 0.003) * 0.35

def bell(f, length=2.5):
    n = int(length * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t + 1.8 * np.sin(2 * np.pi * f * 3.5 * t) * np.exp(-t / 0.4))
    return s * np.exp(-t / 0.8) * np.minimum(1, t / 0.002) * 0.22

def pad(freqs, length, bright=6):
    n = int(length * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0, 0.13):
            ff = f * 2 ** (det / 12)
            for k in range(1, bright + 1):
                s += np.sin(2 * np.pi * ff * k * t + rng.uniform(0, 6.28)) / k
    s /= (len(freqs) * 3 * 2.2)
    e = np.minimum(1, t / 0.6) * np.minimum(1, (length - t) / 0.6)
    return s * np.clip(e, 0, 1) * 0.3

def riser(length):
    n = int(length * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n); seg = 2048
    for i in range(0, n, seg):
        k = max(1, int(40 * (1 - i / n) ** 2))
        out[i:i + seg] = hp(x[i:i + seg], k) if k > 1 else x[i:i + seg]
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 1800 * (t / length) ** 2) / SR)
    return (0.5 * out + 0.15 * sweep) * (t / length) ** 2.2

def impact(length=2.5):
    n = int(length * SR); t = np.arange(n) / SR
    f = 32 + 90 * np.exp(-t / 0.15)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9)
    nz = smooth(rng.standard_normal(n), 3) * np.exp(-t / 0.25)
    crash = hp(rng.standard_normal(n), 2) * np.exp(-t / 0.9) * 0.25
    return np.tanh(1.8 * boom) * 0.9 + 0.35 * nz + crash

def revcym(length=1.2):
    n = int(length * SR); t = np.arange(n) / SR
    x = hp(rng.standard_normal(n), 2) * np.exp(-t / 0.5)
    return x[::-1] * 0.35

# ---------------- arrangement ----------------
b = lambda n: n * BAR
G1, Bb1, C2, D2, Eb2, F1, A1 = [note(n) for n in (31, 34, 36, 38, 39, 29, 33)]
CHORDS = [[55, 58, 62], [51, 55, 58], [48, 51, 55], [50, 54, 57]]  # Gm Eb Cm D
CH_BASS = [G1, note(27 + 12), note(24 + 12), D2 / 2 * 2]

# vinyl + pads all along (quiet)
crack = np.zeros(N)
clicks = rng.integers(0, N, 900)
crack[clicks] = rng.uniform(-0.6, 0.6, 900)
crack = smooth(crack, 2) + 0.004 * smooth(rng.standard_normal(N), 8)
L += crack * 0.25; R += np.roll(crack, 300) * 0.25

for bar in range(0, 20):
    ch = CHORDS[(bar // 1) % 4] if bar >= 4 else CHORDS[(bar // 1) % 4]
    p = pad([note(n) for n in ch], BAR + 0.6, bright=5 if bar < 4 else 7)
    gain = 0.55 if bar < 4 else 0.4
    if 15 <= bar < 17: gain = 0.6
    add(p, b(bar), gain, -0.35); add(np.roll(p, 700), b(bar), gain, 0.35)

# piano / bell melody (dark arp)
MEL = [(0, 74), (3, 70), (6, 67), (8, 74), (11, 75), (14, 74)]
for bar in range(0, 20):
    if 15 <= bar < 16: continue
    shift = [0, -4, -7, -5][bar % 4]
    for pos, n in MEL:
        if bar < 2 and pos > 8: continue
        add(piano(note(n + shift - 12)), b(bar) + pos * S16, 0.55, 0.15)
        if bar >= 4: add(bell(note(n + shift)), b(bar) + pos * S16, 0.35, -0.2)

# risers & impacts
add(riser(b(1.5)), b(2.5), 0.55)
add(revcym(1.2), b(4) - 1.2, 0.8)
for t_hit, g in [(b(4), 1.0), (b(12), 0.9), (b(16.25), 1.1), (b(19.6), 1.0)]:
    add(impact(), t_hit, g)
for t_hit in [b(5), b(6), b(7), b(8), b(9), b(10), b(14)]:
    add(revcym(0.5), t_hit - 0.5, 0.35)
add(riser(b(1)), b(15.25), 0.5)

# drums + 808
BEAT_BARS = [x for x in range(4, 15)] + [17, 18, 19]
BASS_PAT = [  # (pos16, semis rel to chord root, len16, slide_to)
    [(0, 0, 6, None), (6, 0, 4, None), (10, 3, 3, 5), (14, -2, 2, None)],
    [(0, 0, 5, None), (5, 0, 3, None), (8, 7, 4, 3), (13, 0, 3, None)],
]
for bar in BEAT_BARS:
    t0 = b(bar); root = [G1, note(27 + 12) / 2, note(24 + 12) / 2, D2 / 2][bar % 4]
    root = root if root > 35 else root * 2
    # kick+808
    for pos, semi, ln, slide in BASS_PAT[bar % 2]:
        f0 = root * 2 ** (semi / 12)
        f1 = root * 2 ** (slide / 12) if slide is not None else f0
        length = ln * S16
        def fr(t, f0=f0, f1=f1, length=length):
            k = np.clip((t - length * 0.45) / (length * 0.35), 0, 1)
            return f0 * (f1 / f0) ** k
        add(b808(fr, length), t0 + pos * S16, 0.75)
        add(kick(), t0 + pos * S16, 0.55)
    # snare: beat 3 + ghost
    add(snare(), t0 + 8 * S16, 0.75, 0.05)
    if bar % 2 == 1: add(snare(), t0 + 14 * S16, 0.35, 0.05)
    # hats: 8ths with triplet rolls
    for e8 in range(8):
        tt = t0 + e8 * 2 * S16
        if (bar % 2 == 0 and e8 in (3, 7)) or (bar % 2 == 1 and e8 == 5):
            for k in range(3): add(hat(), tt + k * (2 * S16 / 3), 0.5 + 0.15 * k, 0.25)
        elif bar % 4 == 3 and e8 == 6:
            for k in range(6): add(hat(), tt + k * (2 * S16 / 6), 0.3 + 0.1 * k, 0.25)
        else:
            add(hat(), tt, 0.6 if e8 % 2 == 0 else 0.42, 0.25)
    if bar % 4 == 0: add(hat(True), t0 + 4 * S16, 0.35, -0.25)

# outro sub tail
n = int(2.4 * SR); t = np.arange(n) / SR
add(np.sin(2 * np.pi * G1 * t) * np.exp(-t / 0.8) * 0.6, b(19.6), 1)

# tape-stop at break (fade the end of bar 15 quickly)
i0 = int(b(15) * SR); i1 = int((b(15) + 0.08) * SR)

# master
mix = np.stack([L, R], 1)
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.6) / np.tanh(1.6)
fade = int(1.2 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
fi = int(0.05 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
pcm = (mix * 0.92 * 32767).astype(np.int16)
with wave.open('music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', DUR)
