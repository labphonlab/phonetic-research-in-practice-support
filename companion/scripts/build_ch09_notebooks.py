#!/usr/bin/env python3
"""Build the two Chapter 9 R notebooks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "companion" / "notebooks" / "ch09"


def markdown(identifier: str, source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "id": identifier, "metadata": {}, "source": source}


def code(identifier: str, source: str) -> dict[str, object]:
    return {"cell_type": "code", "execution_count": None, "id": identifier, "metadata": {}, "outputs": [], "source": source}


def notebook(cells: list[dict[str, object]]) -> dict[str, object]:
    return {"cells": cells, "metadata": {"kernelspec": {"display_name": "R", "language": "R", "name": "ir"}, "language_info": {"name": "R", "version": "4.6.1"}, "phonetic_research_in_practice": {"book_chapter": 9, "data_policy": "explicitly synthetic independent judgments", "schema_version": "0.1"}}, "nbformat": 4, "nbformat_minor": 5}


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
DATA_ROOT <- file.path(REPOSITORY_ROOT, "companion", "data", "ch09", "synthetic_annotation")
if (!dir.exists(DATA_ROOT)) stop("Chapter 9 fixture absent. Run companion/scripts/generate_ch09_fixture.py explicitly; no data are substituted silently.")
source(file.path(REPOSITORY_ROOT, "companion", "r", "ch09.R"))
cat("DATA STATUS: SYNTHETIC_TEACHING_FIXTURE — independent generated judgments, not human annotations.\n")'''


CATEGORICAL = [
    markdown("ch09-cat-title", '''# Chapter 9. Categorical agreement

**Learning objective.** Evaluate independent categorical judgments using label distributions, confusion structure, chance-corrected agreement, cluster-respecting uncertainty, and category-specific usability.

**Estimated time:** 60–75 minutes. **Exercises:** 9.1 and 9.2. All bundled labels are **synthetic teaching fixtures** generated with seed 9042026. They are not evidence about annotators or voice quality.'''),
    markdown("ch09-cat-contract", '''## Contract and integrity gate

The notebook accepts the schema, assignment table, and long-form independent first-pass judgments. It stops if adjudicated labels replace independent judgments. It writes `categorical_agreement.tsv`, `confusion_matrices.tsv`, `agreement_diagnostics.html`, `analysis_decisions.yaml`, `run_provenance.json`, and an unresolved learner decision under `companion/outputs/ch09/01_categorical_agreement/`.'''),
    code("ch09-cat-setup", SETUP),
    code("ch09-cat-run", '''OUTPUT <- file.path(REPOSITORY_ROOT, "companion", "outputs", "ch09", "01_categorical_agreement")
result <- run_categorical_agreement(
  file.path(DATA_ROOT, "annotation_schema.yaml"), file.path(DATA_ROOT, "annotation_assignments.tsv"),
  file.path(DATA_ROOT, "categorical_judgments.tsv"), OUTPUT
)
stopifnot(nrow(result$pair) == 120)
stopifnot(is.finite(result$agreement$kappa[result$agreement$scope == "overall"]))
print(result$agreement)
print(result$confusion)'''),
    markdown("ch09-cat-prompt", '''## Learner decision

Change prevalence while keeping a comparable disagreement rule, then compare percent agreement, kappa, the confusion matrix, and category positive agreement. Decide separately whether *modal*, *breathy*, and *creaky* are usable for the intended downstream contrast. Do not declare the scheme valid from one coefficient.'''),
    code("ch09-cat-decision", '''learner_decision <- list(data_status = "SYNTHETIC_TEACHING_FIXTURE", decision_status = "undecided", category_decisions = list(), rationale = "Learner response required.", warning = "Agreement does not validate the construct or estimate a real workforce.")
jsonlite::write_json(learner_decision, file.path(OUTPUT, "decision_record.json"), pretty = TRUE, auto_unbox = TRUE)
stopifnot(all(file.exists(file.path(OUTPUT, c("categorical_agreement.tsv", "confusion_matrices.tsv", "agreement_diagnostics.html", "analysis_decisions.yaml", "run_provenance.json", "decision_record.json")))))
print(learner_decision)'''),
]


BOUNDARY = [
    markdown("ch09-bound-title", '''# Chapter 9. Boundary and automation audit

**Learning objective.** Retain and interpret continuous boundary differences while testing whether correction of automatic defaults changes labels, boundaries, time, or confidence.

**Estimated time:** 75–90 minutes. **Exercises:** 9.3 and 9.4. All boundaries and automatic proposals are explicitly **synthetic teaching fixtures**.'''),
    markdown("ch09-bound-contract", '''## Contract and integrity gate

The notebook compares two independent first-pass boundary series and a counterbalanced automation audit. Continuous signed and absolute differences remain in the primary output even when tolerance indicators are added. Outputs are `boundary_differences.tsv`, `boundary_diagnostics.html`, `automation_bias.tsv`, `review_decisions.tsv`, `analysis_decisions.yaml`, `run_provenance.json`, and `decision_record.json`.'''),
    code("ch09-bound-setup", SETUP),
    code("ch09-bound-run", '''OUTPUT <- file.path(REPOSITORY_ROOT, "companion", "outputs", "ch09", "02_boundary_and_automation_audit")
result <- run_boundary_and_automation_audit(
  file.path(DATA_ROOT, "annotation_schema.yaml"), file.path(DATA_ROOT, "annotation_assignments.tsv"),
  file.path(DATA_ROOT, "boundary_judgments.tsv"), file.path(DATA_ROOT, "automatic_proposal_audit.tsv"), OUTPUT
)
stopifnot(nrow(result$differences) == 240)
stopifnot(all(c("signed_difference_ms", "absolute_difference_ms") %in% names(result$differences)))
print(result$summary)
print(result$bias)
print(result$review)'''),
    markdown("ch09-bound-prompt", '''## Learner decision

Use the full difference distribution to decide whether the same boundaries are interchangeable for 15 ms and 100 ms duration contrasts. Then compare from-scratch and correction modes, distinguishing faster annotation from default anchoring. Recommend a counterbalanced review design and name the fields that must remain auditable.'''),
    code("ch09-bound-decision", '''learner_decision <- list(data_status = "SYNTHETIC_TEACHING_FIXTURE", decision_status = "undecided", contrast_15ms = "Learner response required.", contrast_100ms = "Learner response required.", automation_review = "Learner response required.", warning = "Tolerance indicators do not replace the continuous difference distribution.")
jsonlite::write_json(learner_decision, file.path(OUTPUT, "decision_record.json"), pretty = TRUE, auto_unbox = TRUE)
stopifnot(all(file.exists(file.path(OUTPUT, c("boundary_differences.tsv", "boundary_diagnostics.html", "automation_bias.tsv", "review_decisions.tsv", "analysis_decisions.yaml", "run_provenance.json", "decision_record.json")))))
print(learner_decision)'''),
]


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    for filename, payload in {
        "01_categorical_agreement.ipynb": notebook(CATEGORICAL),
        "02_boundary_and_automation_audit.ipynb": notebook(BOUNDARY),
    }.items():
        (TARGET / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
