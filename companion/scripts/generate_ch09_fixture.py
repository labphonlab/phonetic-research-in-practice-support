#!/usr/bin/env python3
"""Generate explicitly synthetic Chapter 9 annotation fixtures."""

from __future__ import annotations

import csv
import hashlib
import random
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "companion" / "data"
CHAPTER_ROOT = DATA_ROOT / "ch09" / "synthetic_annotation"
SEED = 9042026


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rng = random.Random(SEED)
    CHAPTER_ROOT.mkdir(parents=True, exist_ok=True)
    schema = {
        "schema_version": "0.1",
        "data_status": "SYNTHETIC_TEACHING_FIXTURE",
        "scheme": {
            "scheme_id": "SYN_VOICE_QUALITY_01",
            "title": "Synthetic three-category voice-quality judgments",
            "manual_version": "0.1",
            "construct": "instructional perceptual classification, not a validated voice-quality construct",
            "downstream_use": "agreement and category-usability exercise only",
        },
        "unit": {
            "unit_type": "interval",
            "candidate_generation": "120 generated item records in 30 synthetic speaker clusters",
            "parent_unit": "synthetic utterance",
        },
        "evidence": {"audio": False, "waveform": True, "spectrogram": True, "pitch_track": False, "orthography": False, "wider_context": False, "other": []},
        "display": {"software": "fixture table", "software_version": "0.1", "spectrogram_settings": "synthetic only", "playback_controls": "not applicable"},
        "decisions": {
            "detection": {"required": False, "labels": []},
            "boundaries": ["onset", "offset"],
            "classification": {"required": True, "scale": "nominal", "labels": ["modal", "breathy", "creaky"], "distance_function": "identity disagreement"},
            "links": {"required": False, "permitted_targets": ""},
        },
        "uncertainty": {"permitted": True, "codes": ["low_confidence"], "confidence_scale": "1-5"},
        "missingness_codes": ["not_judged"],
        "training": {"training_set_version": "synthetic-training-0.1", "qualification_rule": "not applicable to synthetic fixture", "recalibration_schedule": "after each 40 items"},
        "reliability": {"sampling_design": "two independent first-pass annotators; clustered by synthetic speaker", "primary_statistic": "Cohen kappa with speaker-cluster bootstrap", "clustering_unit": "speaker_id", "boundary_tolerances_ms": [5, 10, 20]},
        "adjudication": {"method": "none", "preserve_independent_labels": True},
    }
    schema_path = CHAPTER_ROOT / "annotation_schema.yaml"
    schema_path.write_text(yaml.safe_dump(schema, sort_keys=False), encoding="utf-8")

    assignments: list[dict[str, object]] = []
    judgments: list[dict[str, object]] = []
    labels = ["modal", "breathy", "creaky"]
    base_weights = [0.62, 0.23, 0.15]
    for item_number in range(1, 121):
        item_id = f"SYN_ANN_{item_number:03d}"
        speaker_id = f"SYN_SPK_{(item_number - 1) // 4 + 1:02d}"
        condition = "easy" if item_number % 3 else "difficult"
        assignments.append({"item_id": item_id, "speaker_id": speaker_id, "condition": condition, "annotator_a": "SYN_RATER_A", "annotator_b": "SYN_RATER_B", "assignment_status": "independent_first_pass", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
        truth = rng.choices(labels, weights=base_weights, k=1)[0]
        for annotator in ("SYN_RATER_A", "SYN_RATER_B"):
            accuracy = 0.92 if condition == "easy" else (0.72 if annotator == "SYN_RATER_A" else 0.67)
            if rng.random() < accuracy:
                label = truth
            else:
                label = rng.choice([candidate for candidate in labels if candidate != truth])
            judgments.append({
                "item_id": item_id,
                "speaker_id": speaker_id,
                "condition": condition,
                "annotator_id": annotator,
                "label": label,
                "confidence": rng.randint(3, 5) if condition == "easy" else rng.randint(1, 4),
                "judgment_stage": "independent_first_pass",
                "automatic_default_present": "false",
                "adjudicated": "false",
                "data_status": "SYNTHETIC_TEACHING_FIXTURE",
            })
    write_tsv(CHAPTER_ROOT / "annotation_assignments.tsv", assignments, list(assignments[0]))
    write_tsv(CHAPTER_ROOT / "categorical_judgments.tsv", judgments, list(judgments[0]))

    boundary_rows: list[dict[str, object]] = []
    for assignment in assignments:
        item_id = str(assignment["item_id"])
        speaker_id = str(assignment["speaker_id"])
        condition = str(assignment["condition"])
        base_onset = rng.uniform(80, 180)
        base_offset = base_onset + rng.uniform(70, 150)
        for boundary_type, base_time in (("onset", base_onset), ("offset", base_offset)):
            condition_sd = 3.0 if condition == "easy" else 9.0
            for annotator, bias in (("SYN_RATER_A", -1.0), ("SYN_RATER_B", 2.0)):
                boundary_rows.append({
                    "item_id": item_id,
                    "speaker_id": speaker_id,
                    "condition": condition,
                    "boundary_type": boundary_type,
                    "annotator_id": annotator,
                    "time_ms": round(base_time + bias + rng.gauss(0, condition_sd), 3),
                    "judgment_stage": "independent_first_pass",
                    "data_status": "SYNTHETIC_TEACHING_FIXTURE",
                })
    write_tsv(CHAPTER_ROOT / "boundary_judgments.tsv", boundary_rows, list(boundary_rows[0]))

    audit_rows: list[dict[str, object]] = []
    for item_number in range(1, 241):
        mode = "from_scratch" if item_number % 2 else "correct_default"
        difficulty = "easy" if item_number % 3 else "difficult"
        default_label = rng.choices(labels, weights=[0.70, 0.18, 0.12], k=1)[0]
        latent_label = rng.choices(labels, weights=[0.55, 0.27, 0.18], k=1)[0]
        if mode == "correct_default":
            retention_probability = 0.90 if difficulty == "easy" else 0.76
            final_label = default_label if rng.random() < retention_probability else latent_label
            annotation_time = rng.gauss(6.5 if difficulty == "easy" else 10.0, 1.2)
        else:
            final_label = latent_label
            annotation_time = rng.gauss(10.0 if difficulty == "easy" else 15.0, 1.8)
        default_boundary = rng.uniform(100, 240)
        final_boundary = default_boundary + rng.gauss(1.5 if mode == "correct_default" else 0.0, 3.0 if difficulty == "easy" else 8.0)
        audit_rows.append({
            "audit_id": f"SYN_AUTO_{item_number:03d}",
            "item_id": f"SYN_AUTO_ITEM_{item_number:03d}",
            "speaker_id": f"SYN_AUTO_SPK_{(item_number - 1) // 8 + 1:02d}",
            "counterbalance_group": "A" if item_number % 4 < 2 else "B",
            "annotation_mode": mode,
            "difficulty": difficulty,
            "automatic_default_label": default_label,
            "automatic_default_boundary_ms": round(default_boundary, 3),
            "final_label": final_label,
            "final_boundary_ms": round(final_boundary, 3),
            "annotation_time_s": round(max(1.0, annotation_time), 3),
            "confidence": rng.randint(3, 5) if difficulty == "easy" else rng.randint(1, 4),
            "data_status": "SYNTHETIC_TEACHING_FIXTURE",
        })
    write_tsv(CHAPTER_ROOT / "automatic_proposal_audit.tsv", audit_rows, list(audit_rows[0]))

    fixture_files = sorted(path for path in CHAPTER_ROOT.iterdir() if path.is_file())
    chapter_manifest_rows = [
        {"artifact_id": f"CH09_SYN_{index + 1:02d}", "relative_path": str(path.relative_to(DATA_ROOT)), "data_status": "SYNTHETIC_TEACHING_FIXTURE", "source": "generated locally by companion/scripts/generate_ch09_fixture.py", "license": "CC-BY-4.0", "sha256": sha256_file(path), "contains_human_data": "false"}
        for index, path in enumerate(fixture_files)
    ]
    global_manifest = DATA_ROOT / "MANIFEST.tsv"
    preserved_rows: list[dict[str, str]] = []
    if global_manifest.exists():
        with global_manifest.open("r", encoding="utf-8", newline="") as source:
            preserved_rows = [row for row in csv.DictReader(source, delimiter="\t") if not row["artifact_id"].startswith("CH09_")]
    write_tsv(global_manifest, sorted(preserved_rows + chapter_manifest_rows, key=lambda row: row["artifact_id"]), ["artifact_id", "relative_path", "data_status", "source", "license", "sha256", "contains_human_data"])


if __name__ == "__main__":
    main()
