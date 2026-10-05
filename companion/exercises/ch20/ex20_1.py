# Exercise 20.1: Classify the research objects
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import pathlib, pandas as pd
ROLE = {
    ".wav": "recording", ".TextGrid": "annotation",
    ".praat": "script", ".py": "script", ".R": "script",
    ".qmd": "document", ".ipynb": "notebook", ".png": "figure",
    ".tsv": "measurement", ".yaml": "configuration",
}
rows = [
    {"path": str(p), "role": ROLE.get(p.suffix, "unclassified")}
    for p in pathlib.Path("my_project").rglob("*")
    if p.is_file()
]
inv = pd.DataFrame(rows).assign(
    owner="", access_class="", license="",
    source_or_generator="",
    release_disposition="exclude_until_decided",
)
inv.to_csv("inventory.tsv", sep="\t", index=False)
m = pd.read_csv(
    "companion/data/ch20/release_candidate/release_manifest.tsv",
    sep="\t",
    dtype=str,
)
need = [
    "rights_holder", "license_or_agreement", "access_class",
    "source_or_generator", "version", "sha256", "citation_id",
]
# placeholders still open
print(
    m[need]
    .apply(
        lambda c: c.str.contains(
            "AUTHOR_INPUT_REQUIRED|PENDING", na=False
        )
    )
    .sum()
)
