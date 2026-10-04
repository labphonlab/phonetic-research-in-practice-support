#!/usr/bin/env python3
"""Build the two Chapter 7 notebooks from reviewable source strings."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "companion" / "notebooks" / "ch07"


def markdown(identifier: str, source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "id": identifier, "metadata": {}, "source": source}


def code(identifier: str, source: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": identifier,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def notebook(cells: list[dict[str, object]]) -> dict[str, object]:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11+"},
            "phonetic_research_in_practice": {
                "book_chapter": 7,
                "data_policy": "synthetic fixture by default; authorized local files only",
                "schema_version": "0.1",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


SETUP_CODE = '''from pathlib import Path
import csv
import json
import sys

start = Path.cwd().resolve()
for candidate in (start, *start.parents):
    if (candidate / "companion" / "data" / "MANIFEST.tsv").is_file():
        REPOSITORY_ROOT = candidate
        break
else:
    raise RuntimeError("Run this notebook from the repository root or one of its subdirectories.")

SOURCE_ROOT = REPOSITORY_ROOT / "companion" / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

DATA_ROOT = REPOSITORY_ROOT / "companion" / "data" / "ch07" / "synthetic_recordings"
if not DATA_ROOT.exists():
    raise FileNotFoundError(
        "The Chapter 7 fixture is absent. Run companion/scripts/generate_ch07_fixture.py explicitly; "
        "the notebook will not create or substitute data silently."
    )
print(f"Repository: {REPOSITORY_ROOT}")
print("DATA STATUS: SYNTHETIC_TEACHING_FIXTURE — no participant observations are present.")'''


QC_CELLS = [
    markdown(
        "ch07-qc-title",
        '''# Chapter 7. Recording quality control

**Learning objective.** Diagnose whether a recorded file is technically readable and fit for a declared phonetic measure, while preserving the distinction between file integrity and measurement validity.

**Estimated time:** 45–60 minutes. **Prerequisite:** Chapter 7. **Exercises:** 7.1 and 7.2.

The bundled input is an explicitly **synthetic teaching fixture**: three one-second numerical tones created by `generate_ch07_fixture.py`. They are not speech, participant data, or evidence about a population. One file is intentionally clipped and one is intentionally near silent. To use authorized local study files, create a separate manifest with the documented columns and run the notebook locally; do not upload restricted recordings to Colab.''',
    ),
    markdown(
        "ch07-qc-contract",
        '''## Input and output contract

The input manifest must supply `file_id`, `session_id`, `source_path`, `expected_sample_rate_hz`, `expected_bit_depth`, `expected_channels`, and `data_status`. The notebook reads WAV headers and samples but never modifies audio. It writes `recording_qc.tsv`, `recording_qc_summary.html`, `run_provenance.json`, and `decision_record.json` under `companion/outputs/ch07/01_recording_qc/`.

A passing technical check is not a certificate of scientific validity. Measure-specific usability remains a research decision tied to the construct, recording chain, and planned estimator.''',
    ),
    code("ch07-qc-setup", SETUP_CODE),
    code(
        "ch07-qc-run",
        '''from phonetic_research_companion.ch07 import run_recording_qc

MANIFEST = DATA_ROOT / "recording_manifest.tsv"
OUTPUT = REPOSITORY_ROOT / "companion" / "outputs" / "ch07" / "01_recording_qc"
results = run_recording_qc(MANIFEST, OUTPUT)

# Fixture invariants: these tests prevent an apparently successful but changed lesson.
assert len(results) == 3
assert sum("possible_digital_clipping" in row["warnings"] for row in results) == 1
assert sum("near_silent" in row["warnings"] for row in results) == 1
assert all(row["data_status"] == "SYNTHETIC_TEACHING_FIXTURE" for row in results)
print(f"Validated {len(results)} explicitly synthetic files; outputs: {OUTPUT}")''',
    ),
    code(
        "ch07-qc-inspect",
        '''display_fields = [
    "file_id", "qc_status", "peak_normalized", "rms_normalized", "clipped_fraction",
    "warnings", "usable_for_duration", "usable_for_relative_amplitude", "usable_for_spectral_measures",
]
for row in results:
    print({field: row.get(field) for field in display_fields})''',
    ),
    markdown(
        "ch07-qc-decision-prompt",
        '''## Learner decision

Explain why the clipped file may retain usable duration information while failing for relative-amplitude or spectral work. Then state whether each file should be accepted, re-recorded, restricted to named measures, or excluded. Your decision must cite the target measure and should not use a single global “good/bad audio” label.''',
    ),
    code(
        "ch07-qc-decision",
        '''LEARNER_DECISION = {
    "data_status": "SYNTHETIC_TEACHING_FIXTURE",
    "decision_status": "undecided",
    "measure_specific_decisions": [],
    "rationale": "Learner response required before assessment.",
    "warning": "This clean-run record is not an empirical conclusion and must not be reported as one.",
}
(OUTPUT / "decision_record.json").write_text(json.dumps(LEARNER_DECISION, indent=2), encoding="utf-8")
assert (OUTPUT / "recording_qc.tsv").exists()
assert (OUTPUT / "recording_qc_summary.html").exists()
assert (OUTPUT / "run_provenance.json").exists()
print(json.dumps(LEARNER_DECISION, indent=2))''',
    ),
]


METADATA_CELLS = [
    markdown(
        "ch07-meta-title",
        '''# Chapter 7. Calibration, timing, and session metadata

**Learning objective.** Validate whether a recording-session record is internally consistent with file headers and a declared timing requirement, without confusing documentation with equipment certification.

**Estimated time:** 45–60 minutes. **Prerequisite:** Chapter 7 and the recording-QC notebook. **Exercises:** 7.3 and 7.4.

All bundled inputs are explicitly **synthetic teaching fixtures**. The timing events are generated numerical values. The metadata describe no participant, real site, or physical microphone. Replace them only with institutionally authorized local records.''',
    ),
    markdown(
        "ch07-meta-contract",
        '''## Input and output contract

The notebook requires a session YAML record, the WAV manifest, and a timing-event table. It writes `validated_session_metadata.json`, `recording_deviations.tsv`, `timing_check.tsv`, `run_provenance.json`, and `decision_record.json` under `companion/outputs/ch07/02_calibration_and_metadata/`.

The validator checks required fields, WAV headers, file counts, and the residuals of a linear timing relation. A successful run establishes internal consistency only. It does not establish microphone calibration, room suitability, or construct validity.''',
    ),
    code("ch07-meta-setup", SETUP_CODE),
    code(
        "ch07-meta-run",
        '''from phonetic_research_companion.ch07 import validate_session_metadata

METADATA = DATA_ROOT / "recording_session_metadata.yaml"
MANIFEST = DATA_ROOT / "recording_manifest.tsv"
TIMING_EVENTS = DATA_ROOT / "timing_events.tsv"
OUTPUT = REPOSITORY_ROOT / "companion" / "outputs" / "ch07" / "02_calibration_and_metadata"

validated = validate_session_metadata(METADATA, MANIFEST, TIMING_EVENTS, OUTPUT)
assert validated["metadata"]["data_status"] == "SYNTHETIC_TEACHING_FIXTURE"
assert validated["validation_status"] == "pass"
assert validated["observed_file_count"] == 3
print(json.dumps(validated["timing_fit"], indent=2))''',
    ),
    code(
        "ch07-meta-inspect",
        '''with (OUTPUT / "recording_deviations.tsv").open(encoding="utf-8", newline="") as source:
    deviations = list(csv.DictReader(source, delimiter="\t"))
with (OUTPUT / "timing_check.tsv").open(encoding="utf-8", newline="") as source:
    timing_rows = list(csv.DictReader(source, delimiter="\t"))
print(f"Recorded deviations: {len(deviations)}")
print("Timing events:")
for row in timing_rows:
    print(row)''',
    ),
    markdown(
        "ch07-meta-decision-prompt",
        '''## Learner decision

Decide whether the synthetic session should be accepted, rerun, restricted to named measures, or stopped. Distinguish the deliberately defective teaching files from the timing check, and state why a complete metadata form does not certify the physical accuracy of hardware that was never calibrated.''',
    ),
    code(
        "ch07-meta-decision",
        '''LEARNER_DECISION = {
    "data_status": "SYNTHETIC_TEACHING_FIXTURE",
    "decision_status": "undecided",
    "claim_requirements_checked": ["file headers", "file count", "timing residual"],
    "limitations": ["no physical microphone", "no calibrated amplitude", "no participant speech"],
    "rationale": "Learner response required before assessment.",
    "warning": "This clean-run record is not an empirical conclusion and must not be reported as one.",
}
(OUTPUT / "decision_record.json").write_text(json.dumps(LEARNER_DECISION, indent=2), encoding="utf-8")
for required in (
    "validated_session_metadata.json", "recording_deviations.tsv", "timing_check.tsv", "run_provenance.json"
):
    assert (OUTPUT / required).exists(), required
print(json.dumps(LEARNER_DECISION, indent=2))''',
    ),
]


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    outputs = {
        "01_recording_qc.ipynb": notebook(QC_CELLS),
        "02_calibration_and_metadata.ipynb": notebook(METADATA_CELLS),
    }
    for filename, payload in outputs.items():
        (TARGET / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
