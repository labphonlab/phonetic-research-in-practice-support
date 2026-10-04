#!/usr/bin/env python3
"""Build the two Chapter 11 R notebooks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "companion" / "notebooks" / "ch11"


def markdown(identifier: str, source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "id": identifier, "metadata": {}, "source": source}


def code(identifier: str, source: str) -> dict[str, object]:
    return {"cell_type": "code", "execution_count": None, "id": identifier, "metadata": {}, "outputs": [], "source": source}


def notebook(cells: list[dict[str, object]]) -> dict[str, object]:
    return {"cells": cells, "metadata": {"kernelspec": {"display_name": "R", "language": "R", "name": "ir"}, "language_info": {"name": "R", "version": "4.6.1"}, "phonetic_research_in_practice": {"book_chapter": 11, "data_policy": "explicitly synthetic segmental measurements", "schema_version": "0.1"}}, "nbformat": 4, "nbformat_minor": 5}


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
DATA_ROOT <- file.path(REPOSITORY_ROOT, "companion", "data", "ch11", "synthetic_segmental")
if (!dir.exists(DATA_ROOT)) stop("Chapter 11 fixture absent. Run companion/scripts/generate_ch11_fixture.py explicitly; no data are substituted silently.")
source(file.path(REPOSITORY_ROOT, "companion", "r", "ch11.R"))
cat("DATA STATUS: SYNTHETIC_TEACHING_FIXTURE — generated landmarks and measures, not speech observations.\n")'''


AUDIT = [
    markdown("ch11-audit-title", '''# Chapter 11. Segmental-measure audit

**Learning objective.** Reconstruct VOT, closure, vowel duration, formants, and fricative measures from stable events while retaining absent, ambiguous, and invalid requests.

**Estimated time:** 75–90 minutes. **Exercises:** 11.1 and 11.2. The 1,080 tokens, event times, and acoustic estimates are explicitly **synthetic teaching fixtures** and do not describe speech.'''),
    markdown("ch11-audit-contract", '''## Input and output contract

Inputs are the event dictionary, token annotation manifest, acoustic estimates, and requested-measure manifest. Outputs are one raw row per request, a landmark audit, contextual coverage, HTML diagnostics, analysis decisions, and provenance under `companion/outputs/ch11/01_segmental_measure_audit/`. No failure is removed silently.'''),
    code("ch11-audit-setup", SETUP),
    code("ch11-audit-run", '''OUTPUT <- file.path(REPOSITORY_ROOT, "companion", "outputs", "ch11", "01_segmental_measure_audit")
result <- run_segmental_measure_audit(file.path(DATA_ROOT, "event_dictionary.yaml"), file.path(DATA_ROOT, "annotation_manifest.tsv"), file.path(DATA_ROOT, "acoustic_estimates.tsv"), file.path(DATA_ROOT, "segmental_measure_manifest.tsv"), OUTPUT)
stopifnot(nrow(result$raw) == 3240)
stopifnot(nrow(result$audit) > 0)
stopifnot(all(c("vot", "closure_duration", "vowel_onset_f0", "vowel_duration", "f1", "f2", "f3", "fricative_duration", "fricative_cog") %in% result$raw$measure_id))
print(result$coverage)
cat("Retained review or failure rows:", nrow(result$audit), "\n")'''),
    markdown("ch11-audit-prompt", '''## Learner gate

Inspect landmark order, absent periodicity, multiple releases, context coverage, and the relationship among signed VOT, closure, and vowel-onset F0. Decide **accept**, **restrict**, **amend and rerun**, or **reject** separately for each requested measure before fitting any outcome model.'''),
    code("ch11-audit-decision", '''learner_gate <- list(data_status = "SYNTHETIC_TEACHING_FIXTURE", decision_status = "undecided", measure_decisions = list(), rationale = "Learner response required.", warning = "Generated cue profiles are not empirical laryngeal contrasts.")
jsonlite::write_json(learner_gate, file.path(OUTPUT, "decision_record.json"), pretty = TRUE, auto_unbox = TRUE)
stopifnot(all(file.exists(file.path(OUTPUT, c("segmental_raw_measures.tsv", "landmark_audit.tsv", "coverage_by_context.tsv", "segmental_diagnostics.html", "analysis_decisions.yaml", "run_provenance.json", "decision_record.json")))))
print(learner_gate)'''),
]


NORMALIZATION = [
    markdown("ch11-norm-title", '''# Chapter 11. Normalization comparison

**Learning objective.** Compare raw, log, within-speaker standardized, and explicit F3-reference-scaled formants after declaring the estimand, preservation target, reduction target, and reference sample.

**Estimated time:** 90 minutes. **Exercises:** 11.3 and 11.4. All values and speaker codes are explicitly **synthetic teaching fixtures**. Apparent category separation is not an empirical result.'''),
    markdown("ch11-norm-contract", '''## Input and output contract

This notebook requires the validated raw output from the preceding Chapter 11 notebook, category metadata, the prespecified training/evaluation split, and the measurement manifest. It records eligibility, reference inventory, speaker parameters, four transformation layers, bootstrap stability, an explicit decision, and provenance. Raw columns remain unchanged and every normalized value must rebuild from the raw value and recorded parameter.'''),
    code("ch11-norm-setup", SETUP),
    code("ch11-norm-run", '''RAW_PATH <- file.path(REPOSITORY_ROOT, "companion", "outputs", "ch11", "01_segmental_measure_audit", "segmental_raw_measures.tsv")
if (!file.exists(RAW_PATH)) stop("Run 01_segmental_measure_audit.ipynb first; normalization will not fabricate or substitute validated raw measures.")
OUTPUT <- file.path(REPOSITORY_ROOT, "companion", "outputs", "ch11", "02_normalization_comparison")
result <- run_normalization_comparison(RAW_PATH, file.path(DATA_ROOT, "annotation_manifest.tsv"), file.path(DATA_ROOT, "split_manifest.tsv"), file.path(DATA_ROOT, "segmental_measure_manifest.tsv"), OUTPUT)
stopifnot(result$exact_rebuild, result$raw_unchanged)
stopifnot(nrow(result$parameters) == 90)
stopifnot(any(!result$parameters$eligible))
print(unique(result$parameters[, c("speaker_id", "split", "eligible", "eligibility_reason", "reference_categories")]))'''),
    markdown("ch11-norm-prompt", '''## Learner decision

Compare preservation of within-speaker vowel ordering with reduction of reference-frequency dispersion. Identify speakers excluded by the unequal inventory, remove one vowel category in a sensitivity exercise, and quantify parameter instability. State the eligible population for every conclusion; do not describe normalization as neutral cleaning.'''),
    code("ch11-norm-decision", '''stopifnot(all(file.exists(file.path(OUTPUT, c("normalization_parameters.tsv", "segmental_normalized_measures.tsv", "normalization_stability.tsv", "normalization_diagnostics.html", "normalization_decision.yaml", "run_provenance.json")))))
print(result$decision)
cat("Exact rebuild:", result$exact_rebuild, " Raw unchanged:", result$raw_unchanged, "\n")'''),
]


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    for filename, payload in {"01_segmental_measure_audit.ipynb": notebook(AUDIT), "02_normalization_comparison.ipynb": notebook(NORMALIZATION)}.items():
        (TARGET / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
