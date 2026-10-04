#!/usr/bin/env python3
"""Build the two Chapter 8 R notebooks from reviewable source strings."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "companion" / "notebooks" / "ch08"


def markdown(identifier: str, source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "id": identifier, "metadata": {}, "source": source}


def code(identifier: str, source: str) -> dict[str, object]:
    return {"cell_type": "code", "execution_count": None, "id": identifier, "metadata": {}, "outputs": [], "source": source}


def notebook(cells: list[dict[str, object]]) -> dict[str, object]:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "R", "language": "R", "name": "ir"},
            "language_info": {"name": "R", "version": "4.6.1"},
            "phonetic_research_in_practice": {
                "book_chapter": 8,
                "data_policy": "explicitly synthetic fixtures by default",
                "schema_version": "0.1",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


SETUP = '''find_repository <- function(start = getwd()) {
  current <- normalizePath(start, mustWork = TRUE)
  repeat {
    if (file.exists(file.path(current, "companion", "data", "MANIFEST.tsv"))) return(current)
    parent <- dirname(current)
    if (identical(parent, current)) stop("Run from the repository root or one of its subdirectories.")
    current <- parent
  }
}
REPOSITORY_ROOT <- find_repository()
DATA_ROOT <- file.path(REPOSITORY_ROOT, "companion", "data", "ch08", "synthetic_perception")
if (!dir.exists(DATA_ROOT)) {
  stop("Chapter 8 fixture absent. Run companion/scripts/generate_ch08_fixture.py explicitly; no data are substituted silently.")
}
source(file.path(REPOSITORY_ROOT, "companion", "r", "ch08.R"))
cat("Repository:", REPOSITORY_ROOT, "\n")
cat("DATA STATUS: SYNTHETIC_TEACHING_FIXTURE — no participant observations are present.\n")'''


PSYCHOMETRIC_CELLS = [
    markdown(
        "ch08-psych-title",
        '''# Chapter 8. Psychometric functions

**Learning objective.** Fit and audit trial-level response functions while separating observed classification behavior from claims about categorical perception.

**Estimated time:** 75–90 minutes. **Prerequisite:** Chapter 8 and introductory logistic regression. **Exercises:** 8.1 and 8.2.

Every bundled trial and stimulus is an explicitly **synthetic teaching fixture** generated with seed 8042026. The seven WAV assets are numerical tones, not speech. The response rows are simulated and cannot provide evidence about human listeners, phoneme categories, or a population.''',
    ),
    markdown(
        "ch08-psych-contract",
        '''## Input and output contract

Inputs are a trial manifest, stimulus manifest with SHA-256 hashes, and trial-level response file. The notebook validates identifiers and assets, fits a group-descriptive logistic function and separate participant functions, derives location and slope summaries, and flags reverse or unsupported functions rather than forcing a threshold.

Outputs are `psychometric_parameters.tsv`, `psychometric_diagnostics.html`, `analysis_decisions.yaml`, `run_provenance.json`, and an unresolved `decision_record.json` under `companion/outputs/ch08/01_psychometric_functions/`.''',
    ),
    code("ch08-psych-setup", SETUP),
    code(
        "ch08-psych-run",
        '''OUTPUT <- file.path(REPOSITORY_ROOT, "companion", "outputs", "ch08", "01_psychometric_functions")
result <- run_psychometric_analysis(
  file.path(DATA_ROOT, "perception_trial_manifest.tsv"),
  file.path(DATA_ROOT, "stimulus_manifest.tsv"),
  file.path(DATA_ROOT, "psychometric_responses.tsv"),
  OUTPUT
)
stopifnot(nrow(result$parameters) == 13)
stopifnot(any(grepl("nonmonotonic_or_reverse", result$parameters$diagnostic_flag)))
print(result$parameters)''',
    ),
    markdown(
        "ch08-psych-audit",
        '''## Model and claim audit

Inspect the participant flagged as reverse or nonmonotonic. Compare the group location with participant locations, then refit after changing the sampled continuum points or excluding endpoints. Explain which changes concern the response model and which would change the theoretical claim. Do not describe a logistic shape alone as evidence of categorical perception.''',
    ),
    code(
        "ch08-psych-decision",
        '''learner_decision <- list(
  data_status = "SYNTHETIC_TEACHING_FIXTURE",
  decision_status = "undecided",
  classification_function_claim = "Learner response required before assessment.",
  categorical_perception_claim = "not supported by this synthetic classification task",
  warning = "This record is an instructional prompt, not an empirical conclusion."
)
jsonlite::write_json(learner_decision, file.path(OUTPUT, "decision_record.json"), pretty = TRUE, auto_unbox = TRUE)
required_outputs <- c("psychometric_parameters.tsv", "psychometric_diagnostics.html", "analysis_decisions.yaml", "run_provenance.json", "decision_record.json")
stopifnot(all(file.exists(file.path(OUTPUT, required_outputs))))
print(learner_decision)''',
    ),
]


SIGNAL_CELLS = [
    markdown(
        "ch08-sdt-title",
        '''# Chapter 8. Signal detection and reaction time

**Learning objective.** Decompose event-level responses into sensitivity, criterion, accuracy, and reaction-time evidence under an explicit correction and exclusion rule.

**Estimated time:** 60–75 minutes. **Prerequisite:** Chapter 8. **Exercises:** 8.3 and 8.4.

All event counts, response times, and device configurations are explicitly **synthetic teaching fixtures**. They illustrate how similar accuracy can conceal different response structures; they are not measurements of listeners or browser hardware.''',
    ),
    markdown(
        "ch08-sdt-contract",
        '''## Input and output contract

The event log retains signal presence, response, correctness, participant, condition, reaction time, time-zero definition, and device profile. A YAML decision file declares the loglinear correction and admissible reaction-time interval. The timing-audit file represents two synthetic configurations.

Outputs are `signal_detection_summary.tsv`, `reaction_time_diagnostics.html`, `excluded_events.tsv`, `online_experiment_audit.tsv`, `analysis_decisions.yaml`, `run_provenance.json`, and an unresolved `decision_record.json` under `companion/outputs/ch08/02_signal_detection_and_rt/`.''',
    ),
    code("ch08-sdt-setup", SETUP),
    code(
        "ch08-sdt-run",
        '''OUTPUT <- file.path(REPOSITORY_ROOT, "companion", "outputs", "ch08", "02_signal_detection_and_rt")
result <- run_signal_detection_analysis(
  file.path(DATA_ROOT, "detection_event_log.tsv"),
  file.path(DATA_ROOT, "signal_detection_decisions.yaml"),
  file.path(DATA_ROOT, "online_timing_audit.tsv"),
  OUTPUT
)
stopifnot(nrow(result$summary) == 2)
stopifnot(nrow(result$excluded) == 48)
stopifnot(abs(diff(result$summary$accuracy)) < 0.10)
print(result$summary)
print(result$timing_audit)''',
    ),
    markdown(
        "ch08-sdt-audit",
        '''## Learner decision

Compare the two conditions using accuracy, hit rate, false-alarm rate, *d′*, criterion, and correct-trial reaction times. State whether the manipulation changes sensitivity, criterion, speed, accuracy, or an unresolved combination. Then use the two synthetic device profiles to decide which timing claims would require laboratory validation or narrower wording.''',
    ),
    code(
        "ch08-sdt-decision",
        '''learner_decision <- list(
  data_status = "SYNTHETIC_TEACHING_FIXTURE",
  decision_status = "undecided",
  sensitivity_statement = "Learner response required before assessment.",
  criterion_statement = "Learner response required before assessment.",
  reaction_time_statement = "Learner response required before assessment.",
  timing_scope = "synthetic configuration comparison only",
  warning = "This record is an instructional prompt, not an empirical conclusion."
)
jsonlite::write_json(learner_decision, file.path(OUTPUT, "decision_record.json"), pretty = TRUE, auto_unbox = TRUE)
required_outputs <- c(
  "signal_detection_summary.tsv", "reaction_time_diagnostics.html", "excluded_events.tsv",
  "online_experiment_audit.tsv", "analysis_decisions.yaml", "run_provenance.json", "decision_record.json"
)
stopifnot(all(file.exists(file.path(OUTPUT, required_outputs))))
print(learner_decision)''',
    ),
]


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    outputs = {
        "01_psychometric_functions.ipynb": notebook(PSYCHOMETRIC_CELLS),
        "02_signal_detection_and_rt.ipynb": notebook(SIGNAL_CELLS),
    }
    for filename, payload in outputs.items():
        (TARGET / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
