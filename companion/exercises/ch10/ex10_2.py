# Exercise 10.2: Diagnose a pitch tracker
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import parselmouth as pm, pandas as pd, numpy as np
root = "companion/data/ch10/synthetic_acoustics/"
iv = pd.read_csv(root + "interval_manifest.tsv", sep="\t")
profiles = {"F0_LOW": (50, 200), "F0_GENERAL": (70, 350),
            "F0_HIGH": (120, 500)}
rows = []
for r in iv.itertuples():
    snd = pm.Sound(root + f"audio/{r.file_id}.wav").extract_part(r.interval_start_s, r.interval_end_s)
    for pid, (fl, ce) in profiles.items():
        f0 = snd.to_pitch_ac(
            time_step=0.01, pitch_floor=fl, pitch_ceiling=ce
        ).selected_array["frequency"]
        v = f0[f0 > 0]
        q = np.percentile(v, [5, 50, 95]).round(1) if len(v) else [np.nan] * 3
        rows.append(dict(file=r.file_id, profile=pid, window_ms=round(3000 / fl), frames=len(f0),
            missing=round(1 - len(v) / len(f0), 2), p05=q[0], median=q[1], p95=q[2],
            near_limit=round(float(np.mean(
                (v < fl * 1.05) | (v > ce * 0.95))), 2)
            if len(v) else np.nan))
print(pd.DataFrame(rows).to_string(index=False))
