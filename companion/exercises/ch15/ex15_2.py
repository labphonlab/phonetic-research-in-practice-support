# Exercise 15.2: Produce a candidate-to-analysis flow
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
import pandas as pd, yaml
d = "companion/data/ch15/synthetic_corpus/"
hits = pd.read_csv(d + "searchable_hits.tsv", sep="\t")
link = pd.read_csv(d + "linkage_table.tsv", sep="\t")[["source_token_id", "linkage_status"]]
cfg = yaml.safe_load(open(d + "query_config.yaml"))
m = hits.merge(
    link,
    on="source_token_id",
    how="left",
    validate="many_to_one",
)
# one row per raw hit
assert len(m) == len(hits)
m["duplicate"] = m.duplicated(
    cfg["duplicate_key"], keep="first"
)
reason = [("duplicate", m.duplicate), ("context_ineligible", ~m.context_eligible),
          ("signal_unavailable", ~m.signal_available), ("measurement_failure", ~m.measurement_success),
          ("quality_rejected", ~m.quality_approved), ("metadata_missing", ~m.metadata_complete),
          ("linkage_ambiguous", m.linkage_status == "ambiguous"), ("linkage_unmatched", m.linkage_status == "unmatched")]

# --- Part 2 of 2 ---
m["exclusion_reason"] = "included"
for name, cond in reversed(reason):
    # first listed reason wins
    m.loc[cond, "exclusion_reason"] = name
m["final_inclusion"] = m.exclusion_reason == "included"
print(len(m), int(m.final_inclusion.sum()))     # 640 440
for col in ["speaker_id", "item_id", "condition_id"]:
    t = m.groupby(col).agg(raw=("source_hit_id", "size"), final=("final_inclusion", "sum"))
    print(col, (t.final / t.raw).round(2).agg(["min", "max"]).to_dict())
m.to_csv("candidate_manifest.tsv", sep="\t", index=False)
