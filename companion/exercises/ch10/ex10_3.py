# Exercise 10.3: Audit automated duration
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import pandas as pd
root = "companion/data/ch10/synthetic_acoustics/"
d = pd.read_csv(root + "automatic_landmarks.tsv", sep="\t").merge(
    pd.read_csv(root + "reference_landmarks.tsv", sep="\t"), on="observation_id")
d["onset_err"] = d.automatic_onset_ms - d.reference_onset_ms
d["offset_err"] = (
    d.automatic_offset_ms - d.reference_offset_ms
)
d["dur_err"] = d.offset_err - d.onset_err
print(d.extractor_status.value_counts().to_dict())
g = d.groupby("context")[["onset_err", "offset_err", "dur_err"]]
print(g.mean().round(1)); print(g.agg(lambda x: x.abs().median()).round(1))
s = d[(d.onset_err.abs() > 5)
      & (d.offset_err.abs() > 5)
      & (d.dur_err.abs() < 2)]
print(s[["observation_id", "onset_err", "offset_err", "dur_err"]].round(1).head())
for tol in (5, 20):  # milliseconds, fixed in advance
    print(f"within {tol} ms:", d.groupby("context")[["onset_err", "offset_err", "dur_err"]]
          .agg(lambda x: round((x.abs() <= tol).sum() / len(x), 2)).to_dict("index"))
