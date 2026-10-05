# Exercise 13.4: Stress-test a kinematic landmark
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import numpy as np, pandas as pd, yaml
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
d = "companion/data/ch13/synthetic_multimodal/"
tr = pd.read_csv(d + "validated_trajectories.tsv", sep="\t")
profiles = yaml.safe_load(open(d + "landmark_profiles.yaml"))["profiles"]
out = []
for (ev, shape), g in tr.groupby(["event_id", "shape_class"]):
    y = g.displacement_mm.to_numpy(float)
    ok = np.isfinite(y)
    if ok.mean() < 0.85 or np.ptp(y[ok]) < 2.0:
        out.append((ev, shape, "all", 0, "nonidentifiable"))
        continue
    y = np.interp(np.arange(len(y)), np.flatnonzero(ok), y[ok])
    for p in profiles:
        s = (gaussian_filter1d(y, p["filter_sigma_samples"])
             if p["filter"] == "gaussian" else y)
        v = np.abs(np.gradient(s, 0.005))
        pk, _ = find_peaks(v, height=p["peak_fraction"] * v.max())
        out.append((ev, shape, p["profile_id"], len(pk), "candidates"))
res = pd.DataFrame(
    out, columns=["event", "shape", "profile", "n_candidates", "status"]
)
# low_excursion 4, missing 4
print(res[res.status == "nonidentifiable"].groupby("shape").size())
