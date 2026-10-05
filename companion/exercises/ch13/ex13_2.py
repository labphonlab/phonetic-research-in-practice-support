# Exercise 13.2: Reconstruct a coordinate chain
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import numpy as np, pandas as pd
d = "companion/data/ch13/synthetic_multimodal/"
xy = pd.read_csv(d + "native_coordinates.tsv", sep="\t")
tm = pd.read_csv(d + "transformation_matrices.tsv", sep="\t")
cols = ["m11","m12","m13","m21","m22","m23","m31","m32","m33"]
def mat(frame, tid):
    row = tm[(tm.frame_index == frame) & (tm.transform_id == tid)]
    return row[cols].to_numpy().reshape(3, 3)
def to_head(r):
    return (mat(r.frame_index, "native_to_head") @ [r.native_x_mm, r.native_y_mm, 1])[:2]
xy[["head_x", "head_y"]] = [to_head(r) for r in xy.itertuples()]
w = xy.pivot(index="frame_index", columns="sensor_id", values=["head_x", "head_y"])
dist = np.hypot(w[("head_x", "REF_A")] - w[("head_x", "REF_B")],
                w[("head_y", "REF_A")] - w[("head_y", "REF_B")])
bad = (dist - 40.0).abs() > 0.75
print(len(dist), int(bad.sum()))  # 238 27
