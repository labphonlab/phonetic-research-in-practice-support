from __future__ import annotations
import csv,hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/"companion"/"src";sys.path.insert(0,str(SRC)) if str(SRC) not in sys.path else None
from phonetic_research_companion.ch16 import run_pipeline_graph_and_contracts,run_clean_reproduction
DATA=ROOT/"companion"/"data"/"ch16"/"synthetic_pipeline"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Chapter16Tests(unittest.TestCase):
 def test_manifest(self):
  with (ROOT/"companion"/"data"/"MANIFEST.tsv").open(encoding="utf-8",newline="") as s:rows=[r for r in csv.DictReader(s,delimiter="\t") if r["artifact_id"].startswith("CH16_")]
  self.assertEqual(len(rows),12)
  for r in rows:self.assertEqual(r["contains_human_data"],"false");self.assertEqual(sha(ROOT/"companion"/"data"/r["relative_path"]),r["sha256"])
 def test_contracts_and_clean_run(self):
  before=sha(DATA/"source_measurements.tsv")
  with tempfile.TemporaryDirectory() as t:
   graph=Path(t)/"graph";a=run_pipeline_graph_and_contracts(DATA/"pipeline_spec.yaml",DATA/"data_contracts.yaml",DATA/"source_measurements.tsv",DATA/"correction_table.tsv",DATA/"adverse_cases.tsv",graph)
   self.assertTrue(a["decision"]["canonical_contracts_pass"]);self.assertEqual(a["decision"]["adverse_failures_detected"],3);self.assertFalse(a["decision"]["protected_data_accessed"])
   b=run_clean_reproduction(DATA/"pipeline_spec.yaml",graph/"configuration_resolved.yaml",DATA/"source_measurements.tsv",DATA/"correction_table.tsv",DATA/"expected_artifacts.tsv",DATA/"expected",DATA/"tolerance_policy.yaml",DATA/"public_allowlist.txt",Path(t)/"clean")
   self.assertEqual(len(b["analysis"]),11);self.assertEqual(b["assessment"]["decision"],"pass_public_fixture");self.assertTrue(all(x["passed"] for x in b["comparisons"]+b["privacy"]));self.assertFalse(b["assessment"]["scientific_interpretation_warranted_by_run"])
  self.assertEqual(before,sha(DATA/"source_measurements.tsv"))
 def test_notebooks(self):
  ps=sorted((ROOT/"companion"/"notebooks"/"ch16").glob("*.ipynb"));self.assertEqual(len(ps),2)
  for p in ps:
   x=json.loads(p.read_text());self.assertEqual(x["nbformat"],4);self.assertEqual(x["metadata"]["kernelspec"]["language"],"python");self.assertIn("SYNTHETIC_TEACHING_FIXTURE",p.read_text())
if __name__=="__main__":unittest.main()
