#!/usr/bin/env python3
"""Generate explicitly synthetic Chapter 13 multimodal fixtures."""

from __future__ import annotations

import csv
import hashlib
import math
import random
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "companion" / "data"
CHAPTER_ROOT = DATA_ROOT / "ch13" / "synthetic_multimodal"
SEED = 13042026


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def rotate(x: float, y: float, angle: float) -> tuple[float, float]:
    return math.cos(angle) * x - math.sin(angle) * y, math.sin(angle) * x + math.cos(angle) * y


def main() -> None:
    rng = random.Random(SEED)
    CHAPTER_ROOT.mkdir(parents=True, exist_ok=True)

    stream_rows = [
        {"stream_id": "SYN_EMA", "modality": "ema", "role": "primary", "native_unit": "mm", "nominal_rate_hz": 100, "clock": "articulatory", "data_status": "SYNTHETIC_TEACHING_FIXTURE"},
        {"stream_id": "SYN_AUDIO_CLOCK", "modality": "audio", "role": "complementary", "native_unit": "s", "nominal_rate_hz": 48000, "clock": "reference", "data_status": "SYNTHETIC_TEACHING_FIXTURE"},
    ]
    write_tsv(CHAPTER_ROOT / "stream_manifest.tsv", stream_rows, list(stream_rows[0]))

    coordinate_rows: list[dict[str, object]] = []
    transform_rows: list[dict[str, object]] = []
    anatomy_angle = math.radians(15)
    for frame in range(240):
        if frame in (80, 81):
            continue
        time_s = frame / 100
        head_angle = 0.08 * math.sin(2 * math.pi * time_s / 2.4)
        translation = (2.5 * math.sin(2 * math.pi * time_s / 1.7), 1.8 * math.cos(2 * math.pi * time_s / 2.1))
        tongue_head = (5 * math.sin(2 * math.pi * time_s), 8 + 7 * math.sin(math.pi * time_s / 1.2) ** 2)
        positions = {"REF_A": (-20.0, 0.0), "REF_B": (20.0, 0.0), "TONGUE": tongue_head, "STATIONARY": (0.0, -18.0)}
        observed: dict[str, tuple[float, float]] = {}
        for sensor, (head_x, head_y) in positions.items():
            native_x, native_y = rotate(head_x, head_y, head_angle)
            native_x += translation[0]
            native_y += translation[1]
            if sensor == "REF_B" and 140 <= frame <= 170:
                drift = 5 * (frame - 139) / 31
                native_x += drift
                native_y += 0.4 * drift
            native_x += rng.gauss(0, 0.025)
            native_y += rng.gauss(0, 0.025)
            observed[sensor] = (native_x, native_y)
            coordinate_rows.append({"stream_id": "SYN_EMA", "frame_index": frame, "native_time_s": round(time_s, 6), "sensor_id": sensor, "native_x_mm": round(native_x, 6), "native_y_mm": round(native_y, 6), "generator_head_x_mm": round(head_x, 6), "generator_head_y_mm": round(head_y, 6), "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
        ax, ay = observed["REF_A"]
        bx, by = observed["REF_B"]
        midpoint_x, midpoint_y = (ax + bx) / 2, (ay + by) / 2
        observed_angle = math.atan2(by - ay, bx - ax)
        c, s = math.cos(-observed_angle), math.sin(-observed_angle)
        native_to_head = (c, -s, -(c * midpoint_x - s * midpoint_y), s, c, -(s * midpoint_x + c * midpoint_y), 0.0, 0.0, 1.0)
        ca, sa = math.cos(anatomy_angle), math.sin(anatomy_angle)
        head_to_anatomical = (ca, -sa, 0.0, sa, ca, 0.0, 0.0, 0.0, 1.0)
        for transform_id, matrix in (("native_to_head", native_to_head), ("head_to_anatomical", head_to_anatomical)):
            row: dict[str, object] = {"frame_index": frame, "native_time_s": round(time_s, 6), "transform_id": transform_id, "data_status": "SYNTHETIC_TEACHING_FIXTURE"}
            for index, value in enumerate(matrix):
                row[f"m{index // 3 + 1}{index % 3 + 1}"] = round(value, 10)
            transform_rows.append(row)
    write_tsv(CHAPTER_ROOT / "native_coordinates.tsv", coordinate_rows, list(coordinate_rows[0]))
    write_tsv(CHAPTER_ROOT / "transformation_matrices.tsv", transform_rows, list(transform_rows[0]))

    sync_rows: list[dict[str, object]] = []
    for event_index, audio_time in enumerate(range(0, 120, 10), start=1):
        articulatory_time: object = round(0.035 + 1.0004 * audio_time + rng.uniform(-0.0008, 0.0008), 6)
        status = "observed"
        if event_index == 7:
            articulatory_time, status = "", "dropped_event"
        sync_rows.append({"event_id": f"SYNC_{event_index:02d}", "reference_time_s": audio_time, "articulatory_time_s": articulatory_time, "event_status": status, "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
    write_tsv(CHAPTER_ROOT / "calibration_sync_events.tsv", sync_rows, list(sync_rows[0]))

    trajectory_rows: list[dict[str, object]] = []
    shapes = ("smooth", "plateaued", "multi_peaked", "noisy", "missing", "low_excursion")
    for event_number in range(1, 25):
        shape = shapes[(event_number - 1) % len(shapes)]
        event_id = f"SYN_KIN_{event_number:03d}"
        speaker_id = f"SYN_ART_SPK_{(event_number - 1) // 4 + 1:02d}"
        for sample_index in range(101):
            time_ms = sample_index * 5
            p = sample_index / 100
            base = 12 * math.sin(math.pi * p) ** 2
            if shape == "plateaued":
                base = 12 * min(1.0, max(0.0, p / 0.35), max(0.0, (1 - p) / 0.35))
                if p < 0.35:
                    base = 12 * (p / 0.35) ** 2 * (3 - 2 * p / 0.35)
                elif p > 0.65:
                    q = (1 - p) / 0.35
                    base = 12 * q**2 * (3 - 2 * q)
                else:
                    base = 12
            elif shape == "multi_peaked":
                base = 8 * math.exp(-0.5 * ((p - 0.35) / 0.12) ** 2) + 11 * math.exp(-0.5 * ((p - 0.68) / 0.13) ** 2)
            elif shape == "noisy":
                base += rng.gauss(0, 1.2) + 0.7 * math.sin(20 * math.pi * p)
            elif shape == "low_excursion":
                base *= 0.08
            value: object = round(base + rng.gauss(0, 0.08), 6)
            status = "observed"
            if shape == "missing" and 36 <= sample_index <= 58:
                value, status = "", "tracking_failure"
            trajectory_rows.append({"event_id": event_id, "speaker_id": speaker_id, "shape_class": shape, "sample_index": sample_index, "time_ms": time_ms, "displacement_mm": value, "sample_status": status, "event_domain_start_ms": 0, "event_domain_end_ms": 500, "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
    write_tsv(CHAPTER_ROOT / "validated_trajectories.tsv", trajectory_rows, list(trajectory_rows[0]))

    profiles = {
        "schema_version": "0.1",
        "data_status": "SYNTHETIC_TEACHING_FIXTURE",
        "profiles": [
            {"profile_id": "RAW_15", "filter": "none", "filter_sigma_samples": 0, "peak_fraction": 0.15, "minimum_excursion_mm": 2.0},
            {"profile_id": "RAW_25", "filter": "none", "filter_sigma_samples": 0, "peak_fraction": 0.25, "minimum_excursion_mm": 2.0},
            {"profile_id": "GAUSS_15", "filter": "gaussian", "filter_sigma_samples": 1.5, "peak_fraction": 0.15, "minimum_excursion_mm": 2.0},
            {"profile_id": "GAUSS_25", "filter": "gaussian", "filter_sigma_samples": 1.5, "peak_fraction": 0.25, "minimum_excursion_mm": 2.0},
        ],
        "selection_rule": "earliest positive velocity peak above the profile threshold; retain every candidate",
        "nonidentifiable_rules": {"maximum_missing_fraction": 0.15, "maximum_target_plateau_ms": 80, "multiple_candidates": "retain and flag", "software_failure": "separate from phonetic nonidentifiability"},
    }
    (CHAPTER_ROOT / "landmark_profiles.yaml").write_text(yaml.safe_dump(profiles, sort_keys=False), encoding="utf-8")

    session = {
        "schema_version": "0.1",
        "data_status": "SYNTHETIC_TEACHING_FIXTURE",
        "session": {"session_id": "SYN_MM_SESSION_01", "participant_id": "SYNTHETIC_ONLY", "operator": "fixture_generator"},
        "coordinates": {"native_frame": "generated_device_xy", "transforms": ["native_to_head", "head_to_anatomical"], "transform_order": ["native_to_head", "head_to_anatomical"], "output_frame": "synthetic_occlusal_xy", "reference_distance_mm": 40.0, "reference_distance_tolerance_mm": 0.75},
        "synchronization": {"reference_stream_id": "SYN_AUDIO_CLOCK", "offset_model": "single median offset", "drift_model": "linear least squares", "dropped_frame_policy": "retain gaps and reason codes", "acceptance_rule_ms": 2.0},
        "gate": {"permitted_decisions": ["accept", "restrict", "amend_and_rerun", "reject"], "combined_rule": "every claimed relation requires valid component streams and residual synchronization error below its temporal scale"},
        "provenance": {"source_hash_required": True, "retain_native_coordinates": True, "retain_native_timestamps": True, "overwrite_permitted": False},
    }
    (CHAPTER_ROOT / "multimodal_session.yaml").write_text(yaml.safe_dump(session, sort_keys=False), encoding="utf-8")

    files = sorted(path for path in CHAPTER_ROOT.iterdir() if path.is_file())
    chapter_rows = [{"artifact_id": f"CH13_SYN_{index + 1:02d}", "relative_path": str(path.relative_to(DATA_ROOT)), "data_status": "SYNTHETIC_TEACHING_FIXTURE", "source": "generated locally by companion/scripts/generate_ch13_fixture.py", "license": "CC-BY-4.0", "sha256": sha256_file(path), "contains_human_data": "false"} for index, path in enumerate(files)]
    global_manifest = DATA_ROOT / "MANIFEST.tsv"
    preserved: list[dict[str, str]] = []
    if global_manifest.exists():
        with global_manifest.open("r", encoding="utf-8", newline="") as source:
            preserved = [row for row in csv.DictReader(source, delimiter="\t") if not row["artifact_id"].startswith("CH13_")]
    write_tsv(global_manifest, sorted(preserved + chapter_rows, key=lambda row: row["artifact_id"]), ["artifact_id", "relative_path", "data_status", "source", "license", "sha256", "contains_human_data"])


if __name__ == "__main__":
    main()
