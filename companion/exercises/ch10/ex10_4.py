# Exercise 10.4: Build a traceable correction layer
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
import pandas as pd, hashlib
root = "companion/data/ch10/synthetic_acoustics/"
raw_path = root + "automatic_landmarks.tsv"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
before = sha(raw_path)
m = pd.read_csv(raw_path, sep="\t").merge(
    pd.read_csv(root + "correction_decisions.tsv", sep="\t"), on="observation_id", how="left")
m["onset_final_ms"] = m.corrected_onset_ms.fillna(
    m.automatic_onset_ms)
m["offset_final_ms"] = m.corrected_offset_ms.fillna(
    m.automatic_offset_ms)
m["duration_final_ms"] = m.offset_final_ms - m.onset_final_ms
print("missing without reason:", (m.duration_final_ms.isna() & m.reason_code.isna()).sum())
print("corrected:", m.reason_code.notna().sum(),
      "| raw unchanged:", before == sha(raw_path))

# --- Part 2 of 2 ---
decided = set(m.observation_id[m.reason_code.notna()])
todo = m[(m.extractor_status != "ok") & ~m.observation_id.isin(decided)]
print({"corrected": len(decided), "still undecided": len(todo)})
