#!/usr/bin/env python3
"""Build the two Chapter 12 R notebooks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "companion" / "notebooks" / "ch12"


def markdown(identifier: str, source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "id": identifier, "metadata": {}, "source": source}


def code(identifier: str, source: str) -> dict[str, object]:
    return {"cell_type": "code", "execution_count": None, "id": identifier, "metadata": {}, "outputs": [], "source": source}


def notebook(cells: list[dict[str, object]]) -> dict[str, object]:
    return {"cells": cells, "metadata": {"kernelspec": {"display_name": "R", "language": "R", "name": "ir"}, "language_info": {"name": "R", "version": "4.6.1"}, "phonetic_research_in_practice": {"book_chapter": 12, "data_policy": "explicitly synthetic trajectories and intervals", "schema_version": "0.1"}}, "nbformat": 4, "nbformat_minor": 5}


SETUP = '''find_repository <- function(start = getwd()) {
  current <- normalizePath(start, mustWork = TRUE)
  repeat {
    if (file.exists(file.path(current, "companion", "data", "MANIFEST.tsv"))) return(current)
    parent <- dirname(current)
    if (identical(parent, current)) stop("Run from the repository root or a subdirectory.")
    current <- parent
  }
}
REPOSITORY_ROOT <- find_repository()
DATA_ROOT <- file.path(REPOSITORY_ROOT, "companion", "data", "ch12", "synthetic_prosody")
if (!dir.exists(DATA_ROOT)) stop("Chapter 12 fixture absent. Run companion/scripts/generate_ch12_fixture.py explicitly; no data are substituted silently.")
source(file.path(REPOSITORY_ROOT, "companion", "r", "ch12.R"))
cat("DATA STATUS: SYNTHETIC_TEACHING_FIXTURE — generated contours and intervals, not human prosody.\n")'''


PREPARATION = [
    markdown("ch12-prep-title", '''# Chapter 12. Pitch-trajectory preparation

**Learning objective.** Preserve the denominator of requested frames, assign distinct missingness causes, retain three time coordinates, and distinguish observed from bounded interpolation.

**Estimated time:** 75–90 minutes. **Exercises:** 12.1 and 12.2. All 96 trajectories and their F0 values are explicitly **synthetic teaching fixtures**; they are not observations of speakers.'''),
    markdown("ch12-prep-contract", '''## Input and output contract

Inputs are source and interval manifests, a fixed-delay landmark, raw frame candidates, and the trajectory specification. The notebook reconstructs every requested 10 ms frame, verifies the join, permits interpolation only for estimator-failure gaps no longer than 20 ms, and writes requested frames, preprocessing state, coverage with contributing-token counts, diagnostics, decisions, and provenance.'''),
    code("ch12-prep-setup", SETUP),
    code("ch12-prep-run", '''OUTPUT <- file.path(REPOSITORY_ROOT, "companion", "outputs", "ch12", "01_pitch_trajectory_preparation")
result <- run_pitch_trajectory_preparation(file.path(DATA_ROOT, "source_manifest.tsv"), file.path(DATA_ROOT, "interval_manifest.tsv"), file.path(DATA_ROOT, "landmarks.tsv"), file.path(DATA_ROOT, "raw_frame_estimates.tsv"), file.path(DATA_ROOT, "prosodic_trajectory_spec.yaml"), OUTPUT)
stopifnot(nrow(result$prepared) > 3000, result$raw_unchanged)
stopifnot(all(c("structural_unvoiced", "estimator_failure", "quality_rejection", "source_failure") %in% result$prepared$gap_code))
stopifnot(any(result$prepared$value_origin == "interpolated_estimator_failure"))
print(head(result$coverage, 20))
cat("Requested frames:", nrow(result$prepared), "\n")'''),
    markdown("ch12-prep-prompt", '''## Learner decision

Compare denominators obtained from requested frames and successful estimates. Plot the same synthetic contours in onset-relative milliseconds, proportional time, and time from the fixed-delay event. State which claim each coordinate can support and which it obscures. Keep structural voicelessness separate from tracker failure and interpolation.'''),
    code("ch12-prep-decision", '''stopifnot(all(file.exists(file.path(OUTPUT, c("requested_frames.tsv", "trajectory_preprocessing.tsv", "trajectory_coverage.tsv", "trajectory_diagnostics.html", "preprocessing_decision.yaml", "run_provenance.json")))))
print(result$decision)'''),
]


DYNAMIC = [
    markdown("ch12-dyn-title", '''# Chapter 12. Dynamic models and rhythm sensitivity

**Learning objective.** Compare a naive aggregate smooth with a model that represents speaker, item, token, and serial dependence, then stress-test duration-based rhythm summaries across speakers, material, and segmentation.

**Estimated time:** 90–120 minutes. **Exercises:** 12.3 and 12.4. Model estimates and rhythm metrics are generated teaching results, not empirical language classifications.'''),
    markdown("ch12-dyn-contract", '''## Input and output contract

The notebook requires the preceding prepared trajectory, segmented interval data, and a prespecified comparison file. It writes population-level prediction grids, token-level residual-dependence summaries, rhythm metrics by speaker and sentence set, sensitivity results by material and segmentation, a trajectory gate, diagnostics, and provenance. Frame count is never reported as independent replication.'''),
    code("ch12-dyn-setup", SETUP),
    code("ch12-dyn-run", '''PREPARED <- file.path(REPOSITORY_ROOT, "companion", "outputs", "ch12", "01_pitch_trajectory_preparation", "trajectory_preprocessing.tsv")
if (!file.exists(PREPARED)) stop("Run 01_pitch_trajectory_preparation.ipynb first; the model notebook will not substitute a trajectory table.")
OUTPUT <- file.path(REPOSITORY_ROOT, "companion", "outputs", "ch12", "02_dynamic_models_and_rhythm")
result <- run_dynamic_models_and_rhythm(PREPARED, file.path(DATA_ROOT, "segmented_intervals.tsv"), file.path(DATA_ROOT, "model_comparison.yaml"), OUTPUT)
stopifnot(nrow(result$predictions) == 204)
stopifnot(nrow(result$residual_dependence) == 2)
stopifnot(!result$gate$frame_count_is_replication_count)
print(result$residual_dependence)
print(head(result$rhythm))'''),
    markdown("ch12-dyn-prompt", '''## Learner gate

Compare residual lag-one dependence and uncertainty between the naive and structured models. Explain why thousands of frames still derive from only twelve speakers, eight items, and ninety-six tokens. Compare rhythm metrics by speaker, sentence subset, and segmentation profile, then decide whether the evidence permits only a sample description, a synthetic group contrast, or any broader classification.'''),
    code("ch12-dyn-decision", '''stopifnot(all(file.exists(file.path(OUTPUT, c("dynamic_model_diagnostics.html", "trajectory_predictions.tsv", "residual_dependence.tsv", "rhythm_metrics_by_unit.tsv", "rhythm_sensitivity.tsv", "model_warnings.tsv", "trajectory_gate.yaml", "run_provenance.json")))))
print(result$gate)'''),
]


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    for filename, payload in {"01_pitch_trajectory_preparation.ipynb": notebook(PREPARATION), "02_dynamic_models_and_rhythm.ipynb": notebook(DYNAMIC)}.items():
        (TARGET / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
