#!/usr/bin/env python3
"""Generate explicitly synthetic Chapter 18 complex-model fixtures."""
from __future__ import annotations
import csv, hashlib, math, random
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[2]; DATA_ROOT=ROOT/"companion"/"data"; CHAPTER_ROOT=DATA_ROOT/"ch18"/"synthetic_complex"; STATUS="SYNTHETIC_TEACHING_FIXTURE"; SEED=18042026
def write_tsv(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as target:
        writer=csv.DictWriter(target,fieldnames=fields,delimiter="\t",extrasaction="ignore");writer.writeheader();writer.writerows(rows)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    rng=random.Random(SEED);CHAPTER_ROOT.mkdir(parents=True,exist_ok=True)
    speakers=[f"SYN_CPX_SPK_{i:02d}" for i in range(1,31)];items=[f"SYN_CPX_ITEM_{i:02d}" for i in range(1,13)];times=[i/20 for i in range(21)]
    spk_effect={s:rng.gauss(0,1.8) for s in speakers};item_effect={x:rng.gauss(0,0.9) for x in items}
    frames=[];boundaries=[];token_index=0
    reason_cycle=["observed"]*90+["technical_loss","algorithmic_failure","quality_rejection","censored","structural_absence"]
    for s_i,speaker in enumerate(speakers):
      condition="B" if s_i%2 else "A"
      for item in items:
        token_index+=1;token=f"SYN_TRAJ_{token_index:04d}";duration=420+rng.uniform(-55,55)
        boundaries.append({"token_id":token,"speaker_id":speaker,"item_id":item,"condition":condition,"start_ms":0,"end_ms":f"{duration:.5f}","frames_expected":21,"data_status":STATUS})
        ar=0.0
        for frame_index,t in enumerate(times):
          ar=.62*ar+rng.gauss(0,0.65);shape=5.5*math.sin(math.pi*t)+(3.4*math.sin(2*math.pi*t) if condition=="B" else 0)
          true=80+spk_effect[speaker]+item_effect[item]+shape+ar
          reason=rng.choice(reason_cycle)
          # Structural absence is limited to edge frames, where the event is not defined.
          if reason=="structural_absence" and frame_index not in {0,20}:reason="observed"
          observed=reason=="observed";measured=true+rng.gauss(0,0.8) if observed else ""
          frames.append({"frame_id":f"{token}_F{frame_index:02d}","token_id":token,"speaker_id":speaker,"item_id":item,"condition":condition,"frame_index":frame_index,"time_ms":f"{t*duration:.5f}","time_normalized":f"{t:.5f}","series_start":str(frame_index==0).lower(),"true_value":f"{true:.6f}","measured_value":f"{measured:.6f}" if observed else "","availability_code":reason,"data_status":STATUS})
    write_tsv(CHAPTER_ROOT/"trajectory_frames.tsv",frames,list(frames[0]));write_tsv(CHAPTER_ROOT/"series_boundaries.tsv",boundaries,list(boundaries[0]))
    codes=[{"availability_code":c,"observation_process":p,"imputation_permitted":imp,"interpretation":text,"data_status":STATUS} for c,p,imp,text in [
      ("observed","observed","false","measured value available"),("structural_absence","event_not_defined","false","phonetic event is absent"),("participant_nonresponse","nonresponse","conditional","requires a declared participation model"),("technical_loss","recording_process","conditional","requires multilevel technical-loss model"),("algorithmic_failure","estimation_process","conditional","requires multilevel estimator model"),("quality_rejection","selection_process","conditional","requires reason and sensitivity analysis"),("metadata_missing","design_information","false","design variable cannot be silently imputed"),("censored","thresholded_observation","false","retain bound and use censoring model")]]
    write_tsv(CHAPTER_ROOT/"missingness_codes.tsv",codes,list(codes[0]))
    validation=[]
    for i in range(1,121):
      ref=78+rng.gauss(0,6);error=rng.gauss(0,0.8)
      validation.append({"validation_id":f"SYN_VAL_{i:03d}","reference_value":f"{ref:.6f}","measured_value":f"{ref+error:.6f}","error_source":"paired synthetic reference","evidence_status":"validation_derived_fixture","data_status":STATUS})
    write_tsv(CHAPTER_ROOT/"measurement_validation.tsv",validation,list(validation[0]))
    error=[{"scenario_id":"validation_random","mechanism":"independent Gaussian outcome error","range_or_scale":"estimated SD from measurement_validation.tsv","evidence_status":"validation_derived_fixture","replicates":30,"seed":SEED,"data_status":STATUS},{"scenario_id":"hypothetical_differential","mechanism":"condition-B additive bias","range_or_scale":"uniform 0 to 2 outcome units","evidence_status":"HYPOTHETICAL_SENSITIVITY_ONLY","replicates":30,"seed":SEED+1,"data_status":STATUS}]
    write_tsv(CHAPTER_ROOT/"error_scenarios.tsv",error,list(error[0]))
    spec={"schema_version":"1.0","data_status":STATUS,"seed":SEED,"model_purpose":{"primary_goal":"description and association","scientific_quantity":"condition difference over normalized trajectory time","simple_benchmark":"midpoint condition contrast","justification_for_complexity":"condition B has a generated nonlinear shape difference and within-token dependence"},"dynamic_structure":{"enabled":True,"series_id":"token_id","raw_time":"time_ms","analysis_time":"time_normalized","population_functions":["condition-specific smooth"],"unit_functions":["speaker random effect","item random effect"],"basis_dimension":7,"residual_dependence":"diagnosed from within-token lag-one residual correlation","series_start_indicator":"series_start"},"measurement_error":{"enabled":True,"evidence_source":"measurement_validation.tsv","hypothetical_ranges_are_sensitivity_only":True},"missingness":{"reason_codes":[x["availability_code"] for x in codes],"target_estimand_under_observation_process":"measurable trajectory frames under declared criteria","imputation":{"enabled":False,"prohibit_structural_absence_imputation":True,"seed":SEED}},"diagnostics":{"autocorrelation":True,"observed_support":True},"interpretive_limit":"generated workflow test only"}
    (CHAPTER_ROOT/"complex_model_spec.yaml").write_text(yaml.safe_dump(spec,sort_keys=False),encoding="utf-8")
    # Token-level prediction table. A speaker signature makes row-random validation deceptively favorable.
    features=[];obs=0
    speaker_signature={s:rng.gauss(0,1) for s in speakers}
    for s_i,speaker in enumerate(speakers):
      corpus="SYN_CORPUS_A" if s_i<20 else "SYN_CORPUS_B";speaker_bias=rng.gauss(0,0.75)
      for item_i,item in enumerate(items):
       for session in ["S1","S2"]:
        obs+=1;label=1 if (item_i+s_i+(session=="S2"))%2 else 0
        cue1=0.72*label+speaker_bias+rng.gauss(0,1);cue2=0.48*label+0.35*speaker_signature[speaker]+rng.gauss(0,1);device=0.8 if corpus=="SYN_CORPUS_B" else 0
        features.append({"observation_id":f"SYN_PRED_{obs:04d}","speaker_id":speaker,"item_id":item,"session_id":session,"corpus_id":corpus,"outcome":label,"cue_1":f"{cue1:.6f}","cue_2":f"{cue2:.6f}","speaker_signature":f"{speaker_signature[speaker]:.6f}","device_signature":f"{device+rng.gauss(0,.08):.6f}","data_status":STATUS})
    write_tsv(CHAPTER_ROOT/"prediction_features.tsv",features,list(features[0]))
    candidates=[{"model_id":"cue_only","formula":"outcome ~ cue_1 + cue_2","purpose":"prediction","prespecified":"true","data_status":STATUS},{"model_id":"expanded_signatures","formula":"outcome ~ cue_1 + cue_2 + speaker_signature + device_signature","purpose":"prediction","prespecified":"true","data_status":STATUS}]
    write_tsv(CHAPTER_ROOT/"candidate_models.tsv",candidates,list(candidates[0]))
    policies={"schema_version":"1.0","data_status":STATUS,"seed":SEED,"schemes":{"row_random":{"folds":5,"target":"new rows from represented units"},"speaker_heldout":{"folds":5,"target":"new speakers"},"item_heldout":{"folds":4,"target":"new items"},"session_heldout":{"folds":2,"target":"new sessions"},"corpus_heldout":{"folds":2,"target":"new corpora"}},"preprocessing_inside_folds":True,"tuning":"none; bounded candidate set"}
    (CHAPTER_ROOT/"fold_policy.yaml").write_text(yaml.safe_dump(policies,sort_keys=False),encoding="utf-8")
    for name,payload in {
      "deployment_domain.yaml":{"data_status":STATUS,"intended_primary_deployment":"new speakers from represented corpora, items, sessions, and measurement process","unsupported":"new corpus or recording chain without external validation"},
      "preprocessing_recipe.yaml":{"data_status":STATUS,"steps":["training-fold mean centering","training-fold standard deviation scaling"],"feature_selection":"none","imputation":"none; fixture is complete","test_information_permitted":False},
      "outcome_schema.yaml":{"data_status":STATUS,"outcome":"binary synthetic category","levels":[0,1],"positive_class":1,"metrics":["accuracy","Brier score","calibration intercept","calibration slope"]},
      "claim_map.yaml":{"data_status":STATUS,"population":"new speakers are primary; new items, sessions, and corpora are sensitivity domains","measurement":"synthetic generated cues only","predictor":"observed training-fold ranges","goal":"prediction, not causal or mechanistic explanation"}
    }.items():(CHAPTER_ROOT/name).write_text(yaml.safe_dump(payload,sort_keys=False),encoding="utf-8")
    files=sorted(p for p in CHAPTER_ROOT.iterdir() if p.is_file());generated=[{"artifact_id":f"CH18_SYN_{i+1:02d}","relative_path":str(p.relative_to(DATA_ROOT)),"data_status":STATUS,"source":"generated locally by companion/scripts/generate_ch18_fixture.py","license":"CC-BY-4.0","sha256":sha(p),"contains_human_data":"false"} for i,p in enumerate(files)]
    manifest=DATA_ROOT/"MANIFEST.tsv";preserved=[]
    if manifest.exists():
      with manifest.open(encoding="utf-8",newline="") as source:preserved=[r for r in csv.DictReader(source,delimiter="\t") if not r["artifact_id"].startswith("CH18_")]
    write_tsv(manifest,sorted(preserved+generated,key=lambda r:r["artifact_id"]),["artifact_id","relative_path","data_status","source","license","sha256","contains_human_data"])
if __name__=="__main__":main()
