# Exercise 16.2: Replace a manual correction
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
import pandas as pd
def apply_corrections(src, corr):
    if not corr.token_id.is_unique:
        raise ValueError("duplicate correction keys")
    unmatched = set(corr.token_id) - set(src.token_id)
    if unmatched:
        raise KeyError(
            f"unmatched correction keys: {sorted(unmatched)}"
        )
    out = src.merge(
        corr[["token_id", "corrected_value", "reason_code"]],
        on="token_id",
        how="left",
    )
    # raw_value untouched
    out["analysis_value"] = out.corrected_value.fillna(
        out.raw_value
    )
    return out
d = "companion/data/ch16/synthetic_pipeline/"
src = pd.read_csv(d + "source_measurements.tsv", sep="\t")
corr = pd.read_csv(d + "correction_table.tsv", sep="\t")
out = apply_corrections(src, corr)
assert out.raw_value.equals(src.raw_value)                    # raw values unchanged
print(int((out.analysis_value != out.raw_value).sum()))       # 1 corrected value

# --- Part 2 of 2 ---
import pytest
def test_unmatched_key_fails():
    bad = corr.assign(token_id="SYN_PIPE_999")
    with pytest.raises(KeyError):
        apply_corrections(src, bad)
