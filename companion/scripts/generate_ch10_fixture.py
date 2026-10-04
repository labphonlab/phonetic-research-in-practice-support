#!/usr/bin/env python3
"""Generate explicitly synthetic Chapter 10 acoustic-measurement fixtures."""

from __future__ import annotations

import csv
import hashlib
import random
import wave
from pathlib import Path

import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "companion" / "data"
CHAPTER_ROOT = DATA_ROOT / "ch10" / "synthetic_acoustics"
SEED = 10042026
SAMPLE_RATE = 16000


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def synthetic_vowel(f0: float, formants: tuple[float, float, float], *, duration: float = 0.6, noise: float = 0.002, irregular: bool = False) -> np.ndarray:
    rng = np.random.default_rng(SEED + round(f0 * 10))
    time = np.arange(round(SAMPLE_RATE * duration)) / SAMPLE_RATE
    phase = 2 * np.pi * f0 * time
    if irregular:
        phase += 0.9 * np.sin(2 * np.pi * 3.2 * time)
    signal = np.zeros_like(time)
    for harmonic in range(1, max(2, int(5000 // f0))):
        frequency = harmonic * f0
        spectral_shape = sum(np.exp(-0.5 * ((frequency - formant) / bandwidth) ** 2) for formant, bandwidth in zip(formants, (90, 130, 180)))
        signal += (0.04 + spectral_shape) * np.sin(harmonic * phase) / harmonic
    envelope = np.minimum(1.0, time / 0.04) * np.minimum(1.0, (duration - time) / 0.04)
    signal = signal * np.clip(envelope, 0, 1) + rng.normal(0, noise, len(time))
    signal /= max(np.max(np.abs(signal)), 1e-9)
    return 0.55 * signal


def write_wav(path: Path, signal: np.ndarray) -> None:
    pcm = np.clip(np.round(signal * 32767), -32768, 32767).astype("<i2")
    with wave.open(str(path), "wb") as target:
        target.setnchannels(1)
        target.setsampwidth(2)
        target.setframerate(SAMPLE_RATE)
        target.writeframes(pcm.tobytes())


def main() -> None:
    rng = random.Random(SEED)
    audio_root = CHAPTER_ROOT / "audio"
    audio_root.mkdir(parents=True, exist_ok=True)
    specifications = [
        ("SYN_VOWEL_01", 120, (500, 1500, 2500), 0.002, False, "reference_mid_f0"),
        ("SYN_VOWEL_02", 78, (420, 1250, 2400), 0.002, False, "low_f0_floor_risk"),
        ("SYN_VOWEL_03", 265, (380, 2100, 2850), 0.002, False, "high_f0_ceiling_risk"),
        ("SYN_VOWEL_04", 145, (650, 1150, 2350), 0.015, False, "noisy_formant_risk"),
        ("SYN_VOWEL_05", 105, (520, 1650, 2550), 0.004, True, "irregular_pitch_risk"),
        ("SYN_VOWEL_06", 190, (330, 2800, 3400), 0.006, False, "high_formant_risk"),
        ("SYN_VOWEL_07", 160, (500, 1500, 2500), 0.000001, False, "low_energy_missing"),
    ]
    source_rows: list[dict[str, object]] = []
    interval_rows: list[dict[str, object]] = []
    for file_id, f0, formants, noise, irregular, teaching_role in specifications:
        path = audio_root / f"{file_id}.wav"
        signal = np.random.default_rng(SEED + 7).normal(0, 0.000001, round(SAMPLE_RATE * 0.6)) if teaching_role == "low_energy_missing" else synthetic_vowel(f0, formants, noise=noise, irregular=irregular)
        write_wav(path, signal)
        source_rows.append({"file_id": file_id, "source_path": str(path.relative_to(CHAPTER_ROOT)), "sample_rate_hz": SAMPLE_RATE, "channel": 1, "sha256": sha256_file(path), "data_status": "SYNTHETIC_TEACHING_FIXTURE", "teaching_role": teaching_role, "true_f0_hz_generator_only": f0, "true_formants_hz_generator_only": ",".join(map(str, formants))})
        interval_rows.append({"observation_id": f"OBS_{file_id}", "file_id": file_id, "interval_start_s": 0.10, "interval_end_s": 0.50, "label": "synthetic_vowel", "condition_blinded": f"BLIND_{len(interval_rows)+1:02d}", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
    write_tsv(CHAPTER_ROOT / "source_manifest.tsv", source_rows, list(source_rows[0]))
    write_tsv(CHAPTER_ROOT / "interval_manifest.tsv", interval_rows, list(interval_rows[0]))

    measurement_spec = {
        "schema_version": "0.1",
        "data_status": "SYNTHETIC_TEACHING_FIXTURE",
        "measure": {"measure_id": "SYN_F0_FORMANTS", "construct": "instructional periodicity and spectral-resonance estimates", "measurand": "frame F0 and interval spectral peak locations", "unit": "Hz", "representation": "trajectory"},
        "source_requirements": {"channel": 1, "minimum_sample_rate_hz": 16000, "recording_constraints": ["mono linear PCM", "synthetic fixture only"]},
        "annotation_requirements": {"tier": "synthetic_interval", "included_labels": ["synthetic_vowel"], "excluded_labels": []},
        "window": {"alignment_event": "interval start", "start_rule": "interval_start_s", "end_rule": "interval_end_s", "window_length_ms": 40, "frame_step_ms": 10},
        "preprocessing": {"operations": ["remove frame mean", "Hann window for formant spectrum"]},
        "estimator": {"software": "phonetic_research_companion.ch10", "software_version": "0.1.0", "algorithm": "normalized autocorrelation F0; spectral peak teaching estimator", "settings_profile_id": "prespecified_profiles", "settings": {}},
        "output": {"raw_variable": "value_hz", "analysis_variable": "not selected in QC notebook", "confidence_variable": "autocorrelation_peak_or_spectral_prominence", "missingness_codes": ["low_energy", "no_candidate", "insufficient_peaks"]},
        "quality_control": {"admissible_range": "profile-specific", "flags": ["missing_frame", "near_search_limit", "abrupt_jump", "insufficient_formants", "formant_crossing"], "risk_strata": ["teaching_role"], "review_sample_rule": "all flagged observations plus deterministic unflagged sample", "correction_policy": "retain raw candidates; amend settings and rerun"},
        "validation": {"target_domain": "synthetic source-filter signals", "reference_method": "known generator parameters for pedagogy only", "sampling_design": "six adverse and reference signals", "primary_error_summaries": ["missing fraction", "median absolute F0 error for fixture"], "differential_error_checks": ["teaching_role", "profile"], "acceptance_rule": "profile must not exceed 20% missing frames and must flag search-limit contact"},
        "sensitivity": {"prespecified_profiles": [
            {"profile_id": "F0_LOW", "measure": "f0", "floor_hz": 50, "ceiling_hz": 200},
            {"profile_id": "F0_GENERAL", "measure": "f0", "floor_hz": 70, "ceiling_hz": 350},
            {"profile_id": "F0_HIGH", "measure": "f0", "floor_hz": 120, "ceiling_hz": 500},
            {"profile_id": "FORMANT_4500", "measure": "formant", "maximum_hz": 4500, "peak_count": 3},
            {"profile_id": "FORMANT_5500", "measure": "formant", "maximum_hz": 5500, "peak_count": 3}
        ], "claim_stability_rule": "choose by blinded signal-level quality, not group outcome"},
        "provenance": {"source_hash_required": True, "retain_raw_output": True, "overwrite_permitted": False},
        "interpretive_limit": "teaching estimators and generated signals are not validated human-speech measurements",
    }
    (CHAPTER_ROOT / "acoustic_measurement_spec.yaml").write_text(yaml.safe_dump(measurement_spec, sort_keys=False), encoding="utf-8")

    automatic_rows: list[dict[str, object]] = []
    reference_rows: list[dict[str, object]] = []
    validation_rows: list[dict[str, object]] = []
    correction_rows: list[dict[str, object]] = []
    contexts = ["vowel", "fricative", "stop"]
    for index in range(1, 121):
        observation_id = f"SYN_DUR_{index:03d}"
        context = contexts[(index - 1) % len(contexts)]
        speaker_id = f"SYN_DSPK_{(index - 1) // 6 + 1:02d}"
        reference_onset = rng.uniform(100, 300)
        reference_duration = rng.uniform(45, 180)
        reference_offset = reference_onset + reference_duration
        if index % 17 == 0:
            onset_error = 12.0
            offset_error = 12.0
        else:
            error_sd = {"vowel": 3.0, "fricative": 7.0, "stop": 10.0}[context]
            onset_error = rng.gauss(1.0, error_sd)
            offset_error = rng.gauss(-1.0, error_sd)
        automatic_onset = reference_onset + onset_error
        automatic_offset = reference_offset + offset_error
        raw_status = "ok"
        if index % 29 == 0:
            automatic_offset = ""
            raw_status = "missing_offset"
        automatic_rows.append({"observation_id": observation_id, "speaker_id": speaker_id, "context": context, "automatic_onset_ms": round(automatic_onset, 3), "automatic_offset_ms": round(automatic_offset, 3) if automatic_offset != "" else "", "extractor_status": raw_status, "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
        reference_rows.append({"observation_id": observation_id, "reference_onset_ms": round(reference_onset, 3), "reference_offset_ms": round(reference_offset, 3), "reference_method": "synthetic_generator_truth", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
        validation_rows.append({"observation_id": observation_id, "validation_included": "true", "risk_stratum": context, "review_blinded": "true", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
        if index % 23 == 0:
            correction_rows.append({"observation_id": observation_id, "corrected_onset_ms": round(reference_onset, 3), "corrected_offset_ms": round(reference_offset, 3), "correction_action": "replace_both_boundaries", "reason_code": "synthetic_large_error_review", "reviewer_code": "SYN_REVIEWER", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
        elif index % 29 == 0:
            correction_rows.append({"observation_id": observation_id, "corrected_onset_ms": round(reference_onset, 3), "corrected_offset_ms": round(reference_offset, 3), "correction_action": "replace_missing_offset", "reason_code": "synthetic_missing_output_review", "reviewer_code": "SYN_REVIEWER", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
    write_tsv(CHAPTER_ROOT / "automatic_landmarks.tsv", automatic_rows, list(automatic_rows[0]))
    write_tsv(CHAPTER_ROOT / "reference_landmarks.tsv", reference_rows, list(reference_rows[0]))
    write_tsv(CHAPTER_ROOT / "duration_validation_manifest.tsv", validation_rows, list(validation_rows[0]))
    write_tsv(CHAPTER_ROOT / "correction_decisions.tsv", correction_rows, list(correction_rows[0]))

    fixture_files = sorted(path for path in CHAPTER_ROOT.rglob("*") if path.is_file())
    chapter_manifest_rows = [{"artifact_id": f"CH10_SYN_{index+1:02d}", "relative_path": str(path.relative_to(DATA_ROOT)), "data_status": "SYNTHETIC_TEACHING_FIXTURE", "source": "generated locally by companion/scripts/generate_ch10_fixture.py", "license": "CC-BY-4.0", "sha256": sha256_file(path), "contains_human_data": "false"} for index, path in enumerate(fixture_files)]
    global_manifest = DATA_ROOT / "MANIFEST.tsv"
    preserved_rows: list[dict[str, str]] = []
    if global_manifest.exists():
        with global_manifest.open("r", encoding="utf-8", newline="") as source:
            preserved_rows = [row for row in csv.DictReader(source, delimiter="\t") if not row["artifact_id"].startswith("CH10_")]
    write_tsv(global_manifest, sorted(preserved_rows + chapter_manifest_rows, key=lambda row: row["artifact_id"]), ["artifact_id", "relative_path", "data_status", "source", "license", "sha256", "contains_human_data"])


if __name__ == "__main__":
    main()
