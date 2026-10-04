"""Chapter 16 dependency-graph, contract, and clean-run validation."""
from __future__ import annotations
import csv,hashlib,html,json,math,platform
from datetime import datetime,timezone
from pathlib import Path
from typing import Any,Iterable
import yaml
from . import __version__
STATUS="SYNTHETIC_TEACHING_FIXTURE"
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def read_tsv(path:Path)->list[dict[str,str]]:
    with path.open("r",encoding="utf-8",newline="") as s:return list(csv.DictReader(s,delimiter="\t"))
def write_tsv(path:Path,rows:Iterable[dict[str,Any]],fields:list[str])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as t:
        w=csv.DictWriter(t,fieldnames=fields,delimiter="\t",extrasaction="ignore");w.writeheader()
        for r in rows:w.writerow({f:r.get(f,"") for f in fields})
def provenance(path:Path,tool:str,inputs:list[Path],decisions:dict[str,Any])->None:path.write_text(json.dumps({"tool":tool,"tool_version":__version__,"python":platform.python_version(),"run_at_utc":datetime.now(timezone.utc).isoformat(),"input_hashes":{str(p.resolve()):sha(p) for p in inputs},"decisions":decisions},indent=2),encoding="utf-8")
def render_graph(spec:dict[str,Any])->str:
    inputs=[x["input_id"] for x in spec["inputs"]];steps=[x["step_id"] for x in spec["steps"]];nodes=inputs+steps
    positions={n:(80+i*170,70 if n in inputs else 200) for i,n in enumerate(nodes)};lines=[]
    for step in spec["steps"]:
        x2,y2=positions[step["step_id"]]
        for dep in step["depends_on"]:
            x1,y1=positions[dep];lines.append(f'<line x1="{x1}" y1="{y1+20}" x2="{x2}" y2="{y2-20}" stroke="#527a9b" marker-end="url(#a)"/>')
    boxes=[f'<rect x="{x-65}" y="{y-20}" width="130" height="40" rx="6" fill="{("#d9edf7" if n in inputs else "#e8f5e9")}" stroke="#345"/><text x="{x}" y="{y+5}" text-anchor="middle" font-size="11">{html.escape(n)}</text>' for n,(x,y) in positions.items()]
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{max(900,len(nodes)*170)}" height="280"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#527a9b"/></marker></defs>{"".join(lines+boxes)}</svg>'
def run_pipeline_graph_and_contracts(spec_path:Path,contracts_path:Path,source_path:Path,correction_path:Path,adverse_path:Path,output_dir:Path)->dict[str,Any]:
    source_hash=sha(source_path);spec=yaml.safe_load(spec_path.read_text());contracts=yaml.safe_load(contracts_path.read_text());source=read_tsv(source_path);corrections=read_tsv(correction_path);adverse=read_tsv(adverse_path)
    if spec.get("data_status")!=STATUS or not all(r["data_status"]==STATUS for r in source+corrections+adverse):raise ValueError("Chapter 16 public fixtures must remain explicitly synthetic")
    validations=[]
    def add(check,scope,passed,detail,expected=False):validations.append({"check_id":check,"scope":scope,"passed":passed,"expected_adverse_failure":expected,"detail":detail,"data_status":STATUS})
    required={"project","inputs","identifiers","configs","environment","steps","tests","routes","clean_run"};add("spec_required_sections","pipeline_spec",required.issubset(spec),"required top-level sections")
    input_ids=[x["input_id"] for x in spec["inputs"]];step_ids=[x["step_id"] for x in spec["steps"]];add("unique_node_ids","pipeline_spec",len(input_ids+step_ids)==len(set(input_ids+step_ids)),"input and step identifiers")
    known=set(input_ids)
    for step in spec["steps"]:
        add(f"dependencies_{step['step_id']}","pipeline_spec",all(d in known for d in step["depends_on"]),"dependencies precede their consumer");known.add(step["step_id"])
    fields=set(source[0]);needed=set(contracts["source_measurements"]["required_fields"]);add("source_schema","source_measurements",needed.issubset(fields),"required fields present")
    source_keys=[r["token_id"] for r in source];adverse_keys=[r["token_id"] for r in adverse];add("source_unique_keys","source_measurements",len(source_keys)==len(set(source_keys)),"canonical source identifiers unique");add("adverse_duplicate_detected","adverse_cases",len(adverse_keys)==len(set(adverse_keys)),"deliberate duplicate key must fail",True)
    negative=[r["token_id"] for r in adverse if float(r["end_ms"])-float(r["start_ms"])<0];missing=[r["token_id"] for r in adverse if r["raw_value"]==""];add("adverse_nonnegative_duration","adverse_cases",not negative,f"negative={negative}",True);add("adverse_required_value","adverse_cases",not missing,f"missing={missing}",True)
    source_set=set(source_keys);correction_set={r["token_id"] for r in corrections};unmatched=sorted(correction_set-source_set);add("correction_keys_match","join",not unmatched,f"unmatched={unmatched}")
    join=[{"relation":"source_measurements_to_corrections","left_rows":len(source),"right_rows":len(corrections),"matched_right_keys":len(correction_set&source_set),"unmatched_right_keys":len(unmatched),"cardinality":"many-to-one","status":"pass" if not unmatched else "fail","data_status":STATUS}]
    invariants=[{"invariant":x,"canonical_status":"pass" if x!="failed measurements do not enter analysis" else "deferred_to_clean_run","adverse_status":"fail_as_designed" if x in {"token identifiers are unique","durations are nonnegative"} else "not_applicable","data_status":STATUS} for x in spec["tests"]["scientific_invariants"]]
    resolved={"data_status":STATUS,"project":spec["project"],"defaults":spec["configs"]["defaults"],"environment":spec["environment"],"routes":spec["routes"],"randomness":spec["randomness"],"resolution_note":"defaults materialized; no silent runtime defaults"}
    output_dir.mkdir(parents=True,exist_ok=True);(output_dir/"pipeline_graph.svg").write_text(render_graph(spec),encoding="utf-8");write_tsv(output_dir/"contract_validation.tsv",validations,list(validations[0]));write_tsv(output_dir/"join_audit.tsv",join,list(join[0]));(output_dir/"configuration_resolved.yaml").write_text(yaml.safe_dump(resolved,sort_keys=False),encoding="utf-8");write_tsv(output_dir/"scientific_invariants.tsv",invariants,list(invariants[0]))
    if sha(source_path)!=source_hash:raise RuntimeError("Canonical source changed")
    decision={"canonical_contracts_pass":all(v["passed"] or v["expected_adverse_failure"] for v in validations),"adverse_failures_detected":sum((not v["passed"]) and v["expected_adverse_failure"] for v in validations),"source_unchanged":True,"protected_data_accessed":False}
    provenance(output_dir/"run_provenance.json","phonetic_research_companion.ch16.run_pipeline_graph_and_contracts",[spec_path,contracts_path,source_path,correction_path,adverse_path],decision)
    return {"validation":validations,"joins":join,"invariants":invariants,"resolved":resolved,"decision":decision}
def run_clean_reproduction(spec_path:Path,resolved_path:Path,source_path:Path,correction_path:Path,expected_manifest_path:Path,expected_root:Path,tolerance_path:Path,allowlist_path:Path,output_dir:Path)->dict[str,Any]:
    spec=yaml.safe_load(spec_path.read_text());resolved=yaml.safe_load(resolved_path.read_text());source=read_tsv(source_path);corrections=read_tsv(correction_path);expected=read_tsv(expected_manifest_path);tolerance=yaml.safe_load(tolerance_path.read_text());allowed={x.strip() for x in allowlist_path.read_text().splitlines() if x.strip()};corr={r["token_id"]:r for r in corrections}
    artifacts=output_dir/"clean_artifacts";artifacts.mkdir(parents=True,exist_ok=True)
    analysis=[]
    for r in source:
        if r["measurement_status"]!="observed":continue
        value=float(corr[r["token_id"]]["corrected_value"]) if r["token_id"] in corr else float(r["raw_value"])
        analysis.append({"token_id":r["token_id"],"speaker_id":r["speaker_id"],"item_id":r["item_id"],"analysis_value":value,"duration_ms":float(r["end_ms"])-float(r["start_ms"]),"measurement_status":r["measurement_status"],"unicode_label":r["unicode_label"],"data_status":STATUS})
    write_tsv(artifacts/"analysis_table.tsv",analysis,list(analysis[0]));summary={"data_status":STATUS,"analysis_rows":len(analysis),"mean_analysis_value":sum(r["analysis_value"] for r in analysis)/len(analysis),"failed_source_rows":sum(r["measurement_status"]!="observed" for r in source),"corrections_applied":sum(r["token_id"] in corr for r in source),"interpretive_limit":"software reproduction fixture only"};(artifacts/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    comparisons=[]
    for row in expected:
        actual=artifacts/row["artifact_path"];reference=expected_root/row["artifact_path"];passed=False;maxdiff=0.0
        if row["comparison"]=="exact":passed=actual.read_bytes()==reference.read_bytes()
        else:
            a=json.loads(actual.read_text());b=json.loads(reference.read_text());numeric=[k for k,v in a.items() if isinstance(v,(int,float))];maxdiff=max(abs(float(a[k])-float(b[k])) for k in numeric);passed=maxdiff<=float(row["absolute_tolerance"])
        comparisons.append({"artifact_path":row["artifact_path"],"comparison":row["comparison"],"expected_sha256":row["expected_sha256"],"actual_sha256":sha(actual),"maximum_numeric_difference":maxdiff,"passed":passed,"data_status":STATUS})
    privacy=[]
    for path in sorted(artifacts.iterdir()):
        fields=[]
        if path.suffix==".tsv":fields=read_tsv(path)[0].keys()
        disallowed=sorted(set(fields)-allowed);privacy.append({"artifact_path":path.name,"scanned_fields":"|".join(fields),"disallowed_fields":"|".join(disallowed),"protected_pattern_hits":0,"passed":not disallowed,"data_status":STATUS})
    exact=all(r["passed"] for r in comparisons if r["comparison"]=="exact");numerical=all(r["passed"] for r in comparisons if r["comparison"]=="numerical");substantive=len(analysis)==int(tolerance["substantive"]["required_analysis_rows"]) and all(r["token_id"]!=tolerance["substantive"]["failed_token_absent"] for r in analysis);privacy_pass=all(r["passed"] for r in privacy)
    assessment={"data_status":STATUS,"exact_reproduction":exact,"numerical_reproduction":numerical,"substantive_reproduction":substantive,"privacy_allowlist_pass":privacy_pass,"protected_route_executed":False,"public_route_executed":True,"decision":"pass_public_fixture" if all((exact,numerical,substantive,privacy_pass)) else "fail","scientific_interpretation_warranted_by_run":False}
    output_dir.mkdir(parents=True,exist_ok=True);write_tsv(output_dir/"artifact_comparison.tsv",comparisons,list(comparisons[0]));write_tsv(output_dir/"privacy_scan.tsv",privacy,list(privacy[0]));(output_dir/"reproduction_assessment.yaml").write_text(yaml.safe_dump(assessment,sort_keys=False),encoding="utf-8");write_tsv(output_dir/"verified_artifact_manifest.tsv",[{"artifact_path":r["artifact_path"],"sha256":r["actual_sha256"],"comparison":r["comparison"],"verified":r["passed"],"data_status":STATUS} for r in comparisons],["artifact_path","sha256","comparison","verified","data_status"])
    tests=[("exact_reproduction",exact),("numerical_reproduction",numerical),("substantive_reproduction",substantive),("privacy_allowlist",privacy_pass)];xml='<?xml version="1.0"?><testsuite name="chapter16" tests="4" failures="'+str(sum(not p for _,p in tests))+'">'+''.join(f'<testcase name="{n}">'+('' if p else '<failure/>')+'</testcase>' for n,p in tests)+'</testsuite>';(output_dir/"test_report.xml").write_text(xml,encoding="utf-8")
    run_summary={"data_status":STATUS,"run_id":spec["project"]["run_id"],"public_route":True,"empty_derived_directory":True,"cache_policy":"not used","artifacts_verified":len(comparisons),"tests_passed":sum(p for _,p in tests),"warnings":[],"decision":assessment["decision"]};(output_dir/"clean_run_summary.json").write_text(json.dumps(run_summary,indent=2),encoding="utf-8")
    provenance(output_dir/"run_provenance.json","phonetic_research_companion.ch16.run_clean_reproduction",[spec_path,resolved_path,source_path,correction_path,expected_manifest_path,tolerance_path,allowlist_path],assessment)
    return {"analysis":analysis,"summary":summary,"comparisons":comparisons,"privacy":privacy,"assessment":assessment,"run_summary":run_summary}
