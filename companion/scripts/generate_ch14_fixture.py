#!/usr/bin/env python3
"""Generate explicitly synthetic Chapter 14 error and sensitivity fixtures."""

from __future__ import annotations

import csv
import hashlib
import random
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "companion" / "data"
CHAPTER_ROOT = DATA_ROOT / "ch14" / "synthetic_error"
SEED = 14042026


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rng = random.Random(SEED)
    CHAPTER_ROOT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    validation: list[dict[str, object]] = []
    repeats: list[dict[str, object]] = []
    for speaker_index in range(1, 25):
        speaker = f"SYN_ERR_SPK_{speaker_index:02d}"
        group = "SYN_B" if speaker_index > 12 else "SYN_A"
        speaker_effect = rng.gauss(0, 4)
        reference_error = rng.gauss(0, 2.2)
        for item_index in range(1, 21):
            observation = f"SYN_ERR_{speaker_index:02d}_{item_index:02d}"
            predictor_true = rng.uniform(-1.5, 1.5)
            outcome_true = 100 + 7.5 * predictor_true + (5 if group == "SYN_B" else 0) + speaker_effect + rng.gauss(0, 4)
            predictor_primary = predictor_true + rng.gauss(0, 0.35)
            outcome_primary = outcome_true + reference_error + rng.gauss(0, 2.5) + (4 if group == "SYN_B" else 0)
            onset_ref = item_index * 1000 + 100
            offset_ref = onset_ref + 120 + 8 * predictor_true
            shared_shift = rng.gauss(8 if group == "SYN_B" else 2, 3)
            onset_auto = onset_ref + shared_shift + rng.gauss(0, 2)
            offset_auto = offset_ref + shared_shift + rng.gauss(0, 2)
            quality = rng.uniform(0, 1)
            available = not (quality < (0.18 if group == "SYN_B" else 0.08) or (outcome_true > 116 and rng.random() < 0.20))
            row = {"observation_id": observation, "speaker_id": speaker, "item_id": f"ITEM_{item_index:02d}", "group_id": group, "predictor_true": round(predictor_true, 6), "predictor_primary": round(predictor_primary, 6), "outcome_true": round(outcome_true, 6), "outcome_primary": round(outcome_primary, 6) if available else "", "onset_reference_ms": round(onset_ref, 6), "offset_reference_ms": round(offset_ref, 6), "onset_automatic_ms": round(onset_auto, 6), "offset_automatic_ms": round(offset_auto, 6), "quality_score": round(quality, 6), "availability_code": "observed" if available else "measurement_failure", "data_status": "SYNTHETIC_TEACHING_FIXTURE"}
            rows.append(row)
            if item_index <= 5:
                validation.append({"observation_id": observation, "speaker_id": speaker, "group_id": group, "reference_predictor": row["predictor_true"], "measured_predictor": row["predictor_primary"], "reference_outcome": row["outcome_true"], "measured_outcome": row["outcome_primary"], "reference_onset_ms": row["onset_reference_ms"], "measured_onset_ms": row["onset_automatic_ms"], "reference_offset_ms": row["offset_reference_ms"], "measured_offset_ms": row["offset_automatic_ms"], "validation_status": "paired" if available else "paired_measurement_missing", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
                for annotator in ("SYN_ANN_1", "SYN_ANN_2"):
                    repeats.append({"observation_id": observation, "speaker_id": speaker, "annotator_id": annotator, "onset_ms": round(onset_ref + shared_shift + rng.gauss(0, 3), 6), "offset_ms": round(offset_ref + shared_shift + rng.gauss(0, 3), 6), "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
    write_tsv(CHAPTER_ROOT / "raw_analysis_data.tsv", rows, list(rows[0]))
    write_tsv(CHAPTER_ROOT / "validation_pairs.tsv", validation, list(validation[0]))
    write_tsv(CHAPTER_ROOT / "repeated_measurements.tsv", repeats, list(repeats[0]))
    error_map = [
        {"error_id": "E_OUTCOME_RANDOM", "stage": "extraction", "affected_variable": "outcome_primary", "error_type": "random", "dependency_level": "observation", "direction": "mean_zero", "validation_source": "validation_pairs", "plausible_range": "paired SD", "data_status": "SYNTHETIC_TEACHING_FIXTURE"},
        {"error_id": "E_PREDICTOR_RANDOM", "stage": "extraction", "affected_variable": "predictor_primary", "error_type": "random", "dependency_level": "observation", "direction": "attenuation risk", "validation_source": "validation_pairs", "plausible_range": "paired SD", "data_status": "SYNTHETIC_TEACHING_FIXTURE"},
        {"error_id": "E_LANDMARK_SHARED", "stage": "annotation", "affected_variable": "onset+offset", "error_type": "correlated", "dependency_level": "observation", "direction": "alignment shift with limited duration change", "validation_source": "repeated_measurements", "plausible_range": "paired landmark differences", "data_status": "SYNTHETIC_TEACHING_FIXTURE"},
        {"error_id": "E_REFERENCE_SHARED", "stage": "normalization", "affected_variable": "outcome_primary", "error_type": "correlated", "dependency_level": "speaker", "direction": "shared shift", "validation_source": "generator-known teaching range", "plausible_range": "SD 2.2", "data_status": "SYNTHETIC_TEACHING_FIXTURE"},
        {"error_id": "E_DIFFERENTIAL", "stage": "extraction", "affected_variable": "outcome_primary", "error_type": "differential", "dependency_level": "group", "direction": "+4 in SYN_B", "validation_source": "generator-known teaching range", "plausible_range": "0 to 4", "data_status": "SYNTHETIC_TEACHING_FIXTURE"},
        {"error_id": "E_MISSINGNESS", "stage": "missingness", "affected_variable": "outcome_primary", "error_type": "differential", "dependency_level": "group+outcome", "direction": "greater loss in SYN_B and high outcomes", "validation_source": "availability code", "plausible_range": "observed fixture", "data_status": "SYNTHETIC_TEACHING_FIXTURE"},
    ]
    write_tsv(CHAPTER_ROOT / "error_map.tsv", error_map, list(error_map[0]))
    specifications = [
        {"configuration_id": "primary", "priority": "primary", "measurement_layer": "primary", "eligibility_rule": "observed", "model": "additive", "changes_estimand": "false", "exploratory": "false"},
        {"configuration_id": "reference_layer", "priority": "high", "measurement_layer": "reference", "eligibility_rule": "all", "model": "additive", "changes_estimand": "false", "exploratory": "false"},
        {"configuration_id": "differential_corrected", "priority": "high", "measurement_layer": "bias_corrected", "eligibility_rule": "observed", "model": "additive", "changes_estimand": "false", "exploratory": "false"},
        {"configuration_id": "quality_050", "priority": "high", "measurement_layer": "primary", "eligibility_rule": "quality_ge_050", "model": "additive", "changes_estimand": "false", "exploratory": "false"},
        {"configuration_id": "quality_075", "priority": "secondary", "measurement_layer": "primary", "eligibility_rule": "quality_ge_075", "model": "additive", "changes_estimand": "false", "exploratory": "false"},
        {"configuration_id": "interaction", "priority": "high", "measurement_layer": "primary", "eligibility_rule": "observed", "model": "interaction", "changes_estimand": "true", "exploratory": "false"},
        {"configuration_id": "invalid_combo", "priority": "high", "measurement_layer": "unknown", "eligibility_rule": "all", "model": "additive", "changes_estimand": "false", "exploratory": "false"},
        {"configuration_id": "post_result_branch", "priority": "exploratory", "measurement_layer": "reference", "eligibility_rule": "quality_ge_075", "model": "interaction", "changes_estimand": "true", "exploratory": "true"},
    ]
    write_tsv(CHAPTER_ROOT / "specification_table.tsv", specifications, list(specifications[0]))
    spec = {"schema_version": "0.1", "data_status": "SYNTHETIC_TEACHING_FIXTURE", "seed": SEED, "claim": {"claim_id": "SYN_CLAIM", "text": "predictor has a positive association with the outcome in the generated sample", "estimand": "additive predictor slope", "target_population": "24 synthetic speakers and 20 generated items"}, "primary_analysis": {"configuration_id": "primary", "measurement_layer": "primary", "eligibility_rule": "observed", "model": "outcome ~ predictor + group", "uncertainty_method": "ordinary model SE for instruction only"}, "propagation": {"replicates": 40, "preserve_dependency_levels": ["observation", "speaker", "group"]}, "stability": {"direction_rule": "positive in every successful high-priority same-estimand configuration", "magnitude_region": [5.0, 10.0], "scope_rule": "both synthetic groups and at least 18 speakers retained", "diagnostic_rule": "finite estimate and SE; failed specifications retained", "permitted_outcomes": ["stable", "stable_with_restricted_scope", "measurement_dependent", "analysis_dependent", "unsupported"]}, "execution": {"primary_runs_first": True, "retain_failures": True, "post_result_branches_label": "exploratory"}}
    (CHAPTER_ROOT / "sensitivity_analysis_spec.yaml").write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    files = sorted(path for path in CHAPTER_ROOT.iterdir() if path.is_file())
    chapter_rows = [{"artifact_id": f"CH14_SYN_{index+1:02d}", "relative_path": str(path.relative_to(DATA_ROOT)), "data_status": "SYNTHETIC_TEACHING_FIXTURE", "source": "generated locally by companion/scripts/generate_ch14_fixture.py", "license": "CC-BY-4.0", "sha256": sha256_file(path), "contains_human_data": "false"} for index, path in enumerate(files)]
    manifest = DATA_ROOT / "MANIFEST.tsv"
    preserved: list[dict[str, str]] = []
    if manifest.exists():
        with manifest.open("r", encoding="utf-8", newline="") as source:
            preserved = [row for row in csv.DictReader(source, delimiter="\t") if not row["artifact_id"].startswith("CH14_")]
    write_tsv(manifest, sorted(preserved + chapter_rows, key=lambda row: row["artifact_id"]), ["artifact_id", "relative_path", "data_status", "source", "license", "sha256", "contains_human_data"])


if __name__ == "__main__": main()
