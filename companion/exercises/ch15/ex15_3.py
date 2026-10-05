# Exercise 15.3: Audit forced alignment
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import pandas as pd
d = "companion/data/ch10/synthetic_acoustics/"
m = pd.read_csv(d + "automatic_landmarks.tsv", sep="\t").merge(
    pd.read_csv(d + "reference_landmarks.tsv", sep="\t"), on="observation_id", validate="one_to_one")
# signed
m["onset_diff_ms"] = (
    m.automatic_onset_ms - m.reference_onset_ms
)
m["offset_diff_ms"] = (
    m.automatic_offset_ms - m.reference_offset_ms
)
m["duration_diff_ms"] = m.offset_diff_ms - m.onset_diff_ms
s = m.groupby("context", group_keys=False).sample(
    n=20, random_state=15
)
# declared in advance
tol = 20.0
bad = (
    (s.onset_diff_ms.abs() > tol)
    | (s.offset_diff_ms.abs() > tol)
    | s.offset_diff_ms.isna()
)
print(s.assign(bad=bad).groupby("context").agg(n=("bad", "size"), failed=("offset_diff_ms", lambda x: x.isna().sum()),
      onset_median=("onset_diff_ms", "median"), offset_median=("offset_diff_ms", "median"),
      dur_sd=("duration_diff_ms", "std"), share_over_tol=("bad", "mean")).round(2))
