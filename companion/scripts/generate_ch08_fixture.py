#!/usr/bin/env python3
"""Generate the explicitly synthetic Chapter 8 perception fixtures."""

from __future__ import annotations

import csv
import hashlib
import math
import random
import struct
import wave
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "companion" / "data"
CHAPTER_ROOT = DATA_ROOT / "ch08" / "synthetic_perception"
SEED = 8042026


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


def write_tone(path: Path, frequency_hz: float, sample_rate: int = 16000, duration_s: float = 0.25) -> None:
    samples = [
        round(0.25 * math.sin(2 * math.pi * frequency_hz * index / sample_rate) * 32767)
        for index in range(round(sample_rate * duration_s))
    ]
    with wave.open(str(path), "wb") as target:
        target.setnchannels(1)
        target.setsampwidth(2)
        target.setframerate(sample_rate)
        target.writeframes(struct.pack(f"<{len(samples)}h", *samples))


def logistic(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def main() -> None:
    rng = random.Random(SEED)
    stimuli_dir = CHAPTER_ROOT / "stimuli"
    stimuli_dir.mkdir(parents=True, exist_ok=True)

    stimulus_rows: list[dict[str, object]] = []
    for step in range(-3, 4):
        stimulus_id = f"SYN_CONT_{step + 4:02d}"
        frequency = 450 + 35 * step
        path = stimuli_dir / f"{stimulus_id}.wav"
        write_tone(path, frequency)
        stimulus_rows.append(
            {
                "stimulus_id": stimulus_id,
                "continuum_id": "SYN_TONE_FREQUENCY",
                "continuum_step": step,
                "acoustic_value_hz": frequency,
                "asset_path": str(path.relative_to(CHAPTER_ROOT)),
                "sha256": sha256_file(path),
                "license": "CC-BY-4.0",
                "data_status": "SYNTHETIC_TEACHING_FIXTURE",
                "interpretive_limit": "numerical tone; not speech or evidence of categorical perception",
            }
        )
    stimulus_manifest = CHAPTER_ROOT / "stimulus_manifest.tsv"
    write_tsv(
        stimulus_manifest,
        stimulus_rows,
        [
            "stimulus_id", "continuum_id", "continuum_step", "acoustic_value_hz", "asset_path",
            "sha256", "license", "data_status", "interpretive_limit",
        ],
    )

    trial_rows: list[dict[str, object]] = []
    response_rows: list[dict[str, object]] = []
    for participant_index in range(1, 13):
        participant = f"SYN_P{participant_index:02d}"
        location = rng.uniform(-0.55, 0.55)
        slope = -0.85 if participant_index == 12 else rng.uniform(1.0, 1.55)
        trial_index = 0
        for item_index in range(1, 5):
            for step in range(-3, 4):
                trial_index += 1
                trial_id = f"SYN_ID_{participant_index:02d}_{trial_index:03d}"
                stimulus_id = f"SYN_CONT_{step + 4:02d}"
                probability_b = logistic(slope * (step - location))
                binary_response = int(rng.random() < probability_b)
                rt_ms = max(220, round(rng.gauss(720 - 45 * abs(step), 70)))
                trial_rows.append(
                    {
                        "schema_version": "0.1",
                        "participant_code": participant,
                        "session_id": f"SYN_SESSION_{participant_index:02d}",
                        "list_id": "SYN_LIST_A",
                        "block_index": 1,
                        "trial_index": trial_index,
                        "stimulus_id": stimulus_id,
                        "condition_id": "SYN_FREQUENCY_CONTINUUM",
                        "item_id": f"SYN_ITEM_{item_index:02d}",
                        "talker_id": "NOT_APPLICABLE_SYNTHETIC_TONE",
                        "continuum_id": "SYN_TONE_FREQUENCY",
                        "continuum_step": step,
                        "response_mapping_id": "LOW_A_HIGH_B",
                        "correctness_definition": "NOT_APPLICABLE_CLASSIFICATION",
                        "rt_origin": "stimulus_onset",
                        "timeout_ms": 2000,
                        "practice": "false",
                        "feedback": "false",
                        "randomization_seed": SEED,
                        "trial_id": trial_id,
                        "data_status": "SYNTHETIC_TEACHING_FIXTURE",
                    }
                )
                response_rows.append(
                    {
                        "trial_id": trial_id,
                        "participant_code": participant,
                        "stimulus_id": stimulus_id,
                        "continuum_step": step,
                        "response_category": "B" if binary_response else "A",
                        "binary_response": binary_response,
                        "rt_ms": rt_ms,
                        "data_status": "SYNTHETIC_TEACHING_FIXTURE",
                    }
                )
    write_tsv(CHAPTER_ROOT / "perception_trial_manifest.tsv", trial_rows, list(trial_rows[0]))
    write_tsv(CHAPTER_ROOT / "psychometric_responses.tsv", response_rows, list(response_rows[0]))

    detection_rows: list[dict[str, object]] = []
    event_number = 0
    condition_counts = {
        "SYN_NEUTRAL": {"signal_yes": 34, "noise_yes": 6, "rt_mean": 650},
        "SYN_CONSERVATIVE": {"signal_yes": 26, "noise_yes": 2, "rt_mean": 725},
    }
    for participant_index in range(1, 13):
        participant = f"SYN_P{participant_index:02d}"
        for condition, values in condition_counts.items():
            for signal_present, label, yes_count in (
                (1, "signal", values["signal_yes"]),
                (0, "noise", values["noise_yes"]),
            ):
                responses = [1] * yes_count + [0] * (40 - yes_count)
                rng.shuffle(responses)
                for yes_response in responses:
                    event_number += 1
                    correctness = int(yes_response == signal_present)
                    detection_rows.append(
                        {
                            "event_id": f"SYN_DET_{event_number:05d}",
                            "participant_code": participant,
                            "condition_id": condition,
                            "trial_type": label,
                            "signal_present": signal_present,
                            "yes_response": yes_response,
                            "correct": correctness,
                            "rt_ms": max(180, round(rng.gauss(values["rt_mean"], 85))),
                            "rt_origin": "stimulus_onset",
                            "device_profile": "SYN_BROWSER_PROFILE_A",
                            "data_status": "SYNTHETIC_TEACHING_FIXTURE",
                        }
                    )
            for rt_ms, reason_label in ((100, "too_early"), (2500, "timeout")):
                event_number += 1
                detection_rows.append(
                    {
                        "event_id": f"SYN_DET_{event_number:05d}",
                        "participant_code": participant,
                        "condition_id": condition,
                        "trial_type": "signal",
                        "signal_present": 1,
                        "yes_response": int(reason_label == "too_early"),
                        "correct": int(reason_label == "too_early"),
                        "rt_ms": rt_ms,
                        "rt_origin": "stimulus_onset",
                        "device_profile": "SYN_BROWSER_PROFILE_A",
                        "data_status": "SYNTHETIC_TEACHING_FIXTURE",
                    }
                )
    write_tsv(CHAPTER_ROOT / "detection_event_log.tsv", detection_rows, list(detection_rows[0]))

    decisions = {
        "schema_version": "0.1",
        "data_status": "SYNTHETIC_TEACHING_FIXTURE",
        "trial_type_definition": {"signal": "signal_present=1", "noise": "signal_present=0"},
        "response_definition": {"yes": "yes_response=1", "no": "yes_response=0"},
        "correction": "loglinear_0.5",
        "reaction_time": {"origin": "stimulus_onset", "minimum_ms": 150, "maximum_ms": 2000},
        "interpretive_limit": "synthetic event counts demonstrate decomposition; they do not estimate human sensitivity",
        "seed": SEED,
    }
    (CHAPTER_ROOT / "signal_detection_decisions.yaml").write_text(
        yaml.safe_dump(decisions, sort_keys=False), encoding="utf-8"
    )

    timing_audit_rows = [
        {
            "configuration_id": configuration,
            "event_count_expected": 100,
            "event_count_observed": 100,
            "median_onset_error_ms": median_error,
            "p95_onset_error_ms": p95_error,
            "rt_origin": "stimulus_onset",
            "asset_hashes_verified": "true",
            "data_status": "SYNTHETIC_TEACHING_FIXTURE",
        }
        for configuration, median_error, p95_error in (
            ("SYN_DESKTOP_CONFIG", 3.2, 8.5),
            ("SYN_MOBILE_CONFIG", 18.4, 43.7),
        )
    ]
    write_tsv(CHAPTER_ROOT / "online_timing_audit.tsv", timing_audit_rows, list(timing_audit_rows[0]))

    fixture_files = sorted(path for path in CHAPTER_ROOT.rglob("*") if path.is_file())
    chapter_manifest_rows = [
        {
            "artifact_id": f"CH08_SYN_{index + 1:02d}",
            "relative_path": str(path.relative_to(DATA_ROOT)),
            "data_status": "SYNTHETIC_TEACHING_FIXTURE",
            "source": "generated locally by companion/scripts/generate_ch08_fixture.py",
            "license": "CC-BY-4.0",
            "sha256": sha256_file(path),
            "contains_human_data": "false",
        }
        for index, path in enumerate(fixture_files)
    ]
    global_manifest = DATA_ROOT / "MANIFEST.tsv"
    preserved_rows: list[dict[str, str]] = []
    if global_manifest.exists():
        with global_manifest.open("r", encoding="utf-8", newline="") as source:
            preserved_rows = [
                row for row in csv.DictReader(source, delimiter="\t")
                if not row["artifact_id"].startswith("CH08_")
            ]
    combined_rows = sorted(preserved_rows + chapter_manifest_rows, key=lambda row: row["artifact_id"])
    write_tsv(
        global_manifest,
        combined_rows,
        ["artifact_id", "relative_path", "data_status", "source", "license", "sha256", "contains_human_data"],
    )


if __name__ == "__main__":
    main()
