# Exercise 20.2: Build protected and public routes
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import sys, pathlib, yaml, pandas as pd
R = pathlib.Path("companion/data/ch20/release_candidate")
# synthetic fixture
PUBLIC_INPUT = pathlib.Path(
    "companion/data/ch17/synthetic_regression/analysis_data.tsv"
)
def resolve(route):
    profile = yaml.safe_load((R / f"{route}_profile.yaml").read_text())
    placeholder = "AUTHORIZED_LOCAL_PATH_REQUIRED"
    if profile["route"] == "protected":
        if profile["canonical_input"].startswith(placeholder):
            sys.exit(
                "protected route: "
                "no authorized input path in the profile"
            )
        return pathlib.Path(profile["canonical_input"])
    # the public profile admits synthetic files only
    return PUBLIC_INPUT
# identical code on both routes
def transform(path):
    return (
        pd.read_csv(path, sep="\t")
        .groupby("condition")["outcome"]
        .agg(["count", "mean"])
        .round(3)
    )
route = sys.argv[1]
pathlib.Path("derived").mkdir(exist_ok=True)
transform(resolve(route)).to_csv(
    f"derived/summary_{route}.tsv", sep="\t"
)
