# Exercise 16.4: Perform a clean-room run
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
import hashlib, json, math, pathlib
import pandas as pd
D = pathlib.Path("companion/data/ch16/synthetic_pipeline")
out_dir = pathlib.Path("clean_run"); out_dir.mkdir(exist_ok=True)
src = pd.read_csv(D / "source_measurements.tsv", sep="\t")
corr = pd.read_csv(D / "correction_table.tsv", sep="\t")
a = src.merge(corr[["token_id", "corrected_value"]], on="token_id", how="left")
a = a[a.measurement_status == "observed"].copy()
a["analysis_value"] = a.corrected_value.fillna(a.raw_value)
a["duration_ms"] = (a.end_ms - a.start_ms).astype(float)
cols = ["token_id", "speaker_id", "item_id", "analysis_value", "duration_ms",
        "measurement_status", "unicode_label", "data_status"]
a[cols].to_csv(
    out_dir / "analysis_table.tsv",
    sep="\t",
    index=False,
    lineterminator="\r\n",
)

# --- Part 2 of 2 ---
exp = pd.read_csv(D / "expected_artifacts.tsv", sep="\t").set_index("artifact_path")
sha = hashlib.sha256(
    (out_dir / "analysis_table.tsv").read_bytes()
).hexdigest()
# True
print(sha == exp.loc["analysis_table.tsv", "expected_sha256"])
ref = json.load(open(D / "expected" / "summary.json"))
# True
print(
    math.isclose(
        a.analysis_value.mean(),
        ref["mean_analysis_value"],
        rel_tol=1e-9,
    )
)
