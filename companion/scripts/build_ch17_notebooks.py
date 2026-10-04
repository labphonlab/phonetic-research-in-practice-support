#!/usr/bin/env python3
"""Build the two Chapter 17 R notebooks."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "companion" / "notebooks" / "ch17"


def markdown(identifier, source): return {"cell_type": "markdown", "id": identifier, "metadata": {}, "source": source}
def code(identifier, source): return {"cell_type": "code", "execution_count": None, "id": identifier, "metadata": {}, "outputs": [], "source": source}
def notebook(cells): return {"cells": cells, "metadata": {"kernelspec": {"display_name": "R", "language": "R", "name": "ir"}, "language_info": {"name": "R", "version": "4.6.1"}, "phonetic_research_in_practice": {"book_chapter": 17, "data_policy": "explicitly synthetic regression teaching fixture", "schema_version": "0.1"}}, "nbformat": 4, "nbformat_minor": 5}


SETUP = '''find_repository <- function(start=getwd()) { current<-normalizePath(start,mustWork=TRUE); repeat { if (file.exists(file.path(current, "companion", "data", "MANIFEST.tsv"))) return(current); parent<-dirname(current); if (identical(parent,current)) stop("Run from the repository root or a subdirectory."); current<-parent } }
REPOSITORY_ROOT<-find_repository(); DATA_ROOT<-file.path(REPOSITORY_ROOT,"companion","data","ch17","synthetic_regression")
if (!dir.exists(DATA_ROOT)) stop("Chapter 17 fixture absent. Run companion/scripts/generate_ch17_fixture.py explicitly; no data are substituted silently.")
source(file.path(REPOSITORY_ROOT,"companion","r","ch17.R")); cat("DATA STATUS: SYNTHETIC_TEACHING_FIXTURE — generated regression example, not empirical evidence.\n")'''

FIRST = [
    markdown("ch17-model-title", '''# Chapter 17. Estimands, design matrices, and mixed models

**Learning objective.** Translate a verbal estimand into auditable factor levels, contrasts, scaling, grouping structure, and a prespecified sequence of regression models.

**Estimated time:** 110 minutes. **Exercises:** 17.1–17.3. This notebook keeps failed validation cases, warnings, and model simplification visible. The conceptual design crosses speakers and items, but the installed `nlme` implementation treats items as fixed blocking effects; that implementation choice narrows inference.'''),
    markdown("ch17-model-contract", '''## Input and output contract

Inputs are the synthetic analysis table, schema, estimand specification, three contrast systems, and deliberate duplicate-key and under-supported-slope cases. Outputs are an estimand record, long-form design matrices, grouping graph, support table, every model attempt, serialized successful models, and provenance.'''),
    code("ch17-model-setup", SETUP),
    code("ch17-model-run", '''OUTPUT<-file.path(REPOSITORY_ROOT,"companion","outputs","ch17","01_estimand_design_matrix_and_mixed_model")
result<-run_estimand_design_and_models(file.path(DATA_ROOT,"analysis_data.tsv"),file.path(DATA_ROOT,"analysis_schema.yaml"),file.path(DATA_ROOT,"regression_analysis_spec.yaml"),file.path(DATA_ROOT,"condition_contrasts.tsv"),file.path(DATA_ROOT,"adverse_cases.tsv"),OUTPUT)
stopifnot(nrow(result$data)==1296,nrow(result$design_matrix)==3888,result$decisions$duplicate_adverse_detected,result$decisions$under_supported_slope_detected)
print(result$attempts); print(head(result$support)); cat("Selected model:",result$selected_model,"\n")'''),
    markdown("ch17-model-prompt", '''## Learner gate

Write the estimand before interpreting a coefficient. Compare treatment, sum-to-zero, and custom coding without changing the fitted values. Then explain why replacing an item random effect with fixed item blocking changes the population to which the result can extend. Treat the deliberate duplicate and sparse speaker as successful validation tests, not research results.'''),
    code("ch17-model-decision", '''required<-c("estimand_record.yaml","design_matrix.tsv","grouping_graph.svg","data_support.tsv","model_attempts.tsv","run_provenance.json")
stopifnot(all(file.exists(file.path(OUTPUT,required))),file.exists(file.path(OUTPUT,paste0(result$selected_model,".rds")))); print(result$decisions)'''),
]

SECOND = [
    markdown("ch17-diagnostics-title", '''# Chapter 17. Diagnostics, predictions, and calibrated reporting

**Learning objective.** Diagnose a selected model, quantify cluster influence, distinguish population-level from conditional prediction, calculate prespecified contrasts on declared scales, and restrict the claim when support or random-effects scope is insufficient.

**Estimated time:** 110 minutes. **Exercise:** 17.4. Chapter 14's stability file is linked only as a synthetic teaching gate, never as empirical confirmation.'''),
    markdown("ch17-diagnostics-contract", '''## Input and output contract

Inputs are the fitted-model archive, prediction grid, focal contrasts, and Chapter 14 stability output. The notebook writes an HTML diagnostic report, leave-one-speaker-out influence table, prediction-support audit, population and conditional predictions, exact focal contrasts, a structured claim gate, and provenance.'''),
    code("ch17-diagnostics-setup", SETUP),
    code("ch17-diagnostics-run", '''MODEL_DIR<-file.path(REPOSITORY_ROOT,"companion","outputs","ch17","01_estimand_design_matrix_and_mixed_model")
CH14<-file.path(REPOSITORY_ROOT,"companion","outputs","ch14","02_sensitivity_universe","claim_stability.tsv")
if (!dir.exists(MODEL_DIR)) stop("Run the first Chapter 17 notebook first.")
OUTPUT<-file.path(REPOSITORY_ROOT,"companion","outputs","ch17","02_diagnostics_predictions_and_reporting")
result<-run_diagnostics_predictions_and_gate(file.path(DATA_ROOT,"analysis_data.tsv"),file.path(DATA_ROOT,"regression_analysis_spec.yaml"),file.path(DATA_ROOT,"prediction_grid.tsv"),file.path(DATA_ROOT,"focal_contrasts.tsv"),MODEL_DIR,CH14,OUTPUT)
stopifnot(result$gate$decision=="restrict",!result$gate$significance_vote_permitted,nrow(result$influence)==24,nrow(result$predictions)==15)
print(result$contrasts); print(result$support); print(result$gate)'''),
    markdown("ch17-diagnostics-prompt", '''## Learner decision

Report the SHIFT_A–BASE contrast with its exact averaging distribution and scale. Compare the population prediction with the first speaker's conditional prediction. Identify unsupported grid points and the most influential omitted speaker. Finally, write one permitted claim and three prohibited extensions, including the new-item generalization that the fitted model cannot support.'''),
    code("ch17-diagnostics-decision", '''required<-c("model_diagnostics.html","cluster_influence.tsv","prediction_support.tsv","model_predictions.tsv","focal_contrasts.tsv","structured_regression_gate.yaml","run_provenance.json")
stopifnot(all(file.exists(file.path(OUTPUT,required))),result$decisions$leave_one_speaker_fits==24,result$gate$new_unit_scope$items==FALSE); print(result$decisions)'''),
]


def main():
    TARGET.mkdir(parents=True, exist_ok=True)
    for name, payload in {"01_estimand_design_matrix_and_mixed_model.ipynb": notebook(FIRST), "02_diagnostics_predictions_and_reporting.ipynb": notebook(SECOND)}.items():
        (TARGET / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
