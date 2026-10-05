# Exercise 20.4: Write the availability and stewardship statement
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import pathlib, pandas as pd, yaml
R = pathlib.Path("companion/data/ch20/release_candidate")
m = pd.read_csv(R / "release_manifest.tsv", sep="\t", dtype=str)
cit = yaml.safe_load((R / "citation_metadata.yaml").read_text())
text = (R / "availability_statement_template.md").read_text()
media = {".wav", ".mp3", ".mp4", ".flac", ".m4a", ".mov"}
facts = {
    "version": sorted(m["version"].unique()),
    "files": len(m),
    "redistributable": int(
        (m["redistributable"] == "true").sum()
    ),
    "personal_data": int(
        (m["contains_personal_data"] == "true").sum()
    ),
    "restricted": int(
        (m["contains_restricted_content"] == "true").sum()
    ),
    "media_files": int(
        m["path"].str.lower().str[-4:].isin(media).sum()
    ),
    "doi": cit["version_specific_identifier"],
    "deposit": cit["deposit_status"],
}
print(facts)
print(
    "states no deposit or DOI:",
    "No public deposit or DOI" in text,
    "| matches fields:",
    facts["doi"] == "NOT_CREATED"
    and facts["deposit"] == "NOT_DEPOSITED",
)
print(
    "states no recordings:",
    "no participant recordings" in text,
    "| matches manifest:",
    facts["media_files"] == 0,
)
