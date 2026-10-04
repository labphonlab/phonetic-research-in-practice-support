#!/usr/bin/env python3
"""Build the two Chapter 13 Python notebooks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "companion" / "notebooks" / "ch13"


def markdown(identifier: str, source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "id": identifier, "metadata": {}, "source": source}


def code(identifier: str, source: str) -> dict[str, object]:
    return {"cell_type": "code", "execution_count": None, "id": identifier, "metadata": {}, "outputs": [], "source": source}


def notebook(cells: list[dict[str, object]]) -> dict[str, object]:
    return {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.11+"}, "phonetic_research_in_practice": {"book_chapter": 13, "data_policy": "explicitly synthetic coordinates, clocks, and trajectories", "schema_version": "0.1"}}, "nbformat": 4, "nbformat_minor": 5}


SETUP = '''from pathlib import Path
import sys

start = Path.cwd().resolve()
for candidate in (start, *start.parents):
    if (candidate / "companion" / "data" / "MANIFEST.tsv").is_file():
        REPOSITORY_ROOT = candidate
        break
else:
    raise RuntimeError("Run from the repository root or one of its subdirectories.")
SOURCE_ROOT = REPOSITORY_ROOT / "companion" / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))
DATA_ROOT = REPOSITORY_ROOT / "companion" / "data" / "ch13" / "synthetic_multimodal"
if not DATA_ROOT.exists():
    raise FileNotFoundError("Chapter 13 fixture absent. Run companion/scripts/generate_ch13_fixture.py explicitly; no data are substituted silently.")
print("DATA STATUS: SYNTHETIC_TEACHING_FIXTURE — generated geometry, clocks, and trajectories, not human articulatory data.")'''


COORDINATES = [
    markdown("ch13-coord-title", '''# Chapter 13. Coordinate and synchronization audit

**Learning objective.** Reconstruct native, head-corrected, anatomically rotated, and time-corrected layers while diagnosing reference drift, dropped frames, clock offset, and clock drift.

**Estimated time:** 90 minutes. **Exercises:** 13.2 and 13.3. Every coordinate and timing event is an explicitly **synthetic teaching fixture**. Passing the audit does not validate a physical EMA or audio system.'''),
    markdown("ch13-coord-contract", '''## Input and output contract

Inputs are session metadata, a stream manifest, immutable native coordinates and timestamps, recorded transformation matrices, and common synchronization events. Outputs preserve native values while adding derived coordinate layers, stream-specific quality decisions, two synchronization models, event-level residuals, diagnostics, and provenance.'''),
    code("ch13-coord-setup", SETUP),
    code("ch13-coord-run", '''from phonetic_research_companion.ch13 import run_coordinate_and_sync_audit
OUTPUT = REPOSITORY_ROOT / "companion" / "outputs" / "ch13" / "01_coordinate_and_sync_audit"
result = run_coordinate_and_sync_audit(DATA_ROOT / "multimodal_session.yaml", DATA_ROOT / "stream_manifest.tsv", DATA_ROOT / "native_coordinates.tsv", DATA_ROOT / "transformation_matrices.tsv", DATA_ROOT / "calibration_sync_events.tsv", OUTPUT)
assert result["native_unchanged"]
assert result["decisions"]["missing_frames"] == [80, 81]
assert result["decisions"]["drift_frames"]
for row in result["quality"]:
    print(row)
for row in result["sync_models"]:
    print(row)'''),
    markdown("ch13-coord-prompt", '''## Learner gate

Locate the interval in which rigid reference geometry fails without consulting a condition label. Show how the failure moves the nominally stationary target after head correction. Compare the residuals from a one-offset correction with the fitted offset-and-drift model, retain the missing anchor and dropped frames, and state which spatial and temporal claims survive.'''),
    code("ch13-coord-decision", '''required = ["stream_quality.tsv", "coordinate_transforms.tsv", "sync_model.tsv", "sync_residuals.tsv", "coordinate_sync_diagnostics.html", "run_provenance.json"]
assert all((OUTPUT / name).exists() for name in required)
print(result["decisions"])'''),
]


KINEMATICS = [
    markdown("ch13-kin-title", '''# Chapter 13. Kinematic candidates and multimodal gates

**Learning objective.** Preserve all candidate landmarks, distinguish phonetic nonidentifiability from software failure, quantify profile-dependent eligibility, and issue stream-specific and combined multimodal decisions.

**Estimated time:** 90–120 minutes. **Exercises:** 13.1 and 13.4. The smooth, plateaued, multi-peaked, noisy, missing, and low-excursion trajectories are generated teaching cases, not observations of speech movement.'''),
    markdown("ch13-kin-contract", '''## Input and output contract

Inputs are the synthetic trajectories, four prespecified filtering-and-threshold profiles, and the preceding stream-quality decisions. Outputs retain every velocity candidate, one rule-governed landmark record per event and profile, availability by trajectory class, profile sensitivity, diagnostics, a multimodal gate, and provenance.'''),
    code("ch13-kin-setup", SETUP),
    code("ch13-kin-run", '''from phonetic_research_companion.ch13 import run_kinematic_landmarks
QUALITY = REPOSITORY_ROOT / "companion" / "outputs" / "ch13" / "01_coordinate_and_sync_audit" / "stream_quality.tsv"
if not QUALITY.exists():
    raise FileNotFoundError("Run 01_coordinate_and_sync_audit.ipynb first; stream decisions are not silently replaced.")
OUTPUT = REPOSITORY_ROOT / "companion" / "outputs" / "ch13" / "02_kinematic_landmarks"
result = run_kinematic_landmarks(DATA_ROOT / "validated_trajectories.tsv", DATA_ROOT / "landmark_profiles.yaml", QUALITY, OUTPUT)
assert result["raw_unchanged"]
assert result["candidates"]
assert any(row["landmark_status"] == "phonetic_nonidentifiability" for row in result["landmarks"])
assert any(row["landmark_status"].startswith("eligible") for row in result["landmarks"])
for row in result["availability"]:
    print(row)'''),
    markdown("ch13-kin-prompt", '''## Learner decision

Build an observability matrix before interpreting a multimodal contrast. Then compare the four landmark profiles for smooth, plateaued, multi-peaked, noisy, missing, and low-excursion trajectories. Explain why a numeric landmark is not forced for every event, how the eligible population changes, and why one global “reliability” label would conceal incompatible stream-level decisions.'''),
    code("ch13-kin-decision", '''required = ["kinematic_candidates.tsv", "kinematic_landmarks.tsv", "landmark_availability.tsv", "landmark_sensitivity.tsv", "kinematic_diagnostics.html", "multimodal_gate.yaml", "run_provenance.json"]
assert all((OUTPUT / name).exists() for name in required)
assert result["gate"]["combined_decision"] == "restrict"
assert not result["gate"]["one_global_reliability_label_permitted"]
print(result["gate"])'''),
]


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    for filename, payload in {"01_coordinate_and_sync_audit.ipynb": notebook(COORDINATES), "02_kinematic_landmarks.ipynb": notebook(KINEMATICS)}.items():
        (TARGET / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
