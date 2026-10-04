#!/usr/bin/env python3
"""Generate explicitly synthetic Chapter 16 pipeline fixtures."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]; DATA_ROOT=ROOT/"companion"/"data"; CHAPTER_ROOT=DATA_ROOT/"ch16"/"synthetic_pipeline"
def write_tsv(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as target:
        w=csv.DictWriter(target,fieldnames=fields,delimiter="\t",extrasaction="ignore");w.writeheader();w.writerows(rows)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    CHAPTER_ROOT.mkdir(parents=True,exist_ok=True)
    source=[]
    for i in range(1,13):
        source.append({"token_id":f"SYN_PIPE_{i:03d}","speaker_id":f"SYN_PSPK_{(i-1)//3+1:02d}","item_id":f"ITEM_{i:02d}","raw_value":round(100+i*1.5,4),"start_ms":i*100,"end_ms":i*100+80+i,"measurement_status":"failed" if i==9 else "observed","unicode_label":"母音" if i==4 else "vowel","data_status":"SYNTHETIC_TEACHING_FIXTURE"})
    write_tsv(CHAPTER_ROOT/"source_measurements.tsv",source,list(source[0]))
    corrections=[{"token_id":"SYN_PIPE_003","corrected_value":111.25,"reason_code":"synthetic_review","reviewer_code":"SYN_REVIEWER","data_status":"SYNTHETIC_TEACHING_FIXTURE"}]
    write_tsv(CHAPTER_ROOT/"correction_table.tsv",corrections,list(corrections[0]))
    adverse=[dict(source[0]),dict(source[4]),dict(source[4]),dict(source[5]),dict(source[8])]
    adverse[0]["token_id"]="SYN_ADVERSE_NEG";adverse[0]["start_ms"]=200;adverse[0]["end_ms"]=150
    adverse[1]["token_id"]="SYN_ADVERSE_DUP";adverse[2]["token_id"]="SYN_ADVERSE_DUP"
    adverse[3]["token_id"]="SYN_ADVERSE_MISSING";adverse[3]["raw_value"]=""
    adverse[4]["token_id"]="SYN_ADVERSE_FAILURE"
    write_tsv(CHAPTER_ROOT/"adverse_cases.tsv",adverse,list(adverse[0]))
    schema={"schema_version":"0.1","data_status":"SYNTHETIC_TEACHING_FIXTURE","source_measurements":{"required_fields":["token_id","speaker_id","item_id","raw_value","start_ms","end_ms","measurement_status","unicode_label","data_status"],"primary_key":["token_id"],"types":{"raw_value":"number_or_missing","start_ms":"number","end_ms":"number"}},"correction_table":{"required_fields":["token_id","corrected_value","reason_code","reviewer_code","data_status"],"primary_key":["token_id"],"join":"many-to-one source to correction","unmatched_policy":"fail"}}
    (CHAPTER_ROOT/"data_contracts.yaml").write_text(yaml.safe_dump(schema,sort_keys=False),encoding="utf-8")
    spec={"schema_version":"1.0","data_status":"SYNTHETIC_TEACHING_FIXTURE","project":{"project_id":"SYN_PIPELINE","title":"Synthetic phonetic pipeline teaching fixture","code_revision":"fixture-generator-v0.1","run_id":"SYN_RUN_CLEAN_001"},"inputs":[{"input_id":"source_measurements","manifest":"source_measurements.tsv","immutable":True,"access_profile":"public","expected_hash_algorithm":"sha256"},{"input_id":"correction_table","manifest":"correction_table.tsv","immutable":True,"access_profile":"public","expected_hash_algorithm":"sha256"}],"identifiers":{"observation_key":["token_id"],"declared_relations":[{"left":"source_measurements.token_id","right":"correction_table.token_id","cardinality":"many-to-one","unmatched_policy":"correction keys must match source"}]},"configs":{"schemas":"data_contracts.yaml","reject_unknown_fields":True,"materialize_resolved_defaults":True,"defaults":{"failed_measurement_policy":"retain_reason_then_exclude_from_analysis","correction_policy":"new_derived_layer"}},"environment":{"primary_language":"python","lockfile":"companion/requirements-python.txt","locale":"C.UTF-8","timezone":"UTC"},"steps":[{"step_id":"validate","depends_on":["source_measurements","correction_table"],"outputs":["contract_validation.tsv","join_audit.tsv"]},{"step_id":"derive","depends_on":["validate"],"outputs":["analysis_table.tsv"]},{"step_id":"summarize","depends_on":["derive"],"outputs":["summary.json"]},{"step_id":"assess","depends_on":["summarize"],"outputs":["reproduction_assessment.yaml"]}],"tests":{"scientific_invariants":["token identifiers are unique","durations are nonnegative","correction keys match source keys","failed measurements do not enter analysis","raw values remain immutable"]},"routes":{"protected":{"profile":"protected_profile.yaml","publishable":False},"public":{"profile":"public_profile.yaml","publishable":True},"shared_code_required":True},"clean_run":{"empty_derived_directory":True,"disable_or_verify_caches":True,"clean_notebook_kernel":True,"verify_expected_artifacts":True,"privacy_allowlist":"public_allowlist.txt"},"randomness":{"master_seed":16042026,"stream_policy":"one deterministic public fixture"}}
    (CHAPTER_ROOT/"pipeline_spec.yaml").write_text(yaml.safe_dump(spec,sort_keys=False),encoding="utf-8")
    for name,payload in {"public_profile.yaml":{"data_status":"SYNTHETIC_TEACHING_FIXTURE","route":"public","input_root":"bundled synthetic fixture","publishable":True,"contains_protected_data":False},"protected_profile.yaml":{"data_status":"CONFIGURATION_ONLY_NO_DATA","route":"protected","input_root":"[AUTHORIZED LOCAL PATH REQUIRED]","publishable":False,"contains_protected_data":True},"tolerance_policy.yaml":{"data_status":"SYNTHETIC_TEACHING_FIXTURE","exact":["analysis_table.tsv"],"numerical":{"summary.json":{"absolute_tolerance":1e-9,"relative_tolerance":1e-9}},"substantive":{"required_analysis_rows":11,"failed_token_absent":"SYN_PIPE_009"}}}.items(): (CHAPTER_ROOT/name).write_text(yaml.safe_dump(payload,sort_keys=False),encoding="utf-8")
    (CHAPTER_ROOT/"public_allowlist.txt").write_text("token_id\nspeaker_id\nitem_id\nanalysis_value\nduration_ms\nmeasurement_status\nunicode_label\ndata_status\n",encoding="utf-8")
    expected_dir=CHAPTER_ROOT/"expected";expected_dir.mkdir(exist_ok=True)
    analysis=[]
    corr={r["token_id"]:r for r in corrections}
    for row in source:
        if row["measurement_status"]!="observed": continue
        value=float(corr[row["token_id"]]["corrected_value"]) if row["token_id"] in corr else float(row["raw_value"])
        analysis.append({"token_id":row["token_id"],"speaker_id":row["speaker_id"],"item_id":row["item_id"],"analysis_value":value,"duration_ms":float(row["end_ms"])-float(row["start_ms"]),"measurement_status":row["measurement_status"],"unicode_label":row["unicode_label"],"data_status":"SYNTHETIC_TEACHING_FIXTURE"})
    write_tsv(expected_dir/"analysis_table.tsv",analysis,list(analysis[0]))
    summary={"data_status":"SYNTHETIC_TEACHING_FIXTURE","analysis_rows":len(analysis),"mean_analysis_value":sum(float(r["analysis_value"]) for r in analysis)/len(analysis),"failed_source_rows":1,"corrections_applied":1,"interpretive_limit":"software reproduction fixture only"}
    (expected_dir/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    expected=[{"artifact_path":"analysis_table.tsv","comparison":"exact","expected_sha256":sha(expected_dir/"analysis_table.tsv"),"absolute_tolerance":0,"relative_tolerance":0,"data_status":"SYNTHETIC_TEACHING_FIXTURE"},{"artifact_path":"summary.json","comparison":"numerical","expected_sha256":sha(expected_dir/"summary.json"),"absolute_tolerance":1e-9,"relative_tolerance":1e-9,"data_status":"SYNTHETIC_TEACHING_FIXTURE"}]
    write_tsv(CHAPTER_ROOT/"expected_artifacts.tsv",expected,list(expected[0]))
    files=sorted(p for p in CHAPTER_ROOT.rglob("*") if p.is_file()); rows=[{"artifact_id":f"CH16_SYN_{i+1:02d}","relative_path":str(p.relative_to(DATA_ROOT)),"data_status":"SYNTHETIC_TEACHING_FIXTURE" if p.name!="protected_profile.yaml" else "CONFIGURATION_ONLY_NO_DATA","source":"generated locally by companion/scripts/generate_ch16_fixture.py","license":"CC-BY-4.0","sha256":sha(p),"contains_human_data":"false"} for i,p in enumerate(files)]
    manifest=DATA_ROOT/"MANIFEST.tsv";preserved=[]
    if manifest.exists():
        with manifest.open("r",encoding="utf-8",newline="") as s:preserved=[r for r in csv.DictReader(s,delimiter="\t") if not r["artifact_id"].startswith("CH16_")]
    write_tsv(manifest,sorted(preserved+rows,key=lambda r:r["artifact_id"]),["artifact_id","relative_path","data_status","source","license","sha256","contains_human_data"])
if __name__=="__main__":main()
