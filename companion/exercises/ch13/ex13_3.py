# Exercise 13.3: Audit multimodal synchronization
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import numpy as np, pandas as pd
d = "companion/data/ch13/synthetic_multimodal/"
ev = pd.read_csv(d + "calibration_sync_events.tsv", sep="\t")
ev = ev[ev.event_status == "observed"]
r, a = ev.reference_time_s.to_numpy(), ev.articulatory_time_s.to_numpy()
offset = np.median(a - r)
res_offset = a - (r + offset)
slope, intercept = np.polyfit(r, a, 1)
res_drift = a - (slope * r + intercept)
# 22.93 0.98
print(round(np.abs(res_offset).max() * 1e3, 2),
      round(np.abs(res_drift).max() * 1e3, 2))
xy = pd.read_csv(d + "native_coordinates.tsv", sep="\t")
t = xy.native_time_s.unique()
print(int(round((t.max() - t.min()) / 0.01)) + 1 - len(t))  # 2 dropped frames
