# Exercise 15.4: Build a cross-corpus compatibility table
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import pandas as pd
d = "companion/data/ch15/synthetic_corpus/"
cmap = pd.read_csv(d + "cross_corpus_map.tsv", sep="\t")
print(cmap.compatibility.value_counts().to_dict())   # compatible 4, restricted 2, incompatible 2
hits = pd.read_csv(d + "searchable_hits.tsv", sep="\t")
cells = hits.groupby(["style", "era"]).corpus_id.nunique().rename("n_corpora").reset_index()
print(int((cells.n_corpora == 2).sum()))             # 0: corpus and era are fully confounded
