#!/usr/bin/env python3
"""Build the two Chapter 14 R notebooks."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; TARGET = ROOT / "companion" / "notebooks" / "ch14"
def markdown(i, s): return {"cell_type":"markdown","id":i,"metadata":{},"source":s}
def code(i, s): return {"cell_type":"code","execution_count":None,"id":i,"metadata":{},"outputs":[],"source":s}
def notebook(cells): return {"cells":cells,"metadata":{"kernelspec":{"display_name":"R","language":"R","name":"ir"},"language_info":{"name":"R","version":"4.6.1"},"phonetic_research_in_practice":{"book_chapter":14,"data_policy":"explicitly synthetic measurement-error simulation","schema_version":"0.1"}},"nbformat":4,"nbformat_minor":5}
SETUP='''find_repository <- function(start=getwd()) { current<-normalizePath(start,mustWork=TRUE); repeat { if (file.exists(file.path(current, "companion", "data", "MANIFEST.tsv"))) return(current); parent<-dirname(current); if (identical(parent,current)) stop("Run from the repository root or a subdirectory."); current<-parent } }
REPOSITORY_ROOT<-find_repository(); DATA_ROOT<-file.path(REPOSITORY_ROOT,"companion","data","ch14","synthetic_error")
if (!dir.exists(DATA_ROOT)) stop("Chapter 14 fixture absent. Run companion/scripts/generate_ch14_fixture.py explicitly; no data are substituted silently.")
source(file.path(REPOSITORY_ROOT,"companion","r","ch14.R")); cat("DATA STATUS: SYNTHETIC_TEACHING_FIXTURE — simulated measurement error, not empirical uncertainty.\n")'''
ERROR=[markdown("ch14-error-title",'''# Chapter 14. Error maps and propagation

**Learning objective.** Separate random, differential, landmark, and shared-reference error and propagate each at the dependency level where it arises.

**Estimated time:** 90 minutes. **Exercises:** 14.1 and 14.2. Observed fixture diagnostics and generator-known hypothetical ranges remain separately labeled.'''),markdown("ch14-error-contract",'''## Input and output contract

Inputs are the frozen synthetic analysis table, validation pairs, repeated landmarks, an error map, and the sensitivity specification. The notebook writes measured error components and a hash-addressed manifest plus estimates for 240 propagated datasets; it never overwrites the raw layer.'''),code("ch14-error-setup",SETUP),code("ch14-error-run",'''OUTPUT<-file.path(REPOSITORY_ROOT,"companion","outputs","ch14","01_error_propagation")
result<-run_error_propagation(file.path(DATA_ROOT,"sensitivity_analysis_spec.yaml"),file.path(DATA_ROOT,"error_map.tsv"),file.path(DATA_ROOT,"validation_pairs.tsv"),file.path(DATA_ROOT,"repeated_measurements.tsv"),file.path(DATA_ROOT,"raw_analysis_data.tsv"),OUTPUT)
stopifnot(nrow(result$components)==6,nrow(result$manifest)==240,result$raw_unchanged)
print(result$components); print(aggregate(estimate~mechanism+estimand,result$effects,function(x)c(median=median(x),min=min(x),max=max(x))))'''),markdown("ch14-error-prompt",'''## Learner gate

Explain why independent outcome error, predictor error, a shared landmark shift, speaker-level reference error, differential group bias, and differential missingness cannot be represented by one global reliability coefficient. For the landmark rows, explain why aligned boundaries can preserve duration while corrupting alignment.'''),code("ch14-error-decision",'''stopifnot(all(file.exists(file.path(OUTPUT,c("error_components.tsv","propagated_datasets_manifest.tsv","measurement_effects.tsv","error_diagnostics.html","run_provenance.json"))))); print(result$primary)''')]
SENS=[markdown("ch14-sens-title",'''# Chapter 14. A bounded sensitivity universe

**Learning objective.** Execute the primary configuration first, retain every attempted specification and failure, and evaluate direction, magnitude, scope, and diagnostics without significance voting.

**Estimated time:** 90 minutes. **Exercises:** 14.3 and 14.4. All numerical results describe a generated sample only.'''),markdown("ch14-sens-contract",'''## Input and output contract

Inputs are the frozen synthetic analysis table, an ordered configuration table, and a prespecified claim-stability rule. Outputs include successful results, failures, stability dimensions, an HTML result universe, a conclusion map, a claim gate, and provenance containing execution order.'''),code("ch14-sens-setup",SETUP),code("ch14-sens-run",'''OUTPUT<-file.path(REPOSITORY_ROOT,"companion","outputs","ch14","02_sensitivity_universe")
result<-run_sensitivity_universe(file.path(DATA_ROOT,"raw_analysis_data.tsv"),file.path(DATA_ROOT,"specification_table.tsv"),file.path(DATA_ROOT,"sensitivity_analysis_spec.yaml"),OUTPUT)
stopifnot(result$results$configuration_id[[1]]=="primary",nrow(result$failures)==1,result$failures$retained_in_denominator[[1]])
print(result$results); print(result$stability)'''),markdown("ch14-sens-prompt",'''## Learner decision

Write an overclaim, an excessively vague claim, a calibrated primary claim, and a limitation. Map each phrase in the calibrated version to the result table. Explain why the changed-estimand and exploratory branches cannot replace the primary result, and why the retained failed specification is not a negative vote.'''),code("ch14-sens-decision",'''stopifnot(all(file.exists(file.path(OUTPUT,c("specification_results.tsv","specification_failures.tsv","claim_stability.tsv","specification_curve.html","conclusion_map.yaml","claim_stability_gate.yaml","run_provenance.json"))))); stopifnot(!result$gate$significance_vote_permitted); print(result$gate)''')]
def main():
    TARGET.mkdir(parents=True,exist_ok=True)
    for name,payload in {"01_error_propagation.ipynb":notebook(ERROR),"02_sensitivity_universe.ipynb":notebook(SENS)}.items(): (TARGET/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if __name__=="__main__": main()
