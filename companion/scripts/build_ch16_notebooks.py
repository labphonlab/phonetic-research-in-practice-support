#!/usr/bin/env python3
"""Build the two Chapter 16 Python notebooks."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];TARGET=ROOT/"companion"/"notebooks"/"ch16"
def md(i,s):return {"cell_type":"markdown","id":i,"metadata":{},"source":s}
def code(i,s):return {"cell_type":"code","execution_count":None,"id":i,"metadata":{},"outputs":[],"source":s}
def nb(c):return {"cells":c,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.11+"},"phonetic_research_in_practice":{"book_chapter":16,"data_policy":"explicitly synthetic public pipeline fixture; protected route configuration only","schema_version":"0.1"}},"nbformat":4,"nbformat_minor":5}
SETUP='''from pathlib import Path
import sys
start=Path.cwd().resolve()
for candidate in (start,*start.parents):
    if (candidate / "companion" / "data" / "MANIFEST.tsv").is_file(): REPOSITORY_ROOT=candidate;break
else: raise RuntimeError("Run from the repository root or a subdirectory.")
SRC=REPOSITORY_ROOT/"companion"/"src";sys.path.insert(0,str(SRC)) if str(SRC) not in sys.path else None
DATA_ROOT=REPOSITORY_ROOT/"companion"/"data"/"ch16"/"synthetic_pipeline"
if not DATA_ROOT.exists():raise FileNotFoundError("Chapter 16 fixture absent. Run companion/scripts/generate_ch16_fixture.py explicitly; no data are substituted silently.")
print("DATA STATUS: SYNTHETIC_TEACHING_FIXTURE — public software-behavior fixture; protected route is configuration only.")'''
GRAPH=[md("ch16-graph-title",'''# Chapter 16. Pipeline graphs and data contracts

**Learning objective.** Convert the evidential chain into an explicit dependency graph and test schemas, identifiers, joins, configuration defaults, invariants, and public/protected route separation.

**Estimated time:** 90 minutes. **Exercises:** 16.1–16.3. Passing tests establishes behavior on the synthetic fixture, not validity of a scientific interpretation.'''),md("ch16-graph-contract",'''## Input and output contract

Inputs are a pipeline specification, schemas, immutable measurements, a correction table, and deliberate adverse cases. Reusable code validates the canonical route and confirms that duplicate keys, negative intervals, and missing required values fail. The notebook writes the graph, contract and join audits, resolved configuration, invariants, and provenance.'''),code("ch16-graph-setup",SETUP),code("ch16-graph-run",'''from phonetic_research_companion.ch16 import run_pipeline_graph_and_contracts
OUTPUT=REPOSITORY_ROOT/"companion"/"outputs"/"ch16"/"01_pipeline_graph_and_data_contracts"
result=run_pipeline_graph_and_contracts(DATA_ROOT/"pipeline_spec.yaml",DATA_ROOT/"data_contracts.yaml",DATA_ROOT/"source_measurements.tsv",DATA_ROOT/"correction_table.tsv",DATA_ROOT/"adverse_cases.tsv",OUTPUT)
assert result["decision"]["canonical_contracts_pass"] and result["decision"]["adverse_failures_detected"]==3
assert result["decision"]["source_unchanged"] and not result["decision"]["protected_data_accessed"]
for row in result["validation"]:print(row)'''),md("ch16-graph-prompt",'''## Learner gate

Trace one reported value from immutable source through correction, derivative, summary, and reproduction assessment. Explain why the three adverse failures are successful tests rather than failed research runs. Add one hidden dependency to the graph and specify which cached outputs it must invalidate.'''),code("ch16-graph-decision",'''required=["pipeline_graph.svg","contract_validation.tsv","join_audit.tsv","configuration_resolved.yaml","scientific_invariants.tsv","run_provenance.json"]
assert all((OUTPUT/name).exists() for name in required);print(result["decision"])''')]
CLEAN=[md("ch16-clean-title",'''# Chapter 16. Clean-run reproduction

**Learning objective.** Regenerate declared public artifacts without stale state, compare them exactly or within tolerance, apply scientific invariants and a privacy allowlist, and distinguish exact, numerical, substantive, and interpretive claims.

**Estimated time:** 90 minutes. **Exercise:** 16.4. The protected profile is not executed; it contains no source data and requires an authorized local path.'''),md("ch16-clean-contract",'''## Input and output contract

Inputs are the resolved specification, public synthetic sources, expected-artifact manifest, tolerance policy, and public field allowlist. Outputs include a clean-run summary, artifact comparisons, machine-readable tests, privacy scan, reproduction assessment, verified manifest, and provenance.'''),code("ch16-clean-setup",SETUP),code("ch16-clean-run",'''from phonetic_research_companion.ch16 import run_clean_reproduction
RESOLVED=REPOSITORY_ROOT/"companion"/"outputs"/"ch16"/"01_pipeline_graph_and_data_contracts"/"configuration_resolved.yaml"
if not RESOLVED.exists():raise FileNotFoundError("Run 01_pipeline_graph_and_data_contracts.ipynb first; resolved configuration is not substituted.")
OUTPUT=REPOSITORY_ROOT/"companion"/"outputs"/"ch16"/"02_clean_run_and_reproduction"
result=run_clean_reproduction(DATA_ROOT/"pipeline_spec.yaml",RESOLVED,DATA_ROOT/"source_measurements.tsv",DATA_ROOT/"correction_table.tsv",DATA_ROOT/"expected_artifacts.tsv",DATA_ROOT/"expected",DATA_ROOT/"tolerance_policy.yaml",DATA_ROOT/"public_allowlist.txt",OUTPUT)
assert result["assessment"]["decision"]=="pass_public_fixture" and len(result["analysis"])==11
assert not result["assessment"]["protected_route_executed"] and not result["assessment"]["scientific_interpretation_warranted_by_run"]
print(result["comparisons"]);print(result["privacy"])'''),md("ch16-clean-prompt",'''## Learner decision

Classify each comparison as exact, numerical, substantive, or interpretive. Explain why successful public-fixture reproduction neither reproduces a protected-data result nor warrants its scientific interpretation. Introduce a controlled numerical change, apply the declared tolerance, and record whether it changes only bytes, a reported number, or the claim gate.'''),code("ch16-clean-decision",'''required=["clean_run_summary.json","artifact_comparison.tsv","test_report.xml","privacy_scan.tsv","reproduction_assessment.yaml","verified_artifact_manifest.tsv","run_provenance.json"]
assert all((OUTPUT/name).exists() for name in required);print(result["assessment"])''')]
def main():
    TARGET.mkdir(parents=True,exist_ok=True)
    for n,p in {"01_pipeline_graph_and_data_contracts.ipynb":nb(GRAPH),"02_clean_run_and_reproduction.ipynb":nb(CLEAN)}.items():(TARGET/n).write_text(json.dumps(p,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if __name__=="__main__":main()
