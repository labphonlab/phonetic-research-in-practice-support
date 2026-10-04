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
from phonetic_research_companion.ch13 import run_coordinate_and_sync_audit, run_kinematic_landmarks


DATA = ROOT / "companion" / "data" / "ch13" / "synthetic_multimodal"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Chapter13CompanionTests(unittest.TestCase):
    def test_manifest_and_synthetic_status(self) -> None:
        with (ROOT / "companion" / "data" / "MANIFEST.tsv").open(encoding="utf-8", newline="") as source:
            rows = [row for row in csv.DictReader(source, delimiter="\t") if row["artifact_id"].startswith("CH13_")]
        self.assertEqual(len(rows), 7)
        for row in rows:
            self.assertEqual(row["data_status"], "SYNTHETIC_TEACHING_FIXTURE")
            self.assertEqual(row["contains_human_data"], "false")
            self.assertEqual(sha256_file(ROOT / "companion" / "data" / row["relative_path"]), row["sha256"])

    def test_coordinate_and_sync_audit_preserves_native_and_detects_failures(self) -> None:
        native_hash = sha256_file(DATA / "native_coordinates.tsv")
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            result = run_coordinate_and_sync_audit(DATA / "multimodal_session.yaml", DATA / "stream_manifest.tsv", DATA / "native_coordinates.tsv", DATA / "transformation_matrices.tsv", DATA / "calibration_sync_events.tsv", output)
            self.assertEqual(len(result["coordinates"]), 952)
            self.assertEqual(result["decisions"]["missing_frames"], [80, 81])
            self.assertGreaterEqual(len(result["decisions"]["drift_frames"]), 20)
            self.assertTrue(result["native_unchanged"])
            offset, drift = result["sync_models"]
            self.assertGreater(offset["maximum_absolute_residual_ms"], 20)
            self.assertLess(drift["maximum_absolute_residual_ms"], 2)
            self.assertEqual(len(result["sync_residuals"]), 24)
            required = ["stream_quality.tsv", "coordinate_transforms.tsv", "sync_model.tsv", "sync_residuals.tsv", "coordinate_sync_diagnostics.html", "run_provenance.json"]
            self.assertTrue(all((output / name).exists() for name in required))
        self.assertEqual(native_hash, sha256_file(DATA / "native_coordinates.tsv"))

    def test_kinematic_candidates_nonidentifiability_and_gate(self) -> None:
        trajectory_hash = sha256_file(DATA / "validated_trajectories.tsv")
        with tempfile.TemporaryDirectory() as temporary:
            coordinate_output = Path(temporary) / "coordinate"
            run_coordinate_and_sync_audit(DATA / "multimodal_session.yaml", DATA / "stream_manifest.tsv", DATA / "native_coordinates.tsv", DATA / "transformation_matrices.tsv", DATA / "calibration_sync_events.tsv", coordinate_output)
            landmark_output = Path(temporary) / "landmark"
            result = run_kinematic_landmarks(DATA / "validated_trajectories.tsv", DATA / "landmark_profiles.yaml", coordinate_output / "stream_quality.tsv", landmark_output)
            self.assertEqual(len(result["landmarks"]), 96)
            self.assertEqual(len(result["availability"]), 24)
            self.assertEqual(len(result["sensitivity"]), 24)
            self.assertGreater(len(result["candidates"]), 100)
            statuses = {row["landmark_status"] for row in result["landmarks"]}
            self.assertIn("phonetic_nonidentifiability", statuses)
            self.assertTrue(any(status.startswith("eligible") for status in statuses))
            self.assertEqual(result["gate"]["combined_decision"], "restrict")
            self.assertFalse(result["gate"]["one_global_reliability_label_permitted"])
            required = ["kinematic_candidates.tsv", "kinematic_landmarks.tsv", "landmark_availability.tsv", "landmark_sensitivity.tsv", "kinematic_diagnostics.html", "multimodal_gate.yaml", "run_provenance.json"]
            self.assertTrue(all((landmark_output / name).exists() for name in required))
        self.assertEqual(trajectory_hash, sha256_file(DATA / "validated_trajectories.tsv"))

    def test_notebooks_are_python_version_four(self) -> None:
        notebooks = sorted((ROOT / "companion" / "notebooks" / "ch13").glob("*.ipynb"))
        self.assertEqual(len(notebooks), 2)
        for path in notebooks:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["nbformat"], 4)
            self.assertEqual(payload["metadata"]["kernelspec"]["language"], "python")
            self.assertIn("SYNTHETIC_TEACHING_FIXTURE", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
