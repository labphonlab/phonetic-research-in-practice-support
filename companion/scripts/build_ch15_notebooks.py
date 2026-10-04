#!/usr/bin/env python3
"""Build the two Chapter 15 Python notebooks."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; TARGET=ROOT/"companion"/"notebooks"/"ch15"
def md(i,s): return {"cell_type":"markdown","id":i,"metadata":{},"source":s}
def code(i,s): return {"cell_type":"code","execution_count":None,"id":i,"metadata":{},"outputs":[],"source":s}
def nb(cells): return {"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.11+"},"phonetic_research_in_practice":{"book_chapter":15,"data_policy":"explicitly synthetic corpus sampling fixture","schema_version":"0.1"}},"nbformat":4,"nbformat_minor":5}
SETUP='''from pathlib import Path
import sys
start=Path.cwd().resolve()
for candidate in (start,*start.parents):
    if (candidate / "companion" / "data" / "MANIFEST.tsv").is_file(): REPOSITORY_ROOT=candidate; break
else: raise RuntimeError("Run from the repository root or a subdirectory.")
SOURCE_ROOT=REPOSITORY_ROOT/"companion"/"src"; sys.path.insert(0,str(SOURCE_ROOT)) if str(SOURCE_ROOT) not in sys.path else None
DATA_ROOT=REPOSITORY_ROOT/"companion"/"data"/"ch15"/"synthetic_corpus"
if not DATA_ROOT.exists(): raise FileNotFoundError("Chapter 15 fixture absent. Run companion/scripts/generate_ch15_fixture.py explicitly; no data are substituted silently.")
print("DATA STATUS: SYNTHETIC_TEACHING_FIXTURE — generated corpus records, not licensed or participant data.")'''
QUERY=[md("ch15-query-title",'''# Chapter 15. Query and denominator audit

**Learning objective.** Preserve every raw corpus hit, reconstruct each selection transition, and expose differential attrition across speakers, items, sessions, conversations, conditions, and corpora.

**Estimated time:** 90 minutes. **Exercises:** 15.1–15.3. The bundled corpus rows are explicitly synthetic; no licensed recordings, transcripts, or participant identifiers are included.'''),md("ch15-query-contract",'''## Input and output contract

Inputs are generated searchable hits, lexical linkage records, a frozen versioned query, and a public synthetic access profile. Outputs include the query run, complete candidate manifest, token flow, domain-level attrition, linkage audit, diagnostics, and provenance. Duplicates and failures remain in the denominator.'''),code("ch15-query-setup",SETUP),code("ch15-query-run",'''from phonetic_research_companion.ch15 import run_query_and_denominator_audit
OUTPUT=REPOSITORY_ROOT/"companion"/"outputs"/"ch15"/"01_query_and_denominator_audit"
result=run_query_and_denominator_audit(DATA_ROOT/"searchable_hits.tsv",DATA_ROOT/"linkage_table.tsv",DATA_ROOT/"query_config.yaml",DATA_ROOT/"corpus_access_profile.yaml",OUTPUT)
assert len(result["candidates"])==640 and result["query_run"]["unique_source_tokens"]==600
assert result["decisions"]["duplicates_retained"]==40 and result["decisions"]["raw_unchanged"]
for row in result["flow"]: print(row)'''),md("ch15-query-prompt",'''## Learner gate

Define the target population, corpus population, searchable universe, measurable sample, and analysis sample before interpreting the flow. Compare losses by corpus, speaker, item, conversation, and condition. Explain how overlap, measurement failure, and ambiguous linkage imply different repairs, and design a stratified forced-alignment audit without discarding failed boundaries.'''),code("ch15-query-decision",'''required=["query_run.json","candidate_manifest.tsv","token_flow.tsv","attrition_by_domain.tsv","linkage_audit.tsv","selection_diagnostics.html","run_provenance.json"]
assert all((OUTPUT/name).exists() for name in required); print(result["query_run"])''')]
REP=[md("ch15-rep-title",'''# Chapter 15. Representativeness and cross-corpus compatibility

**Learning objective.** Evaluate support relative to a declared population and claim, identify unsupported cells, and restrict cross-corpus inference before harmonization or modeling.

**Estimated time:** 90 minutes. **Exercises:** 15.1 and 15.4. Generated category counts illustrate an audit; they cannot certify empirical representativeness.'''),md("ch15-rep-contract",'''## Input and output contract

Inputs are the frozen candidate manifest from the first notebook, a target-population specification, corpus-design metadata, and a cross-corpus compatibility map. Outputs record population and higher-level support, compatibility, unsupported domains, a corpus inference gate, diagnostics, and provenance.'''),code("ch15-rep-setup",SETUP),code("ch15-rep-run",'''from phonetic_research_companion.ch15 import run_representativeness_and_cross_corpus
CANDIDATES=REPOSITORY_ROOT/"companion"/"outputs"/"ch15"/"01_query_and_denominator_audit"/"candidate_manifest.tsv"
if not CANDIDATES.exists(): raise FileNotFoundError("Run 01_query_and_denominator_audit.ipynb first; a candidate denominator is not substituted.")
OUTPUT=REPOSITORY_ROOT/"companion"/"outputs"/"ch15"/"02_representativeness_and_cross_corpus"
result=run_representativeness_and_cross_corpus(CANDIDATES,DATA_ROOT/"target_population.yaml",DATA_ROOT/"corpus_design.tsv",DATA_ROOT/"cross_corpus_map.tsv",OUTPUT)
assert result["gate"]["decision"]=="restrict" and not result["gate"]["synthetic_fixture_is_population_evidence"]
for row in result["support"]: print(row)
for row in result["compatibility"]: print(row)'''),md("ch15-rep-prompt",'''## Learner decision

State the narrowest supported generated domain and identify attractive broader claims that fail. Explain why weighting is not justified without authorized target margins and overlap, and why relabeling manual and automatic word boundaries would not make the corpora equivalent. Draft a conditional cross-corpus claim that retains corpus-defined populations and incompatible recording histories.'''),code("ch15-rep-decision",'''required=["population_support.tsv","higher_level_support.tsv","compatibility_table.tsv","unsupported_domains.tsv","corpus_inference_gate.yaml","representativeness_report.html","run_provenance.json"]
assert all((OUTPUT/name).exists() for name in required); print(result["gate"])''')]
def main():
    TARGET.mkdir(parents=True,exist_ok=True)
    for name,payload in {"01_query_and_denominator_audit.ipynb":nb(QUERY),"02_representativeness_and_cross_corpus.ipynb":nb(REP)}.items(): (TARGET/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if __name__=="__main__": main()
