# Exercise 20.3: Assemble and audit a release candidate
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
import hashlib, json, pathlib, re, shutil, pandas as pd
R = pathlib.Path("companion/data/ch20/release_candidate"); OUT = pathlib.Path("build/release_candidate")
allow = pd.read_csv(R / "release_manifest.tsv", sep="\t", dtype=str)
shutil.rmtree(OUT, ignore_errors=True)
for p in allow["path"]:
    (OUT / p).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, OUT / p)
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
files = sorted(f for f in OUT.rglob("*") if f.is_file()); rel = lambda f: str(f.relative_to(OUT))
(OUT.parent / "checksum_manifest.txt").write_text("".join(f"{sha(f)}  {rel(f)}\n" for f in files))
print("unexpected files:", [rel(f) for f in files if rel(f) not in set(allow["path"])])
print("stale checksums:", [p for p, h in zip(allow["path"], allow["sha256"]) if sha(OUT / p) != h])

# --- Part 2 of 2 ---
PAT = {"private_path": r"/(?:Users|home)/|[A-Za-z]:\\Users\\", "email": r"[\w.+-]+@[\w-]+\.[\w.]+", "secret": r"(?i)(api[_-]?key|secret|password)\s*[:=]\s*\S+"}
MEDIA = {".wav", ".mp3", ".mp4", ".flac", ".m4a", ".mov", ".TextGrid"}
def outputs(f): return sum(bool(c.get("outputs")) for c in json.loads(f.read_text())["cells"]) if f.suffix == ".ipynb" else 0
scan = pd.DataFrame([{"path": rel(f), **{k: len(re.findall(v, f.read_text(errors="ignore"))) for k, v in PAT.items()},
                      "media": f.suffix in MEDIA, "notebook_outputs": outputs(f)} for f in files])
scan.to_csv(OUT.parent / "privacy_scan.tsv", sep="\t", index=False)
print(scan[(scan.drop(columns="path") != 0).any(axis=1)])           # each row needs a human decision
gov = pd.read_csv(R / "governance_decisions.tsv", sep="\t", dtype=str)
print(gov[["review_id", "decision", "record_status"]])                # pending or placeholder means not authorized
