"""Chapter 20 allowlist release building and authorization-aware verification."""
from __future__ import annotations
import csv,hashlib,json,re,shutil
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
import yaml
STATUS="SYNTHETIC_TEACHING_FIXTURE"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def read_tsv(p:Path)->list[dict[str,str]]:
 with p.open(encoding="utf-8",newline="") as s:return list(csv.DictReader(s,delimiter="\t"))
def write_tsv(p:Path,rows:list[dict[str,Any]],fields:list[str]):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("w",encoding="utf-8",newline="") as t:w=csv.DictWriter(t,fieldnames=fields,delimiter="\t",extrasaction="ignore");w.writeheader();w.writerows(rows)
def provenance(p:Path,tool:str,inputs:list[Path],decisions:dict[str,Any]):p.write_text(json.dumps({"tool":tool,"tool_version":"0.1.0","python_version":__import__('platform').python_version(),"run_at_utc":datetime.now(timezone.utc).isoformat(),"input_hashes":{str(x.resolve()):sha(x) for x in inputs},"decisions":decisions},indent=2)+"\n",encoding="utf-8")
def build_candidate(repository_root:Path,spec_path:Path,manifest_path:Path,license_path:Path,governance_path:Path,citation_path:Path,public_profile_path:Path,protected_profile_path:Path,output_dir:Path)->dict[str,Any]:
 spec=yaml.safe_load(spec_path.read_text());rows=read_tsv(manifest_path);licenses=read_tsv(license_path);governance=read_tsv(governance_path);citation=yaml.safe_load(citation_path.read_text());public=yaml.safe_load(public_profile_path.read_text());protected=yaml.safe_load(protected_profile_path.read_text())
 if spec["data_status"]!=STATUS or public["data_status"]!=STATUS:raise ValueError("Public Chapter 20 records must remain explicitly synthetic/candidate status")
 candidate=output_dir/"release_candidate";shutil.rmtree(candidate,ignore_errors=True);candidate.mkdir(parents=True)
 manifest=[];privacy=[];exclusions=[]
 patterns={"private_path":re.compile(r"/(Users|home|var/folders)/[^\s\"']+"),"email":re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),"secret":re.compile(r"(?i)(api[_-]?key|access[_-]?token|secret)\s*[:=]\s*[A-Za-z0-9_-]{12,}")}
 for row in rows:
  source=repository_root/row["path"]
  if not source.is_file():raise FileNotFoundError(source)
  if sha(source)!=row["sha256"]:raise ValueError(f"Allowlist hash mismatch: {row['path']}")
  target=candidate/row["path"];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
  text=target.read_text(encoding="utf-8",errors="replace");hits={name:len(pattern.findall(text)) for name,pattern in patterns.items()};unapproved=target.suffix.lower() in {".wav",".mp3",".flac",".mp4",".mov"};notebook_outputs=0
  if target.suffix==".ipynb":notebook_outputs=sum(bool(c.get("outputs")) for c in json.loads(text).get("cells",[]) if c.get("cell_type")=="code")
  passed=not any(hits.values()) and not unapproved and notebook_outputs==0
  privacy.append({"artifact_id":row["artifact_id"],**hits,"unapproved_media":unapproved,"notebook_cells_with_outputs":notebook_outputs,"passed":passed,"data_status":STATUS})
  manifest.append({**row,"candidate_path":row["path"],"size_bytes":target.stat().st_size,"verified_sha256":sha(target),"candidate_status":"internal_only"})
  if row["redistributable"].lower()!="true":exclusions.append({"artifact_id":row["artifact_id"],"public_release_status":"excluded_pending_authorization","reason":row["license_or_agreement"],"candidate_copy_retained_internal":True,"data_status":STATUS})
 license_audit=[{**r,"passed_for_public_release":r["decision"]=="pass_public_release"} for r in licenses];human=[{**r,"attributable_approval_present":r["record_status"] not in {"UNSIGNED_PLACEHOLDER","AUTOMATED_ONLY"},"passed_for_public_release":r["public_release_authorized"].lower()=="true" and r["record_status"] not in {"UNSIGNED_PLACEHOLDER","AUTOMATED_ONLY"}} for r in governance]
 output_dir.mkdir(parents=True,exist_ok=True);write_tsv(output_dir/"release_candidate_manifest.tsv",manifest,list(manifest[0]));(output_dir/"checksum_manifest.txt").write_text("".join(f"{r['verified_sha256']}  {r['candidate_path']}\n" for r in manifest),encoding="utf-8");write_tsv(output_dir/"license_audit.tsv",license_audit,list(license_audit[0]));write_tsv(output_dir/"privacy_scan.tsv",privacy,list(privacy[0]));write_tsv(output_dir/"human_review.tsv",human,list(human[0]));write_tsv(output_dir/"release_exclusions.tsv",exclusions,list(exclusions[0]))
 decisions={"allowlist_only":True,"files_copied":len(manifest),"privacy_scan_pass":all(r["passed"] for r in privacy),"license_public_release_pass":all(r["passed_for_public_release"] for r in license_audit),"human_public_release_approval":all(r["passed_for_public_release"] for r in human),"protected_route_accessed":False,"deposit_status":citation["deposit_status"],"public_release_authorized":spec["archive"]["publish_authorized"]}
 provenance(output_dir/"run_provenance.json","ch20.build_candidate",[spec_path,manifest_path,license_path,governance_path,citation_path,public_profile_path,protected_profile_path],decisions);return {"manifest":manifest,"privacy":privacy,"licenses":license_audit,"human":human,"exclusions":exclusions,"decisions":decisions,"candidate":candidate}
def clean_verify(repository_root:Path,spec_path:Path,manifest_path:Path,first_manifest_path:Path,availability_template:Path,maintenance_path:Path,citation_path:Path,output_dir:Path)->dict[str,Any]:
 spec=yaml.safe_load(spec_path.read_text());declared=read_tsv(manifest_path);first=read_tsv(first_manifest_path);citation=yaml.safe_load(citation_path.read_text());clean=output_dir/"clean_rebuild";shutil.rmtree(clean,ignore_errors=True);clean.mkdir(parents=True)
 verification=[]
 for row in declared:
  source=repository_root/row["path"];target=clean/row["path"];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);actual=sha(target);prior=next(x for x in first if x["artifact_id"]==row["artifact_id"]);verification.append({"artifact_id":row["artifact_id"],"declared_sha256":row["sha256"],"first_candidate_sha256":prior["verified_sha256"],"clean_rebuild_sha256":actual,"exact_match":actual==row["sha256"]==prior["verified_sha256"],"data_status":STATUS})
 availability=availability_template.read_text();(output_dir/"availability_statement.md").write_text(availability,encoding="utf-8");shutil.copy2(maintenance_path,output_dir/"maintenance_and_withdrawal.md")
 archive={"data_status":STATUS,"project_id":spec["release"]["project_id"],"version":spec["release"]["release_version"],"status":"CANDIDATE_NOT_DEPOSITED","provider":spec["archive"]["provider"],"version_specific_identifier":citation["version_specific_identifier"],"concept_identifier":citation["concept_identifier"],"deposit_authorized":False,"publish_authorized":False,"files":len(verification)};(output_dir/"archive_metadata.json").write_text(json.dumps(archive,indent=2)+"\n",encoding="utf-8")
 technical=all(r["exact_match"] for r in verification);gate={"data_status":STATUS,"decision":"postpone_deposit_pending_author_and_publisher","technical_clean_rebuild_pass":technical,"scientific_package_status":"first substantive draft; final copy-edit and production gates remain","privacy_scan_status":"passed automated candidate scan in notebook 1","license_authorization_pass":False,"human_governance_approval_pass":False,"deposit_authorized":False,"publish_authorized":False,"doi_registered":False,"protected_route_executed":False,"candidate_is_public_release":False,"required_actions":["author identity and authority review","publisher repository and license approval","final citation and style audit","authorized archive deposit and identifier creation"]};(output_dir/"reproducible_release_gate.yaml").write_text(yaml.safe_dump(gate,sort_keys=False),encoding="utf-8")
 run={"data_status":STATUS,"empty_clean_rebuild":True,"artifacts_verified":len(verification),"exact_matches":sum(r["exact_match"] for r in verification),"technical_pass":technical,"deposit_attempted":False,"publication_attempted":False};(output_dir/"public_clean_run.json").write_text(json.dumps(run,indent=2)+"\n",encoding="utf-8");write_tsv(output_dir/"artifact_verification.tsv",verification,list(verification[0]));provenance(output_dir/"run_provenance.json","ch20.clean_verify",[spec_path,manifest_path,first_manifest_path,availability_template,maintenance_path,citation_path],gate);return {"verification":verification,"archive":archive,"gate":gate,"run":run}
