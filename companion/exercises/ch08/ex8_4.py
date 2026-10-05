# Exercise 8.4: Audit an online experiment
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import hashlib, pandas as pd
base = "companion/data/ch08/synthetic_perception/"
stim = pd.read_csv(base + "stimulus_manifest.tsv", sep="\t")
stim["ok"] = [
    hashlib.sha256(open(base + p, "rb").read()).hexdigest()
    == h
    for p, h in zip(stim.asset_path, stim.sha256)
]
print("hash mismatches:", int((~stim.ok).sum()),
      "of", len(stim))
trials = pd.read_csv(base + "perception_trial_manifest.tsv", sep="\t")
print(trials.groupby("participant_code").size().agg(["count", "min", "max"]).to_dict())
print(trials[["response_mapping_id", "rt_origin", "timeout_ms"]].drop_duplicates().to_dict("records"))
audit = pd.read_csv(base + "online_timing_audit.tsv", sep="\t")
print(audit[["configuration_id", "median_onset_error_ms",
             "p95_onset_error_ms"]].to_string(index=False))
