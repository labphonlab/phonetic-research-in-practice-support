#!/usr/bin/env python3
"""Build the two Chapter 10 Python notebooks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "companion" / "notebooks" / "ch10"


def markdown(identifier: str, source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "id": identifier, "metadata": {}, "source": source}


def code(identifier: str, source: str) -> dict[str, object]:
    return {"cell_type": "code", "execution_count": None, "id": identifier, "metadata": {}, "outputs": [], "source": source}


def notebook(cells: list[dict[str, object]]) -> dict[str, object]:
    return {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.11+"}, "phonetic_research_in_practice": {"book_chapter": 10, "data_policy": "explicitly synthetic signals and landmarks", "schema_version": "0.1"}}, "nbformat": 4, "nbformat_minor": 5}


SETUP = '''from pathlib import Path
import json
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
DATA_ROOT = REPOSITORY_ROOT / "companion" / "data" / "ch10" / "synthetic_acoustics"
if not DATA_ROOT.exists():
    raise FileNotFoundError("Chapter 10 fixture absent. Run companion/scripts/generate_ch10_fixture.py explicitly; no data are substituted silently.")
print("DATA STATUS: SYNTHETIC_TEACHING_FIXTURE — generated signals and landmarks, not human speech.")'''


ACOUSTIC = [
    markdown("ch10-ac-title", '''# Chapter 10. Pitch and formant quality control

**Learning objective.** Treat F0 and formant outputs as profile-dependent estimates, preserve every requested observation and failure, and choose settings from blinded signal-level diagnostics rather than group outcomes.

**Estimated time:** 90 minutes. **Exercises:** 10.1 and 10.2. The six bundled WAV files are explicitly **synthetic teaching fixtures** with known generator parameters. The included autocorrelation and spectral-peak estimators are teaching implementations, not validated production measurement systems.'''),
    markdown("ch10-ac-contract", '''## Input and output contract

Inputs are source and interval manifests, a completed measurement specification, and generated PCM audio. Outputs are long-form raw candidates, flags, an HTML settings comparison, a blinded review sample, a measure-specific gate, and run provenance under `companion/outputs/ch10/01_pitch_and_formant_qc/`. Source audio is hash-checked and never overwritten.'''),
    code("ch10-ac-setup", SETUP),
    code("ch10-ac-run", '''from phonetic_research_companion.ch10 import run_pitch_and_formant_qc
OUTPUT = REPOSITORY_ROOT / "companion" / "outputs" / "ch10" / "01_pitch_and_formant_qc"
result = run_pitch_and_formant_qc(DATA_ROOT / "source_manifest.tsv", DATA_ROOT / "interval_manifest.tsv", DATA_ROOT / "acoustic_measurement_spec.yaml", OUTPUT)
assert result["raw"]
assert result["flags"]
assert {row["measure"] for row in result["raw"]} == {"f0", "formant"}
print("Raw estimates:", len(result["raw"]), "Flags:", len(result["flags"]), "Review rows:", len(result["review"]))
for summary in result["summaries"]:
    print(summary)'''),
    markdown("ch10-ac-prompt", '''## Learner gate

Compare the prespecified floor–ceiling and maximum-formant profiles without inspecting the generator role or any group outcome. Explain missing frames, search-limit contact, abrupt jumps, and insufficient peaks. For each measure, choose **accept**, **restrict**, **amend and rerun**, or **reject**, and state why that decision would not automatically generalize to natural speech.'''),
    code("ch10-ac-decision", '''learner_gate = {"data_status": "SYNTHETIC_TEACHING_FIXTURE", "decision_status": "undecided", "f0_gate": "Learner response required.", "formant_gate": "Learner response required.", "scope": "synthetic teaching signals only", "warning": "Generated-signal performance is not validation on human speech."}
(OUTPUT / "learner_measurement_gate.json").write_text(json.dumps(learner_gate, indent=2), encoding="utf-8")
required = ["raw_acoustic_estimates.tsv", "measurement_flags.tsv", "settings_comparison.html", "review_sample.tsv", "measurement_gate.json", "run_provenance.json", "learner_measurement_gate.json"]
assert all((OUTPUT / name).exists() for name in required)
print(json.dumps(learner_gate, indent=2))'''),
]


DURATION = [
    markdown("ch10-dur-title", '''# Chapter 10. Duration validation and correction layers

**Learning objective.** Separate onset, offset, and duration error, preserve the automatic extractor output, and rebuild analysis measurements from reason-coded corrections.

**Estimated time:** 75–90 minutes. **Exercises:** 10.3 and 10.4. All 120 landmark records are explicitly **synthetic teaching fixtures**; error summaries do not evaluate a real aligner.'''),
    markdown("ch10-dur-contract", '''## Input and output contract

Inputs are immutable automatic measurements, independently generated reference landmarks, a validation manifest, and a correction decision table. Outputs are observation-level validation, diagnostics, a normalized correction layer, rebuilt analysis measurements, and provenance containing pre- and post-run hashes under `companion/outputs/ch10/02_duration_validation_and_corrections/`.'''),
    code("ch10-dur-setup", SETUP),
    code("ch10-dur-run", '''from phonetic_research_companion.ch10 import run_duration_validation
OUTPUT = REPOSITORY_ROOT / "companion" / "outputs" / "ch10" / "02_duration_validation_and_corrections"
result = run_duration_validation(DATA_ROOT / "automatic_landmarks.tsv", DATA_ROOT / "reference_landmarks.tsv", DATA_ROOT / "duration_validation_manifest.tsv", DATA_ROOT / "correction_decisions.tsv", OUTPUT)
assert len(result["validation"]) == 120
assert result["raw_unchanged"]
assert len(result["corrections"]) == 9
assert len(result["shifted_accurate"]) >= 5
for summary in result["summaries"]:
    print(summary)
print("Shifted-boundary but accurate-duration cases:", len(result["shifted_accurate"]))'''),
    markdown("ch10-dur-prompt", '''## Learner decision

Identify a token whose two boundaries are shifted while duration remains accurate. Explain why it may be usable for a duration contrast but not for synchronization. Compare contexts and duration strata, inspect every correction reason, and demonstrate that the raw automatic columns can be recovered byte-for-byte.'''),
    code("ch10-dur-decision", '''learner_decision = {"data_status": "SYNTHETIC_TEACHING_FIXTURE", "decision_status": "undecided", "duration_use": "Learner response required.", "synchronization_use": "Learner response required.", "correction_audit": "Learner response required.", "raw_unchanged": result["raw_unchanged"], "warning": "Synthetic error does not estimate a real aligner."}
(OUTPUT / "decision_record.json").write_text(json.dumps(learner_decision, indent=2), encoding="utf-8")
required = ["duration_validation.tsv", "duration_diagnostics.html", "measurement_corrections.tsv", "analysis_measurements.tsv", "run_provenance.json", "decision_record.json"]
assert all((OUTPUT / name).exists() for name in required)
print(json.dumps(learner_decision, indent=2))'''),
]


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    for filename, payload in {"01_pitch_and_formant_qc.ipynb": notebook(ACOUSTIC), "02_duration_validation_and_corrections.ipynb": notebook(DURATION)}.items():
        (TARGET / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
