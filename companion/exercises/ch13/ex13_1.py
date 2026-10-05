# Exercise 13.1: Build an observability matrix
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import pandas as pd
cols = ["modality", "direct_observation", "proxy", "invisible_structures",
        "spatial_resolution", "temporal_resolution", "calibration",
        "burden", "sync_requirement"]
mods = ["EMA", "ultrasound", "EPG", "rtMRI",
        "aerodynamic_or_laryngeal"]
m = pd.DataFrame({"modality": mods}).reindex(columns=cols)
m.to_csv("observability_matrix.tsv", sep="\t", index=False)
print(m.shape)  # (5, 9)
