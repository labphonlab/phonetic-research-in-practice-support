from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "companion" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
from phonetic_research_companion.ch10 import run_duration_validation, run_pitch_and_formant_qc

DATA = ROOT / "companion" / "data" / "ch10" / "synthetic_acoustics"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


class Chapter10CompanionTests(unittest.TestCase):
    def test_manifest_and_synthetic_status(self) -> None:
        with (ROOT / "companion" / "data" / "MANIFEST.tsv").open(encoding="utf-8", newline="") as source:
            rows = [row for row in csv.DictReader(source, delimiter="\t") if row["artifact_id"].startswith("CH10_")]
        self.assertEqual(len(rows), 14)
        for row in rows:
            self.assertEqual(row["data_status"], "SYNTHETIC_TEACHING_FIXTURE")
            self.assertEqual(row["contains_human_data"], "false")
            self.assertEqual(sha256_file(ROOT / "companion" / "data" / row["relative_path"]), row["sha256"])

    def test_acoustic_qc_preserves_sources_and_outputs_failures(self) -> None:
        audio = sorted((DATA / "audio").glob("*.wav"))
        before = {path.name: sha256_file(path) for path in audio}
        with tempfile.TemporaryDirectory() as temporary:
            result = run_pitch_and_formant_qc(DATA / "source_manifest.tsv", DATA / "interval_manifest.tsv", DATA / "acoustic_measurement_spec.yaml", Path(temporary))
            self.assertTrue(result["raw"])
            self.assertTrue(result["flags"])
            self.assertEqual({row["measure"] for row in result["raw"]}, {"f0", "formant"})
            self.assertTrue(any(row["estimator_status"] == "missing" for row in result["raw"]))
        self.assertEqual(before, {path.name: sha256_file(path) for path in audio})

    def test_duration_correction_is_a_separate_layer(self) -> None:
        before = sha256_file(DATA / "automatic_landmarks.tsv")
        with tempfile.TemporaryDirectory() as temporary:
            result = run_duration_validation(DATA / "automatic_landmarks.tsv", DATA / "reference_landmarks.tsv", DATA / "duration_validation_manifest.tsv", DATA / "correction_decisions.tsv", Path(temporary))
            self.assertEqual(len(result["validation"]), 120)
            self.assertEqual(len(result["corrections"]), 9)
            self.assertGreaterEqual(len(result["shifted_accurate"]), 5)
            self.assertTrue(result["raw_unchanged"])
        self.assertEqual(before, sha256_file(DATA / "automatic_landmarks.tsv"))

    def test_notebooks_are_python_version_four(self) -> None:
        notebooks = sorted((ROOT / "companion" / "notebooks" / "ch10").glob("*.ipynb"))
        self.assertEqual(len(notebooks), 2)
        for path in notebooks:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["nbformat"], 4)
            self.assertEqual(payload["metadata"]["kernelspec"]["language"], "python")
            self.assertIn("SYNTHETIC_TEACHING_FIXTURE", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
