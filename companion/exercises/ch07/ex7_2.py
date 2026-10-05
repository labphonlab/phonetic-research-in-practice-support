# Exercise 7.2: Measure-specific device comparison
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import math
import numpy as np, parselmouth
base = "companion/data/ch07/synthetic_recordings/"
def clipped_share(x, threshold=0.999, min_run=3):
    # clipping = runs of samples at the ceiling
    at_ceiling = np.abs(x) >= threshold
    edges = np.flatnonzero(np.diff(np.r_[0, at_ceiling.astype(int), 0]))
    runs = edges[1::2] - edges[::2]
    return runs[runs >= min_run].sum() / len(x)
for name in ["synthetic_good", "synthetic_clipped", "synthetic_near_silent"]:
    snd = parselmouth.Sound(base + name + ".wav")
    x = snd.values[0]
    rms_db = 20 * np.log10(np.sqrt(np.mean(x ** 2)))      # dB re full scale, relative only
    f0 = snd.to_pitch_ac(
        time_step=0.01, pitch_floor=75, pitch_ceiling=600
    ).selected_array["frequency"]
    f0 = f0[f0 > 0]                                       # unvoiced frames are coded 0
    med = np.median(f0) if len(f0) else math.nan          # NA, not 0, when no frame is voiced
    print(f"{name}: dur={snd.duration:.2f} s, peak={np.abs(x).max():.4f}, clipped={clipped_share(x):.3f}, "
          f"rms={rms_db:.1f} dBFS, median F0={med:.0f} Hz")
