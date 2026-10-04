from __future__ import annotations
import csv,hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/"companion"/"src";sys.path.insert(0,str(SRC)) if str(SRC) not in sys.path else None
from phonetic_research_companion.ch20 import build_candidate,clean_verify
DATA=ROOT/"companion"/"data"/"ch20"/"release_candidate"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Chapter20Tests(unittest.TestCase):
 def test_manifest(self):
  with (ROOT/"companion"/"data"/"MANIFEST.tsv").open(encoding="utf-8",newline="") as s:rows=[r for r in csv.DictReader(s,delimiter="\t") if r["artifact_id"].startswith("CH20_")]
  self.assertEqual(len(rows),9)
  for r in rows:self.assertEqual(r["contains_human_data"],"false");self.assertEqual(sha(ROOT/"companion"/"data"/r["relative_path"]),r["sha256"])
 def test_candidate_and_clean_gate(self):
  with tempfile.TemporaryDirectory() as temp:
   first=Path(temp)/"first";a=build_candidate(ROOT,DATA/"release_spec.yaml",DATA/"release_manifest.tsv",DATA/"license_matrix.tsv",DATA/"governance_decisions.tsv",DATA/"citation_metadata.yaml",DATA/"public_profile.yaml",DATA/"protected_profile.yaml",first)
   self.assertEqual(len(a["manifest"]),9);self.assertTrue(a["decisions"]["privacy_scan_pass"]);self.assertFalse(a["decisions"]["license_public_release_pass"]);self.assertFalse(a["decisions"]["protected_route_accessed"])
   b=clean_verify(ROOT,DATA/"release_spec.yaml",DATA/"release_manifest.tsv",first/"release_candidate_manifest.tsv",DATA/"availability_statement_template.md",DATA/"maintenance_policy.md",DATA/"citation_metadata.yaml",Path(temp)/"second")
   self.assertTrue(b["run"]["technical_pass"]);self.assertEqual(b["gate"]["decision"],"postpone_deposit_pending_author_and_publisher");self.assertFalse(b["gate"]["deposit_authorized"]);self.assertFalse(b["run"]["deposit_attempted"])
 def test_notebooks(self):
  paths=sorted((ROOT/"companion"/"notebooks"/"ch20").glob("*.ipynb"));self.assertEqual(len(paths),2)
  for p in paths:
   payload=json.loads(p.read_text());self.assertEqual(payload["nbformat"],4);self.assertEqual(payload["metadata"]["kernelspec"]["language"],"python");self.assertIn("INTERNAL CANDIDATE",p.read_text())
if __name__=="__main__":unittest.main()
