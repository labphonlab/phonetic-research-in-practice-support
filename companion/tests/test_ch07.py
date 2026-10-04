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

from phonetic_research_companion.ch07 import run_recording_qc, validate_session_metadata


DATA = ROOT / "companion" / "data" / "ch07" / "synthetic_recordings"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


class Chapter7CompanionTests(unittest.TestCase):
    def test_fixture_manifest_is_explicitly_synthetic_and_hashes_match(self) -> None:
        manifest_path = ROOT / "companion" / "data" / "MANIFEST.tsv"
        with manifest_path.open(encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source, delimiter="\t"))
        rows = [row for row in rows if row["artifact_id"].startswith("CH07_")]
        self.assertEqual(len(rows), 6)
        for row in rows:
            self.assertEqual(row["data_status"], "SYNTHETIC_TEACHING_FIXTURE")
            self.assertEqual(row["contains_human_data"], "false")
            artifact = ROOT / "companion" / "data" / row["relative_path"]
            self.assertEqual(sha256_file(artifact), row["sha256"])

    def test_recording_qc_preserves_sources_and_flags_known_defects(self) -> None:
        audio = sorted(DATA.glob("*.wav"))
        before = {path.name: sha256_file(path) for path in audio}
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            results = run_recording_qc(DATA / "recording_manifest.tsv", output)
            self.assertEqual(len(results), 3)
            self.assertEqual(sum("possible_digital_clipping" in row["warnings"] for row in results), 1)
            self.assertEqual(sum("near_silent" in row["warnings"] for row in results), 1)
            for required in ("recording_qc.tsv", "recording_qc_summary.html", "run_provenance.json"):
                self.assertTrue((output / required).is_file())
        after = {path.name: sha256_file(path) for path in audio}
        self.assertEqual(before, after)

    def test_metadata_validator_passes_declared_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            result = validate_session_metadata(
                DATA / "recording_session_metadata.yaml",
                DATA / "recording_manifest.tsv",
                DATA / "timing_events.tsv",
                output,
            )
            self.assertEqual(result["validation_status"], "pass")
            self.assertEqual(result["metadata"]["data_status"], "SYNTHETIC_TEACHING_FIXTURE")
            self.assertLess(result["timing_fit"]["max_absolute_residual_ms"], 5)
            for required in (
                "validated_session_metadata.json",
                "recording_deviations.tsv",
                "timing_check.tsv",
                "run_provenance.json",
            ):
                self.assertTrue((output / required).is_file())

    def test_notebooks_are_valid_version_four_json(self) -> None:
        notebook_root = ROOT / "companion" / "notebooks" / "ch07"
        notebooks = sorted(notebook_root.glob("*.ipynb"))
        self.assertEqual(len(notebooks), 2)
        for path in notebooks:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["nbformat"], 4)
            self.assertGreaterEqual(payload["nbformat_minor"], 5)
            self.assertTrue(payload["cells"])
            self.assertTrue(any(cell["cell_type"] == "code" for cell in payload["cells"]))
            serialized = path.read_text(encoding="utf-8")
            self.assertIn("SYNTHETIC_TEACHING_FIXTURE", serialized)


if __name__ == "__main__":
    unittest.main()
