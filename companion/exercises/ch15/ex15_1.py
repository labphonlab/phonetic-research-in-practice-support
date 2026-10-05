# Exercise 15.1: Define the five populations
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import itertools, pandas as pd, yaml
d = "companion/data/ch15/synthetic_corpus/"
dims = yaml.safe_load(open(d + "target_population.yaml"))["dimensions"]
keys = ["region", "style", "era"]
grid = pd.DataFrame(
    list(itertools.product(*[dims[k] for k in keys])),
    columns=keys,
)
hits = pd.read_csv(d + "searchable_hits.tsv", sep="\t")
n = hits.groupby(keys).size().rename("searchable_hits").reset_index()
grid = grid.merge(n, how="left", on=keys).fillna(
    {"searchable_hits": 0}
)
# 18 10
print(len(grid), int((grid.searchable_hits == 0).sum()))
