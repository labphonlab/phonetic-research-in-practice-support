#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];TARGET=ROOT/"companion"/"notebooks"/"ch19"
def md(i,s):return {"cell_type":"markdown","id":i,"metadata":{},"source":s}
def code(i,s):return {"cell_type":"code","execution_count":None,"id":i,"metadata":{},"outputs":[],"source":s}
def nb(c):return {"cells":c,"metadata":{"kernelspec":{"display_name":"R","language":"R","name":"ir"},"language_info":{"name":"R","version":"4.6.1"},"phonetic_research_in_practice":{"book_chapter":19,"data_policy":"explicitly synthetic interpretation fixture; human claim approval required","schema_version":"0.1"}},"nbformat":4,"nbformat_minor":5}
SETUP='''find_repository<-function(start=getwd()){current<-normalizePath(start,mustWork=TRUE);repeat{if(file.exists(file.path(current, "companion", "data", "MANIFEST.tsv")))return(current);parent<-dirname(current);if(identical(parent,current))stop("Run from the repository root or a subdirectory.");current<-parent}}
REPOSITORY_ROOT<-find_repository();DATA_ROOT<-file.path(REPOSITORY_ROOT,"companion","data","ch19","synthetic_claims");if(!dir.exists(DATA_ROOT))stop("Chapter 19 fixture absent. Run companion/scripts/generate_ch19_fixture.py explicitly; no data are substituted silently.");source(file.path(REPOSITORY_ROOT,"companion","r","ch19.R"));cat("DATA STATUS: SYNTHETIC_TEACHING_FIXTURE — interpretation audit, not scientific claim approval.\n")'''
FIRST=[md("ch19-result-title",'''# Chapter 19. Results, uncertainty, and meaningful bounds

**Learning objective.** Separate direction, magnitude, precision, and relevance; assess prospective bounds without converting nonsignificance into equivalence; and calculate Type S and Type M risks from declared scenarios rather than the observed estimate.

**Estimated time:** 100 minutes. **Exercises:** 19.1–19.3. The supplied bounds and true-effect scenarios are synthetic design specifications, not empirically established thresholds.'''),md("ch19-result-contract",'''## Input and output contract

Inputs are Chapter 17 focal contrasts, Chapter 18's scope gate, the claim-map specification, prospective bound record, design scenarios, and Chapter 14 sensitivity conclusion. Outputs retain research-scale results, bound provenance, equivalence assessments, Type S/M simulations, diagnostics, and provenance.'''),code("ch19-result-setup",SETUP),code("ch19-result-run",'''OUTPUT<-file.path(REPOSITORY_ROOT,"companion","outputs","ch19","01_results_uncertainty_and_equivalence")
result<-run_results_uncertainty(file.path(REPOSITORY_ROOT,"companion","outputs","ch17","02_diagnostics_predictions_and_reporting","focal_contrasts.tsv"),file.path(REPOSITORY_ROOT,"companion","outputs","ch18","02_prediction_validation_and_scope","model_scope_gate.yaml"),file.path(DATA_ROOT,"claim_evidence_map.yaml"),file.path(DATA_ROOT,"meaningful_bounds.tsv"),file.path(DATA_ROOT,"effect_scenarios.tsv"),file.path(REPOSITORY_ROOT,"companion","outputs","ch14","02_sensitivity_universe","conclusion_map.yaml"),OUTPUT)
stopifnot(nrow(result$results)==2,nrow(result$risk)==6,result$decisions$inconclusive_retained,!result$decisions$observed_estimate_used_as_scenario_truth)
print(result$results);print(result$equivalence);print(result$risk)'''),md("ch19-result-prompt",'''## Learner gate

Rewrite a threshold-based result using estimate, interval, averaging distribution, diagnostics, and scope. Explain why the SHIFT_B assessment remains inconclusive under its declared bound. Compare Type S and Type M risks across scenarios without treating any supplied scenario as observed truth or an empirical phonetic threshold.'''),code("ch19-result-decision",'''required<-c("research_scale_results.tsv","meaningful_bounds.tsv","equivalence_assessment.tsv","sign_magnitude_risk.tsv","interpretation_diagnostics.html","run_provenance.json");stopifnot(all(file.exists(file.path(OUTPUT,required))),!result$decisions$threshold_generated_claims);print(result$decisions)''')]
SECOND=[md("ch19-claim-title",'''# Chapter 19. Claim–evidence mapping

**Learning objective.** Test the force and reach of proposed clauses against result, diagnostic, sensitivity, population, measurement, prediction, and theoretical-identification evidence.

**Estimated time:** 100 minutes. **Exercise:** 19.4. The workflow detects contradictions and required revisions; it does not generate or approve scientific prose from p-values.'''),md("ch19-claim-contract",'''## Input and output contract

Inputs are the frozen draft claims, evidence inventory, Chapter 17 result and regression gate, Chapter 15 corpus gate, Chapter 18 scope gate, and Chapter 14 sensitivity conclusion. Outputs preserve every claim, support link, unsupported clause, domain statement, calibrated-claim gate, and provenance. Final wording remains a human scientific decision.'''),code("ch19-claim-setup",SETUP),code("ch19-claim-run",'''OUTPUT<-file.path(REPOSITORY_ROOT,"companion","outputs","ch19","02_claim_evidence_map")
result<-run_claim_evidence_map(file.path(DATA_ROOT,"claim_evidence_map.yaml"),file.path(DATA_ROOT,"draft_claim_registry.tsv"),file.path(DATA_ROOT,"evidence_inventory.tsv"),file.path(REPOSITORY_ROOT,"companion","outputs","ch17","02_diagnostics_predictions_and_reporting","focal_contrasts.tsv"),file.path(REPOSITORY_ROOT,"companion","outputs","ch17","02_diagnostics_predictions_and_reporting","structured_regression_gate.yaml"),file.path(REPOSITORY_ROOT,"companion","outputs","ch15","02_representativeness_and_cross_corpus","corpus_inference_gate.yaml"),file.path(REPOSITORY_ROOT,"companion","outputs","ch18","02_prediction_validation_and_scope","model_scope_gate.yaml"),file.path(REPOSITORY_ROOT,"companion","outputs","ch14","02_sensitivity_universe","conclusion_map.yaml"),OUTPUT)
stopifnot(result$gate$decision=="require_revision_and_human_approval",result$gate$claims_failed>=3,!result$gate$automatic_claim_generation,!result$gate$final_wording_approved)
print(result$registry);print(result$unsupported);print(result$gate)'''),md("ch19-claim-prompt",'''## Learner decision

For each failed clause, decide whether to remove it, narrow its force or reach, or supply a genuinely independent evidence source. Draft final wording yourself, preserving synthetic status and observed-item scope. Explain why a prediction claim, a mechanism hypothesis, and a causal explanation require different evidence even when they cite the same numerical result.'''),code("ch19-claim-decision",'''required<-c("claim_registry.tsv","claim_support.tsv","unsupported_clauses.tsv","domain_statements.tsv","calibrated_claim_gate.yaml","run_provenance.json");stopifnot(all(file.exists(file.path(OUTPUT,required))),!result$gate$causal_claim_approved,!result$gate$new_item_generalization_approved,!result$gate$external_corpus_generalization_approved);print(result$gate)''')]
def main():
 TARGET.mkdir(parents=True,exist_ok=True)
 for name,payload in {"01_results_uncertainty_and_equivalence.ipynb":nb(FIRST),"02_claim_evidence_map.ipynb":nb(SECOND)}.items():(TARGET/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if __name__=="__main__":main()
