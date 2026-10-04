#!/usr/bin/env python3
"""Generate the explicitly synthetic Chapter 7 teaching fixture."""

from __future__ import annotations

import csv
import hashlib
import math
import struct
import wave
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "companion" / "data"
CHAPTER_ROOT = DATA_ROOT / "ch07" / "synthetic_recordings"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def write_wav(path: Path, amplitude: float, *, sample_rate: int = 16000, duration: float = 1.0) -> None:
    samples = []
    for index in range(round(sample_rate * duration)):
        value = amplitude * math.sin(2 * math.pi * 440 * index / sample_rate)
        bounded = max(-1.0, min(1.0, value))
        samples.append(round(bounded * 32767))
    with wave.open(str(path), "wb") as target:
        target.setnchannels(1)
        target.setsampwidth(2)
        target.setframerate(sample_rate)
        target.writeframes(struct.pack(f"<{len(samples)}h", *samples))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    CHAPTER_ROOT.mkdir(parents=True, exist_ok=True)
    audio_specs = [
        ("SYN_GOOD", "synthetic_good.wav", 0.40, "clean synthetic reference tone"),
        ("SYN_CLIPPED", "synthetic_clipped.wav", 1.20, "synthetic tone deliberately clipped for teaching"),
        ("SYN_QUIET", "synthetic_near_silent.wav", 0.0005, "synthetic near-silent tone for teaching"),
    ]
    for _, filename, amplitude, _ in audio_specs:
        write_wav(CHAPTER_ROOT / filename, amplitude)

    manifest_rows = [
        {
            "file_id": file_id,
            "session_id": "SYN_CH07_SESSION",
            "source_path": filename,
            "expected_sample_rate_hz": 16000,
            "expected_bit_depth": 16,
            "expected_channels": 1,
            "data_status": "SYNTHETIC_TEACHING_FIXTURE",
            "description": description,
        }
        for file_id, filename, _, description in audio_specs
    ]
    manifest_path = CHAPTER_ROOT / "recording_manifest.tsv"
    write_tsv(
        manifest_path,
        manifest_rows,
        [
            "file_id",
            "session_id",
            "source_path",
            "expected_sample_rate_hz",
            "expected_bit_depth",
            "expected_channels",
            "data_status",
            "description",
        ],
    )

    timing_rows = [
        {
            "event_id": f"SYN_EVENT_{index + 1}",
            "expected_time_s": f"{expected:.6f}",
            "observed_time_s": f"{0.002 + 1.0002 * expected:.6f}",
            "data_status": "SYNTHETIC_TEACHING_FIXTURE",
        }
        for index, expected in enumerate((0.0, 1.0, 2.0, 3.0, 4.0))
    ]
    timing_path = CHAPTER_ROOT / "timing_events.tsv"
    write_tsv(
        timing_path,
        timing_rows,
        ["event_id", "expected_time_s", "observed_time_s", "data_status"],
    )

    metadata = {
        "schema_version": "0.1",
        "data_status": "SYNTHETIC_TEACHING_FIXTURE",
        "session": {
            "session_id": "SYN_CH07_SESSION",
            "participant_code": "SYNTHETIC_NO_PARTICIPANT",
            "date_local": "2000-01-01",
            "timezone": "UTC",
            "site_code": "SYNTHETIC_SITE",
            "room_code": "SYNTHETIC_ROOM",
            "operator_code": "SYNTHETIC_GENERATOR",
            "protocol_version": "ch07-fixture-0.1",
            "consent_scope_code": "NOT_APPLICABLE_SYNTHETIC",
        },
        "claim_requirements": {
            "primary_measures": ["duration", "relative_amplitude", "simple_spectrum"],
            "required_bandwidth_hz": 7000,
            "required_timing_precision_ms": 5,
            "amplitude_basis": "relative",
            "synchronization_required": True,
        },
        "signal_chain": {
            "microphone_manufacturer": "SYNTHETIC",
            "microphone_model": "NUMERICAL_SIGNAL_GENERATOR",
            "microphone_unit_id": "SYNTHETIC_NO_HARDWARE",
            "polar_pattern": "NOT_APPLICABLE",
            "mouth_distance_cm": 0,
            "microphone_angle_degrees": 0,
            "mounting_method": "NOT_APPLICABLE",
            "preamplifier_or_interface": "NOT_APPLICABLE",
            "interface_unit_id": "NOT_APPLICABLE",
            "input_channel": "MONO_SYNTHETIC",
            "gain_setting": "NUMERIC_AMPLITUDE_IN_GENERATOR",
            "recorder_or_device": "PYTHON_WAVE_MODULE",
            "operating_system": "PLATFORM_INDEPENDENT_FIXTURE",
            "recording_software": "generate_ch07_fixture.py",
            "recording_software_version": "0.1",
            "processing_disabled": ["all acquisition processing not applicable"],
            "processing_unavoidable_or_unknown": [],
        },
        "file_configuration": {
            "container": "wav",
            "encoding": "linear_pcm",
            "sample_rate_hz": 16000,
            "bit_depth": 16,
            "channel_count": 1,
            "channel_map": ["synthetic_mono"],
        },
        "checks": {
            "ambient_recording_file_id": "NOT_APPLICABLE_SYNTHETIC",
            "setup_test_file_id": "SYN_GOOD",
            "level_calibration_file_id": "NOT_CALIBRATED_RELATIVE_AMPLITUDE_ONLY",
            "timing_check_file_id": "timing_events.tsv",
            "synchronization_event_file_id": "timing_events.tsv",
            "headphones_monitoring_completed": True,
        },
        "events_and_deviations": [
            {
                "event": "purposeful teaching defects",
                "details": "one file is clipped and one is near silent",
            }
        ],
        "post_session": {
            "expected_file_count": 3,
            "observed_file_count": 3,
            "headers_verified": True,
            "channel_content_verified": True,
            "first_verified_copy": "generated fixture directory",
            "second_verified_copy": "regenerable from source script",
            "checksums_manifest": "../MANIFEST.tsv",
        },
        "measure_specific_decisions": [
            {
                "measure": "relative_amplitude",
                "decision": "evaluate clipping and low level before use",
            }
        ],
        "pre_departure_decision": {
            "status": "restricted_use",
            "rationale": "Synthetic defects are retained intentionally for instruction.",
            "decided_by": "fixture_generator",
            "decided_at": "2000-01-01T00:00:00Z",
        },
    }
    metadata_path = CHAPTER_ROOT / "recording_session_metadata.yaml"
    metadata_path.write_text(yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True), encoding="utf-8")

    fixture_files = sorted(path for path in CHAPTER_ROOT.iterdir() if path.is_file())
    data_manifest_rows = [
        {
            "artifact_id": f"CH07_SYN_{index + 1:02d}",
            "relative_path": str(path.relative_to(DATA_ROOT)),
            "data_status": "SYNTHETIC_TEACHING_FIXTURE",
            "source": "generated locally by companion/scripts/generate_ch07_fixture.py",
            "license": "CC-BY-4.0",
            "sha256": sha256_file(path),
            "contains_human_data": "false",
        }
        for index, path in enumerate(fixture_files)
    ]
    global_manifest = DATA_ROOT / "MANIFEST.tsv"
    preserved_rows = []
    if global_manifest.exists():
        with global_manifest.open("r", encoding="utf-8", newline="") as source:
            preserved_rows = [
                row for row in csv.DictReader(source, delimiter="\t")
                if not row["artifact_id"].startswith("CH07_")
            ]
    combined_rows = sorted(preserved_rows + data_manifest_rows, key=lambda row: row["artifact_id"])
    write_tsv(
        global_manifest,
        combined_rows,
        ["artifact_id", "relative_path", "data_status", "source", "license", "sha256", "contains_human_data"],
    )


if __name__ == "__main__":
    main()
