#!/usr/bin/env python3
"""Generate explicitly synthetic Chapter 12 trajectory and rhythm fixtures."""

from __future__ import annotations

import csv
import hashlib
import math
import random
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "companion" / "data"
CHAPTER_ROOT = DATA_ROOT / "ch12" / "synthetic_prosody"
SEED = 12042026


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rng = random.Random(SEED)
    CHAPTER_ROOT.mkdir(parents=True, exist_ok=True)
    sources: list[dict[str, object]] = []
    intervals: list[dict[str, object]] = []
    landmarks: list[dict[str, object]] = []
    frames: list[dict[str, object]] = []
    token_index = 0
    for speaker_index in range(1, 13):
        speaker = f"SYN_PROS_SPK_{speaker_index:02d}"
        speaker_shift = rng.gauss(0, 9)
        for item_index in range(1, 9):
            token_index += 1
            token = f"SYN_TRAJ_{token_index:03d}"
            item = f"SYN_ITEM_{item_index:02d}"
            condition = "SYN_LONG" if item_index % 2 == 0 else "SYN_SHORT"
            duration_ms = rng.randint(420, 520) if condition == "SYN_LONG" else rng.randint(260, 340)
            start_s = token_index * 2.0
            end_s = start_s + duration_ms / 1000
            landmark_s = start_s + 0.120
            source_status = "source_failure" if token_index == 96 else "available"
            sources.append({"source_id": f"SOURCE_{token}", "token_id": token, "speaker_id": speaker, "item_id": item, "condition_id": condition, "source_status": source_status, "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
            intervals.append({"token_id": token, "source_id": f"SOURCE_{token}", "interval_start_s": round(start_s, 6), "interval_end_s": round(end_s, 6), "duration_ms": duration_ms, "included_label": "synthetic_phrase", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
            landmarks.append({"token_id": token, "landmark_id": "fixed_delay_event", "landmark_time_s": round(landmark_s, 6), "landmark_definition": "120 ms after interval onset by generator", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
            ar_noise = 0.0
            frame_count = duration_ms // 10 + 1
            for frame_index in range(frame_count):
                relative_ms = frame_index * 10
                absolute_s = start_s + relative_ms / 1000
                proportion = relative_ms / duration_ms
                peak_center = 0.42 if condition == "SYN_LONG" else 0.58
                contour = 24 * math.exp(-0.5 * ((proportion - peak_center) / 0.16) ** 2) - 8 * proportion
                ar_noise = 0.65 * ar_noise + rng.gauss(0, 2.2)
                candidate = 125 + speaker_shift + contour + ar_noise + (item_index - 4.5) * 0.7
                status = "observed"
                selected: object = round(candidate, 4)
                if source_status == "source_failure":
                    status, selected = "source_failure", ""
                elif token_index % 5 == 0 and (relative_ms < 30 or duration_ms - relative_ms < 25):
                    status, selected = "structural_unvoiced", ""
                elif (token_index * 17 + frame_index * 13) % 101 == 0:
                    status, selected = "estimator_failure", ""
                elif (token_index * 19 + frame_index * 7) % 137 == 0:
                    status, selected = "quality_rejection", ""
                frames.append({"token_id": token, "frame_index": frame_index, "frame_time_s": round(absolute_s, 6), "raw_candidate_f0_hz": "" if status in ("structural_unvoiced", "source_failure") else round(candidate, 4), "selected_f0_hz": selected, "frame_status": status, "quality_score": round(rng.uniform(0.25, 0.99), 4) if selected != "" else "", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
    write_tsv(CHAPTER_ROOT / "source_manifest.tsv", sources, list(sources[0]))
    write_tsv(CHAPTER_ROOT / "interval_manifest.tsv", intervals, list(intervals[0]))
    write_tsv(CHAPTER_ROOT / "landmarks.tsv", landmarks, list(landmarks[0]))
    write_tsv(CHAPTER_ROOT / "raw_frame_estimates.tsv", frames, list(frames[0]))

    trajectory_spec = {
        "schema_version": "0.1",
        "data_status": "SYNTHETIC_TEACHING_FIXTURE",
        "trajectory": {"trajectory_id": "SYN_F0_CONTOUR", "construct": "instructional phrase-level F0 contour", "acoustic_measure": "selected_f0_hz", "raw_unit": "Hz", "analysis_unit": "semitones_relative_to_training_speaker_median"},
        "domain": {"annotation_tier": "synthetic_phrase", "included_labels": ["synthetic_phrase"], "start_landmark": "interval_start_s", "end_landmark": "interval_end_s", "alignment_landmark": "fixed_delay_event"},
        "frame_grid": {"source_step_ms": 10, "requested_grid_rule": "every 10 ms from inclusive onset while <= interval end", "retain_absolute_time": True, "retain_landmark_relative_time": True, "retain_proportional_time": True},
        "estimation": {"software": "synthetic generator", "software_version": "0.1", "algorithm": "generated AR(1)-noise contour", "settings_profile_id": "SYN_PROFILE", "settings": {"seed": SEED}},
        "missingness": {"required_codes": ["structural_unvoiced", "estimator_failure", "quality_rejection", "source_failure"], "preserve_requested_frames": True},
        "preprocessing": {"correction_policy": "none", "interpolation_permitted": True, "interpolation_max_gap_ms": 20, "interpolation_eligible_codes": ["estimator_failure"], "smoothing_method": "model-based only", "smoothing_parameters": {}},
        "scaling": {"transformation": "12*log2(f0/speaker_observed_median)", "reference_sample_id": "all observed synthetic frames by speaker", "reference_definition": "observed, non-rejected frames only", "reference_unit": "speaker", "interpretive_limit": "not a biological normalization claim"},
        "time_representation": {"primary": "proportional", "sensitivity_representations": ["real", "landmark_relative"], "resampling_method": "none in preparation; model uses observed grid", "target_grid": "0 to 1 by .02 for predictions"},
        "dependence": {"speaker_id": "speaker_id", "item_id": "item_id", "token_id": "token_id", "series_start_variable": "series_start", "frame_order_variable": "frame_index", "residual_structure": "AR1 rho=0.6 prespecified for teaching comparison"},
        "quality_control": {"track_flags": ["reason-coded gap", "interpolated value"], "risk_strata": ["condition_id", "duration"], "review_sample_rule": "all non-observed frames", "contribution_count_required": True},
        "gate": {"coverage_rule": "report contribution counts at every prediction point", "stability_rule": "condition contrast direction must agree across time representations", "permitted_decisions": ["accept", "restrict", "amend_and_rerun", "reject"]},
        "provenance": {"source_hash_required": True, "retain_raw_frames": True, "overwrite_permitted": False},
    }
    (CHAPTER_ROOT / "prosodic_trajectory_spec.yaml").write_text(yaml.safe_dump(trajectory_spec, sort_keys=False), encoding="utf-8")

    segmented: list[dict[str, object]] = []
    for speaker_index in range(1, 13):
        speaker = f"SYN_PROS_SPK_{speaker_index:02d}"
        group = "SYN_GROUP_A" if speaker_index <= 6 else "SYN_GROUP_B"
        for sentence_set in ("SET_1", "SET_2", "SET_3", "SET_4"):
            for profile in ("primary", "alternative"):
                for unit_index in range(1, 11):
                    vowel = rng.uniform(65, 150) * (1.05 if sentence_set in ("SET_3", "SET_4") else 1.0)
                    consonant = rng.uniform(55, 180) * (1.08 if group == "SYN_GROUP_B" else 1.0)
                    if profile == "alternative":
                        shift = rng.uniform(-8, 8)
                        vowel = max(20, vowel + shift)
                        consonant = max(20, consonant - shift)
                    segmented.append({"speaker_id": speaker, "sample_group": group, "sentence_set": sentence_set, "segmentation_profile": profile, "unit_index": unit_index, "vowel_duration_ms": round(vowel, 4), "consonant_duration_ms": round(consonant, 4), "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
    write_tsv(CHAPTER_ROOT / "segmented_intervals.tsv", segmented, list(segmented[0]))
    model_comparison = {"schema_version": "0.1", "data_status": "SYNTHETIC_TEACHING_FIXTURE", "naive_model": "condition-specific smooth only", "structured_model": "condition smooth plus speaker/item random effects and speaker factor smooth", "residual_rho": 0.6, "series_start": "first requested frame per token", "prediction_grid": {"proportional_start": 0, "proportional_end": 1, "step": 0.02}, "rhythm_metrics": ["percent_v", "varco_v", "npvi_v"], "claim_limit": "sample descriptions and synthetic comparisons only; no language rhythm classification"}
    (CHAPTER_ROOT / "model_comparison.yaml").write_text(yaml.safe_dump(model_comparison, sort_keys=False), encoding="utf-8")

    files = sorted(path for path in CHAPTER_ROOT.iterdir() if path.is_file())
    chapter_rows = [{"artifact_id": f"CH12_SYN_{index+1:02d}", "relative_path": str(path.relative_to(DATA_ROOT)), "data_status": "SYNTHETIC_TEACHING_FIXTURE", "source": "generated locally by companion/scripts/generate_ch12_fixture.py", "license": "CC-BY-4.0", "sha256": sha256_file(path), "contains_human_data": "false"} for index, path in enumerate(files)]
    global_manifest = DATA_ROOT / "MANIFEST.tsv"
    preserved: list[dict[str, str]] = []
    if global_manifest.exists():
        with global_manifest.open("r", encoding="utf-8", newline="") as source:
            preserved = [row for row in csv.DictReader(source, delimiter="\t") if not row["artifact_id"].startswith("CH12_")]
    write_tsv(global_manifest, sorted(preserved + chapter_rows, key=lambda row: row["artifact_id"]), ["artifact_id", "relative_path", "data_status", "source", "license", "sha256", "contains_human_data"])


if __name__ == "__main__":
    main()
