from __future__ import annotations
import csv,hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; SRC=ROOT/"companion"/"src"; sys.path.insert(0,str(SRC)) if str(SRC) not in sys.path else None
from phonetic_research_companion.ch15 import run_query_and_denominator_audit,run_representativeness_and_cross_corpus
DATA=ROOT/"companion"/"data"/"ch15"/"synthetic_corpus"
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
class Chapter15CompanionTests(unittest.TestCase):
    def test_manifest(self):
        with (ROOT/"companion"/"data"/"MANIFEST.tsv").open(encoding="utf-8",newline="") as source: rows=[r for r in csv.DictReader(source,delimiter="\t") if r["artifact_id"].startswith("CH15_")]
        self.assertEqual(len(rows),7)
        for row in rows: self.assertEqual(row["data_status"],"SYNTHETIC_TEACHING_FIXTURE"); self.assertEqual(row["contains_human_data"],"false"); self.assertEqual(sha(ROOT/"companion"/"data"/row["relative_path"]),row["sha256"])
    def test_query_and_denominator(self):
        before=sha(DATA/"searchable_hits.tsv")
        with tempfile.TemporaryDirectory() as t:
            r=run_query_and_denominator_audit(DATA/"searchable_hits.tsv",DATA/"linkage_table.tsv",DATA/"query_config.yaml",DATA/"corpus_access_profile.yaml",Path(t))
            self.assertEqual(len(r["candidates"]),640); self.assertEqual(r["query_run"]["unique_source_tokens"],600); self.assertEqual(r["decisions"]["duplicates_retained"],40); self.assertEqual(r["flow"][-1]["count"],440)
            self.assertTrue(all(stage["count"]>=r["flow"][i+1]["count"] for i,stage in enumerate(r["flow"][:-1])))
        self.assertEqual(before,sha(DATA/"searchable_hits.tsv"))
    def test_representativeness_gate(self):
        with tempfile.TemporaryDirectory() as t:
            q=Path(t)/"q"; run_query_and_denominator_audit(DATA/"searchable_hits.tsv",DATA/"linkage_table.tsv",DATA/"query_config.yaml",DATA/"corpus_access_profile.yaml",q)
            r=run_representativeness_and_cross_corpus(q/"candidate_manifest.tsv",DATA/"target_population.yaml",DATA/"corpus_design.tsv",DATA/"cross_corpus_map.tsv",Path(t)/"r")
            self.assertEqual(r["gate"]["decision"],"restrict"); self.assertFalse(r["gate"]["synthetic_fixture_is_population_evidence"]); self.assertTrue(any(x["support_status"]=="unsupported" for x in r["support"])); self.assertTrue(any(x["compatibility"]=="incompatible" for x in r["compatibility"]))
    def test_notebooks(self):
        paths=sorted((ROOT/"companion"/"notebooks"/"ch15").glob("*.ipynb")); self.assertEqual(len(paths),2)
        for p in paths:
            x=json.loads(p.read_text()); self.assertEqual(x["nbformat"],4); self.assertEqual(x["metadata"]["kernelspec"]["language"],"python"); self.assertIn("SYNTHETIC_TEACHING_FIXTURE",p.read_text())
if __name__=="__main__": unittest.main()
