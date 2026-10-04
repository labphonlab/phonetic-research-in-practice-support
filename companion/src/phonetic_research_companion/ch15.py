"""Chapter 15 query denominators and corpus-inference audits."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

from . import __version__


STATUS = "SYNTHETIC_TEACHING_FIXTURE"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256(); digest.update(path.read_bytes()); return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as source: return list(csv.DictReader(source, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", extrasaction="ignore"); writer.writeheader()
        for row in rows: writer.writerow({field: row.get(field, "") for field in fields})


def as_bool(value: Any) -> bool: return str(value).lower() == "true"


def html_table(rows: list[dict[str, Any]], fields: list[str]) -> str:
    h = "".join(f"<th>{html.escape(f)}</th>" for f in fields)
    b = "".join("<tr>" + "".join(f"<td>{html.escape(str(row.get(f,'')))}</td>" for f in fields) + "</tr>" for row in rows)
    return f"<table border='1'><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>"


def provenance(path: Path, tool: str, inputs: list[Path], decisions: dict[str, Any]) -> None:
    payload = {"tool":tool,"tool_version":__version__,"run_at_utc":datetime.now(timezone.utc).isoformat(),"input_hashes":{str(p.resolve()):sha256_file(p) for p in inputs},"decisions":decisions}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def require_synthetic(rows: list[dict[str, str]], label: str) -> None:
    if not rows or not all(row.get("data_status") == STATUS for row in rows): raise ValueError(f"Bundled Chapter 15 {label} must remain explicitly synthetic")


def run_query_and_denominator_audit(hits_path: Path, linkage_path: Path, query_path: Path, access_path: Path, output_dir: Path) -> dict[str, Any]:
    source_hash = sha256_file(hits_path)
    hits = read_tsv(hits_path); links = read_tsv(linkage_path); query = yaml.safe_load(query_path.read_text(encoding="utf-8")); access = yaml.safe_load(access_path.read_text(encoding="utf-8"))
    require_synthetic(hits, "searchable hits"); require_synthetic(links, "linkage table")
    if query.get("data_status") != STATUS or access.get("data_status") != STATUS: raise ValueError("Query and access profiles must remain explicitly synthetic")
    link_index = {row["source_token_id"]: row for row in links}
    seen: dict[tuple[str, str], str] = {}; candidates: list[dict[str, Any]] = []
    stages = query["stage_order"]
    for index, hit in enumerate(hits, start=1):
        candidate_id = f"{query['query_id']}_{index:04d}"; key = (hit["corpus_id"], hit["source_token_id"])
        duplicate_of = seen.get(key, "")
        if not duplicate_of: seen[key] = candidate_id
        linkage = link_index.get(hit["source_token_id"], {"linkage_status":"unmatched","candidate_count":"0"})
        gates = {"raw_hit":True,"deduplicated":not bool(duplicate_of),"context_eligible":as_bool(hit["context_eligible"]),"signal_available":as_bool(hit["signal_available"]),"measurement_success":as_bool(hit["measurement_success"]),"quality_approved":as_bool(hit["quality_approved"]),"metadata_complete":as_bool(hit["metadata_complete"]),"linkage_matched":linkage["linkage_status"] == "matched"}
        cumulative = True
        for stage in stages[:-1]: cumulative = cumulative and gates[stage]; gates[stage] = cumulative
        gates["final_inclusion"] = cumulative
        exclusion = ""
        if not gates["deduplicated"]: exclusion = "duplicate"
        elif not as_bool(hit["context_eligible"]): exclusion = "context_ineligible"
        elif not as_bool(hit["signal_available"]): exclusion = "signal_unavailable"
        elif not as_bool(hit["measurement_success"]): exclusion = "measurement_failure"
        elif not as_bool(hit["quality_approved"]): exclusion = "quality_rejected"
        elif not as_bool(hit["metadata_complete"]): exclusion = "metadata_missing"
        elif linkage["linkage_status"] == "ambiguous": exclusion = "linkage_ambiguous"
        elif linkage["linkage_status"] != "matched": exclusion = "linkage_unmatched"
        row = {"candidate_id":candidate_id,"query_id":query["query_id"],**{k:hit[k] for k in ("source_hit_id","source_token_id","corpus_id","corpus_version","recording_id","speaker_id","session_id","conversation_id","item_id","condition_id","region","style","era")},"duplicate_of":duplicate_of,"linkage_status":linkage["linkage_status"],**gates,"exclusion_code":exclusion,"data_status":STATUS}
        candidates.append(row)
    flow = [{"stage_order":i+1,"stage":stage,"count":sum(bool(row[stage]) for row in candidates),"lost_from_previous":0 if i == 0 else sum(bool(row[stages[i-1]]) for row in candidates)-sum(bool(row[stage]) for row in candidates),"data_status":STATUS} for i,stage in enumerate(stages)]
    attrition: list[dict[str, Any]] = []
    for domain in ("corpus_id","speaker_id","item_id","session_id","conversation_id","condition_id"):
        groups: dict[str,list[dict[str,Any]]] = defaultdict(list)
        for row in candidates: groups[str(row[domain])].append(row)
        for value, subset in sorted(groups.items()):
            raw = len(subset); final = sum(bool(row["final_inclusion"]) for row in subset)
            attrition.append({"domain":domain,"domain_value":value,"raw_hits":raw,"final_inclusions":final,"excluded":raw-final,"inclusion_rate":final/raw if raw else 0,"data_status":STATUS})
    linkage_audit = [{"source_token_id":row["source_token_id"],"linkage_status":row["linkage_status"],"candidate_count":row["candidate_count"],"candidate_rows":sum(hit["source_token_id"] == row["source_token_id"] for hit in hits),"final_inclusions":sum(c["source_token_id"] == row["source_token_id"] and c["final_inclusion"] for c in candidates),"data_status":STATUS} for row in links]
    output_dir.mkdir(parents=True, exist_ok=True)
    query_run = {"data_status":STATUS,"query_id":query["query_id"],"query_expression":query["query_expression"],"corpus_versions":query["corpus_versions"],"annotation_version":query["annotation_version"],"access_profile":access["profile_id"],"raw_hits":len(candidates),"unique_source_tokens":len(seen),"final_inclusions":sum(row["final_inclusion"] for row in candidates),"source_hash":source_hash}
    (output_dir/"query_run.json").write_text(json.dumps(query_run,indent=2),encoding="utf-8")
    write_tsv(output_dir/"candidate_manifest.tsv",candidates,list(candidates[0])); write_tsv(output_dir/"token_flow.tsv",flow,list(flow[0])); write_tsv(output_dir/"attrition_by_domain.tsv",attrition,list(attrition[0])); write_tsv(output_dir/"linkage_audit.tsv",linkage_audit,list(linkage_audit[0]))
    report = "<!doctype html><meta charset='utf-8'><title>Corpus selection diagnostics</title><h1>Corpus selection diagnostics</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Counts demonstrate denominator preservation and are not corpus findings.</p>"+html_table(flow,list(flow[0]))+"<h2>Exclusion reasons</h2>"+html_table([{"reason":k or "included","count":v} for k,v in Counter(row["exclusion_code"] for row in candidates).items()],["reason","count"])
    (output_dir/"selection_diagnostics.html").write_text(report,encoding="utf-8")
    if sha256_file(hits_path) != source_hash: raise RuntimeError("Searchable hit source changed during audit")
    decisions={"raw_unchanged":True,"duplicates_retained":sum(bool(row["duplicate_of"]) for row in candidates),"final_inclusions":query_run["final_inclusions"],"interpretive_limit":"synthetic selection flow only"}
    provenance(output_dir/"run_provenance.json","phonetic_research_companion.ch15.run_query_and_denominator_audit",[hits_path,linkage_path,query_path,access_path],decisions)
    return {"candidates":candidates,"flow":flow,"attrition":attrition,"linkage":linkage_audit,"query_run":query_run,"decisions":decisions}


def run_representativeness_and_cross_corpus(candidate_path: Path, target_path: Path, design_path: Path, compatibility_path: Path, output_dir: Path) -> dict[str, Any]:
    candidates=read_tsv(candidate_path); design=read_tsv(design_path); compatibility=read_tsv(compatibility_path); target=yaml.safe_load(target_path.read_text(encoding="utf-8"))
    require_synthetic(candidates,"candidate manifest"); require_synthetic(design,"corpus design"); require_synthetic(compatibility,"compatibility table")
    if target.get("data_status") != STATUS: raise ValueError("Target population specification must remain explicitly synthetic")
    included=[row for row in candidates if as_bool(row["final_inclusion"])]
    support: list[dict[str,Any]]=[]; unsupported: list[dict[str,Any]]=[]; minimum=int(target["minimum_included_per_cell"])
    for dimension,categories in target["dimensions"].items():
        for category in categories:
            raw=sum(row.get(dimension)==category for row in candidates); final=sum(row.get(dimension)==category for row in included)
            status="adequate_fixture_support" if final>=minimum else ("restricted_fixture_support" if final>0 else "unsupported")
            support.append({"dimension":dimension,"category":category,"target_required":True,"raw_hits":raw,"final_inclusions":final,"minimum_required":minimum,"support_status":status,"data_status":STATUS})
            if status != "adequate_fixture_support": unsupported.append({"domain_type":"target_category","dimension":dimension,"domain_value":category,"reason":status,"data_status":STATUS})
    higher: list[dict[str,Any]]=[]
    for domain in ("speaker_id","conversation_id","item_id","corpus_id"):
        counts=Counter(row[domain] for row in included)
        for value,count in sorted(counts.items()): higher.append({"domain":domain,"domain_value":value,"included_tokens":count,"share_of_analysis":count/len(included) if included else 0,"data_status":STATUS})
    compatibility_rows=[]
    for row in compatibility:
        record=dict(row); record["comparison_permitted"] = row["compatibility"] == "compatible"; compatibility_rows.append(record)
        if row["compatibility"] != "compatible": unsupported.append({"domain_type":"cross_corpus","dimension":row["dimension"],"domain_value":row["compatibility"],"reason":row["overlap_rule"],"data_status":STATUS})
    gate={"data_status":STATUS,"decision":"restrict" if unsupported else "accept_fixture_only","supported_claim":"description of generated measurable tokens in observed north/south, casual/interview, 2010s/2020s cells","unsupported_claims":["central region","read speech","abstract corpus representativeness","causal corpus comparison","era or equipment effect"],"weighting_permitted":False,"reason":"target margins are illustrative rather than authorized population margins; incompatible era and recording domains remain","synthetic_fixture_is_population_evidence":False}
    output_dir.mkdir(parents=True,exist_ok=True)
    write_tsv(output_dir/"population_support.tsv",support,list(support[0])); write_tsv(output_dir/"higher_level_support.tsv",higher,list(higher[0])); write_tsv(output_dir/"compatibility_table.tsv",compatibility_rows,list(compatibility_rows[0])); write_tsv(output_dir/"unsupported_domains.tsv",unsupported,list(unsupported[0])); (output_dir/"corpus_inference_gate.yaml").write_text(yaml.safe_dump(gate,sort_keys=False),encoding="utf-8")
    report="<!doctype html><meta charset='utf-8'><title>Representativeness report</title><h1>Representativeness report</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Support is relative to generated target categories and cannot certify empirical representativeness.</p><h2>Population support</h2>"+html_table(support,list(support[0]))+"<h2>Cross-corpus compatibility</h2>"+html_table(compatibility_rows,list(compatibility_rows[0]))
    (output_dir/"representativeness_report.html").write_text(report,encoding="utf-8")
    provenance(output_dir/"run_provenance.json","phonetic_research_companion.ch15.run_representativeness_and_cross_corpus",[candidate_path,target_path,design_path,compatibility_path],gate)
    return {"support":support,"higher_level":higher,"compatibility":compatibility_rows,"unsupported":unsupported,"gate":gate}
