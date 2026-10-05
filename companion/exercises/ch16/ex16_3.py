# Exercise 16.3: Build a scientific test suite
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 3 ---
# test_pipeline.py
import pandas as pd, pytest, yaml
D = "companion/data/ch16/synthetic_pipeline/"
src = pd.read_csv(D + "source_measurements.tsv", sep="\t")
adv = pd.read_csv(D + "adverse_cases.tsv", sep="\t")
contract = yaml.safe_load(open(D + "data_contracts.yaml"))["source_measurements"]
def violations(df):
    return {"missing_fields": set(contract["required_fields"]) - set(df.columns),
            "duplicate_keys": int(df.duplicated(contract["primary_key"], keep=False).sum()),
            "negative_intervals": int((df.end_ms < df.start_ms).sum()),
            "missing_values": int(df[df.measurement_status == "observed"].raw_value.isna().sum())}

# --- Part 2 of 3 ---
# test_pipeline.py (continued)
def test_schema_valid_fixture():
    v = violations(src)
    assert not v["missing_fields"] and not any(v[k] for k in list(v)[1:])
def test_adverse_cases_are_caught():
    v = violations(adv)
    assert v["duplicate_keys"] == 2 and v["negative_intervals"] == 1 and v["missing_values"] == 1
def test_unicode_label_and_failure_retained():
    assert "\u6bcd\u97f3" in set(src.unicode_label) and (src.measurement_status == "failed").sum() == 1

# --- Part 3 of 3 ---
# test_pipeline.py (continued)
def test_integration_matches_reference():
    corr = pd.read_csv(D + "correction_table.tsv", sep="\t")
    out = src.merge(corr[["token_id", "corrected_value"]], on="token_id", how="left")
    out = out[out.measurement_status == "observed"]
    out = out.assign(analysis_value=out.corrected_value.fillna(out.raw_value))
    ref = pd.read_csv(D + "expected/analysis_table.tsv", sep="\t")
    assert out.token_id.tolist() == ref.token_id.tolist()
    assert out.analysis_value.tolist() == pytest.approx(ref.analysis_value.tolist())
