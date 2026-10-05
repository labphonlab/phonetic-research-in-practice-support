# Exercise 10.1: Write a measurement specification
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import yaml, parselmouth as pm, numpy as np
root = "companion/data/ch10/synthetic_acoustics/"
spec = yaml.safe_load(open(root + "acoustic_measurement_spec.yaml"))
step = spec["window"]["frame_step_ms"] / 1000
snd = pm.Sound(root + "audio/SYN_VOWEL_01.wav").extract_part(0.1, 0.5)
print("Praat", pm.PRAAT_VERSION, "| raw autocorrelation | time step", step, "s")
for p in spec["sensitivity"]["prespecified_profiles"]:
    if p["measure"] == "f0":
        f0 = snd.to_pitch_ac(
            time_step=step, pitch_floor=p["floor_hz"],
            pitch_ceiling=p["ceiling_hz"],
        ).selected_array["frequency"]
        # unvoiced frames are stored as 0
        f0[f0 == 0] = np.nan
        print(p["profile_id"], p["floor_hz"], p["ceiling_hz"], len(f0),
              round(float(np.nanmedian(f0)), 1) if np.isfinite(f0).any() else "NA")
