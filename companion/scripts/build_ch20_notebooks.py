#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];TARGET=ROOT/"companion"/"notebooks"/"ch20"
def md(i,s):return {"cell_type":"markdown","id":i,"metadata":{},"source":s}
def code(i,s):return {"cell_type":"code","execution_count":None,"id":i,"metadata":{},"outputs":[],"source":s}
def nb(c):return {"cells":c,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.11+"},"phonetic_research_in_practice":{"book_chapter":20,"data_policy":"internal synthetic release candidate; no deposit or publication","schema_version":"0.1"}},"nbformat":4,"nbformat_minor":5}
SETUP='''from pathlib import Path
import sys
start=Path.cwd().resolve()
for candidate in (start,*start.parents):
    if (candidate / "companion" / "data" / "MANIFEST.tsv").is_file(): REPOSITORY_ROOT=candidate;break
else: raise RuntimeError("Run from the repository root or a subdirectory.")
SRC=REPOSITORY_ROOT/"companion"/"src";sys.path.insert(0,str(SRC)) if str(SRC) not in sys.path else None
DATA_ROOT=REPOSITORY_ROOT/"companion"/"data"/"ch20"/"release_candidate"
if not DATA_ROOT.exists():raise FileNotFoundError("Chapter 20 fixture absent. Run companion/scripts/generate_ch20_fixture.py explicitly.")
print("RELEASE STATUS: INTERNAL CANDIDATE — no deposit, DOI registration, publication, or protected-data access is authorized.")'''
FIRST=[md("ch20-audit-title",'''# Chapter 20. Release manifest and privacy audit

**Learning objective.** Build a release candidate from an explicit allowlist and audit identity, fixity, license, privacy, media, notebook state, and attributable human authorization without inferring permission from filenames.

**Estimated time:** 110 minutes. **Exercises:** 20.1–20.3. This notebook creates an internal candidate only. Pending rights and unsigned governance records fail public-release authorization by design.'''),md("ch20-audit-contract",'''## Input and output contract

Inputs are the release specification, allowlist manifest, license matrix, governance decisions, citation metadata, and public/protected route profiles. Outputs include the internal candidate, checksums, license and privacy audits, human-review record, exclusions, and provenance. The protected profile is inspected as configuration but never resolved or executed.'''),code("ch20-audit-setup",SETUP),code("ch20-audit-run",'''from phonetic_research_companion.ch20 import build_candidate
OUTPUT=REPOSITORY_ROOT/"companion"/"outputs"/"ch20"/"01_release_manifest_and_privacy_audit"
result=build_candidate(REPOSITORY_ROOT,DATA_ROOT/"release_spec.yaml",DATA_ROOT/"release_manifest.tsv",DATA_ROOT/"license_matrix.tsv",DATA_ROOT/"governance_decisions.tsv",DATA_ROOT/"citation_metadata.yaml",DATA_ROOT/"public_profile.yaml",DATA_ROOT/"protected_profile.yaml",OUTPUT)
assert result["decisions"]["privacy_scan_pass"] and not result["decisions"]["license_public_release_pass"]
assert not result["decisions"]["human_public_release_approval"] and not result["decisions"]["protected_route_accessed"]
print(result["decisions"]);print(*result["exclusions"],sep="\\n")'''),md("ch20-audit-prompt",'''## Learner gate

Explain why a passing automated privacy scan cannot replace rights and governance approval. For every excluded artifact, identify the authority and record needed to change its disposition. Add a deliberately unsafe file to a separate test directory and confirm that the scanner detects it without placing it in the candidate.'''),code("ch20-audit-decision",'''required=["release_candidate_manifest.tsv","checksum_manifest.txt","license_audit.tsv","privacy_scan.tsv","human_review.tsv","release_exclusions.tsv","run_provenance.json"]
assert all((OUTPUT/name).exists() for name in required);assert len(result["manifest"])==9;print(result["decisions"])''')]
SECOND=[md("ch20-release-title",'''# Chapter 20. Clean release and archival preparation

**Learning objective.** Rebuild the allowlisted candidate in an empty directory, verify exact artifacts and availability wording, prepare archival metadata and stewardship records, and distinguish technical readiness from authorization to deposit.

**Estimated time:** 110 minutes. **Exercises:** 20.3–20.4. No network deposit, DOI registration, release tag, or publication action occurs.'''),md("ch20-release-contract",'''## Input and output contract

Inputs are the verified first candidate, release specification, canonical allowlist, availability template, maintenance policy, and citation placeholders. Outputs record the clean rebuild, artifact comparison, accurate availability statement, non-deposited archive metadata, maintenance and withdrawal policy, release gate, and provenance.'''),code("ch20-release-setup",SETUP),code("ch20-release-run",'''from phonetic_research_companion.ch20 import clean_verify
FIRST=REPOSITORY_ROOT/"companion"/"outputs"/"ch20"/"01_release_manifest_and_privacy_audit"/"release_candidate_manifest.tsv"
if not FIRST.exists():raise FileNotFoundError("Run notebook 1 first; candidate verification is not substituted.")
OUTPUT=REPOSITORY_ROOT/"companion"/"outputs"/"ch20"/"02_clean_release_and_archive"
result=clean_verify(REPOSITORY_ROOT,DATA_ROOT/"release_spec.yaml",DATA_ROOT/"release_manifest.tsv",FIRST,DATA_ROOT/"availability_statement_template.md",DATA_ROOT/"maintenance_policy.md",DATA_ROOT/"citation_metadata.yaml",OUTPUT)
assert result["run"]["technical_pass"] and result["gate"]["decision"]=="postpone_deposit_pending_author_and_publisher"
assert not result["gate"]["deposit_authorized"] and not result["gate"]["candidate_is_public_release"]
print(result["run"]);print(result["archive"]);print(result["gate"])'''),md("ch20-release-prompt",'''## Learner decision

Verify every sentence in the availability statement against the manifest and gate. Distinguish technical reconstruction, scientific correctness, license compatibility, and governance authority. Draft—but do not execute—the steps that would follow only after author and publisher approval, including creation of version-specific and concept identifiers.'''),code("ch20-release-decision",'''required=["public_clean_run.json","artifact_verification.tsv","availability_statement.md","archive_metadata.json","maintenance_and_withdrawal.md","reproducible_release_gate.yaml","run_provenance.json"]
assert all((OUTPUT/name).exists() for name in required);assert all(x["exact_match"] for x in result["verification"]);assert not result["run"]["deposit_attempted"] and not result["run"]["publication_attempted"];print(result["gate"])''')]
def main():
 TARGET.mkdir(parents=True,exist_ok=True)
 for name,payload in {"01_release_manifest_and_privacy_audit.ipynb":nb(FIRST),"02_clean_release_and_archive.ipynb":nb(SECOND)}.items():(TARGET/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if __name__=="__main__":main()
