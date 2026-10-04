#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];TARGET=ROOT/"companion"/"notebooks"/"ch18"
def md(i,s):return {"cell_type":"markdown","id":i,"metadata":{},"source":s}
def code(i,s):return {"cell_type":"code","execution_count":None,"id":i,"metadata":{},"outputs":[],"source":s}
def nb(c):return {"cells":c,"metadata":{"kernelspec":{"display_name":"R","language":"R","name":"ir"},"language_info":{"name":"R","version":"4.6.1"},"phonetic_research_in_practice":{"book_chapter":18,"data_policy":"explicitly synthetic complex-model fixture","schema_version":"0.1"}},"nbformat":4,"nbformat_minor":5}
SETUP='''find_repository<-function(start=getwd()){current<-normalizePath(start,mustWork=TRUE);repeat{if(file.exists(file.path(current, "companion", "data", "MANIFEST.tsv")))return(current);parent<-dirname(current);if(identical(parent,current))stop("Run from the repository root or a subdirectory.");current<-parent}}
REPOSITORY_ROOT<-find_repository();DATA_ROOT<-file.path(REPOSITORY_ROOT,"companion","data","ch18","synthetic_complex");if(!dir.exists(DATA_ROOT))stop("Chapter 18 fixture absent. Run companion/scripts/generate_ch18_fixture.py explicitly; no data are substituted silently.");source(file.path(REPOSITORY_ROOT,"companion","r","ch18.R"));cat("DATA STATUS: SYNTHETIC_TEACHING_FIXTURE — complex-model workflow test, not population evidence.\n")'''
FIRST=[md("ch18-dyn-title",'''# Chapter 18. Dynamic structure, measurement error, and missingness

**Learning objective.** Require every complex model component to answer a feature of the data-generating, measurement, or observation process, and preserve the assumptions attached to that component.

**Estimated time:** 120 minutes. **Exercises:** 18.1–18.3. Frames are not treated as independent replications, hypothetical error is not relabeled as validated uncertainty, and structural absence is never imputed.'''),md("ch18-dyn-contract",'''## Input and output contract

Inputs are generated trajectories with raw and normalized time, series boundaries, paired measurement validation, a reason-code dictionary, two error scenarios, the complex-model specification, and Chapter 14's sensitivity schema. Outputs preserve the scalar benchmark, dynamic model, trajectory support, residual dependence, error propagation, missingness map, imputation decision, and provenance.'''),code("ch18-dyn-setup",SETUP),code("ch18-dyn-run",'''OUTPUT<-file.path(REPOSITORY_ROOT,"companion","outputs","ch18","01_dynamic_error_and_missingness")
result<-run_dynamic_error_missingness(file.path(DATA_ROOT,"trajectory_frames.tsv"),file.path(DATA_ROOT,"series_boundaries.tsv"),file.path(DATA_ROOT,"measurement_validation.tsv"),file.path(DATA_ROOT,"missingness_codes.tsv"),file.path(DATA_ROOT,"error_scenarios.tsv"),file.path(DATA_ROOT,"complex_model_spec.yaml"),file.path(REPOSITORY_ROOT,"companion","templates","sensitivity_analysis_spec.yaml"),OUTPUT)
stopifnot(nrow(result$measurement)==60,!result$decisions$frame_count_is_replication_count,!result$decisions$structural_absence_imputed)
print(result$residual_dependence);print(result$missingness);print(aggregate(estimate~scenario_id,result$measurement,range))'''),md("ch18-dyn-prompt",'''## Learner gate

State one question for which the midpoint benchmark is sufficient and one for which it destroys the estimand. Explain why the frame count cannot replace the token count. Then compare validation-derived random error with the explicitly hypothetical differential bias and identify which missingness reasons are observation processes, censoring, or absence of the event itself.'''),code("ch18-dyn-decision",'''required<-c("trajectory_support.tsv","benchmark_model.rds","dynamic_model.rds","residual_dependence.tsv","measurement_error_results.tsv","missingness_map.tsv","imputation_diagnostics.html","run_provenance.json");stopifnot(all(file.exists(file.path(OUTPUT,required))));print(result$decisions)''')]
SECOND=[md("ch18-pred-title",'''# Chapter 18. Prediction validation and model scope

**Learning objective.** Match the validation partition to the intended new unit, keep preprocessing inside training folds, report calibration and domain errors, and separate predictive evidence from explanation.

**Estimated time:** 120 minutes. **Exercise:** 18.4. Row-random, speaker-, item-, session-, and corpus-held-out estimates answer different deployment questions.'''),md("ch18-pred-contract",'''## Input and output contract

Inputs are a complete synthetic token-level feature table, bounded model registry, fold policy, deployment domain, preprocessing recipe, outcome schema, claim map, and the first notebook's diagnostics. Outputs include auditable fold assignments, leakage checks, fold-level performance and calibration, domain errors, model comparison, four-dimensional scope gate, and provenance.'''),code("ch18-pred-setup",SETUP),code("ch18-pred-run",'''DYNAMIC<-file.path(REPOSITORY_ROOT,"companion","outputs","ch18","01_dynamic_error_and_missingness");if(!dir.exists(DYNAMIC))stop("Run the first Chapter 18 notebook first.")
OUTPUT<-file.path(REPOSITORY_ROOT,"companion","outputs","ch18","02_prediction_validation_and_scope")
result<-run_prediction_validation_scope(file.path(DATA_ROOT,"prediction_features.tsv"),file.path(DATA_ROOT,"candidate_models.tsv"),file.path(DATA_ROOT,"fold_policy.yaml"),file.path(DATA_ROOT,"deployment_domain.yaml"),file.path(DATA_ROOT,"preprocessing_recipe.yaml"),file.path(DATA_ROOT,"outcome_schema.yaml"),file.path(DATA_ROOT,"claim_map.yaml"),DYNAMIC,OUTPUT)
stopifnot(nrow(result$folds)==720,result$gate$decision=="restrict",!result$gate$row_random_is_new_speaker_evidence,!result$gate$predictive_success_implies_causation)
print(result$comparison);print(result$audit);print(result$gate)'''),md("ch18-pred-prompt",'''## Learner decision

Compare the five validation schemes without treating them as interchangeable accuracy estimates. Identify every unit that overlaps between train and test, then state the deployment claim supported by each split. Write the final scope in four parts—population, measurement, predictor, and goal—and explain why predictive success does not identify a phonetic mechanism.'''),code("ch18-pred-decision",'''required<-c("fold_assignments.tsv","leakage_audit.tsv","validation_performance.tsv","calibration.tsv","domain_errors.tsv","model_comparison.tsv","model_scope_gate.yaml","run_provenance.json");stopifnot(all(file.exists(file.path(OUTPUT,required))),result$decisions$all_preprocessing_inside_folds);print(result$decisions)''')]
def main():
 TARGET.mkdir(parents=True,exist_ok=True)
 for name,payload in {"01_dynamic_error_and_missingness.ipynb":nb(FIRST),"02_prediction_validation_and_scope.ipynb":nb(SECOND)}.items():(TARGET/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if __name__=="__main__":main()
