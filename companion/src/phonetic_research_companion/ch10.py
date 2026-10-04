"""Chapter 10 acoustic-estimation quality control and duration validation."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import yaml
from scipy.ndimage import gaussian_filter1d
from scipy.signal import correlate, find_peaks

from . import __version__


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def _read_mono_pcm(path: Path) -> tuple[int, np.ndarray]:
    with wave.open(str(path), "rb") as source:
        channels = source.getnchannels()
        width = source.getsampwidth()
        sample_rate = source.getframerate()
        frames = source.readframes(source.getnframes())
    if channels != 1 or width != 2:
        raise ValueError(f"Teaching estimator requires mono 16-bit PCM; found channels={channels}, width={width}")
    signal = np.frombuffer(frames, dtype="<i2").astype(np.float64) / 32768.0
    return sample_rate, signal


def _estimate_f0(frame: np.ndarray, sample_rate: int, floor_hz: float, ceiling_hz: float) -> tuple[float | None, float]:
    centered = frame - np.mean(frame)
    energy = float(np.sqrt(np.mean(centered**2)))
    if energy < 1e-4:
        return None, 0.0
    autocorrelation = correlate(centered, centered, mode="full", method="fft")[len(centered) - 1 :]
    autocorrelation /= max(float(autocorrelation[0]), 1e-12)
    minimum_lag = max(1, math.floor(sample_rate / ceiling_hz))
    maximum_lag = min(len(autocorrelation) - 1, math.ceil(sample_rate / floor_hz))
    if maximum_lag <= minimum_lag:
        return None, 0.0
    local = autocorrelation[minimum_lag : maximum_lag + 1]
    lag = minimum_lag + int(np.argmax(local))
    confidence = float(autocorrelation[lag])
    if confidence < 0.25:
        return None, confidence
    return sample_rate / lag, confidence


def _estimate_formants(signal: np.ndarray, sample_rate: int, maximum_hz: float, count: int) -> tuple[list[float], list[float]]:
    emphasized = np.append(signal[0], signal[1:] - 0.97 * signal[:-1])
    windowed = emphasized * np.hanning(len(emphasized))
    size = max(16384, 2 ** math.ceil(math.log2(max(len(windowed), 2))))
    spectrum = 20 * np.log10(np.maximum(np.abs(np.fft.rfft(windowed, n=size)), 1e-12))
    frequencies = np.fft.rfftfreq(size, 1 / sample_rate)
    bin_hz = frequencies[1] - frequencies[0]
    smoothed = gaussian_filter1d(spectrum, sigma=max(1.0, 80 / bin_hz))
    minimum_distance = max(1, round(250 / bin_hz))
    peaks, properties = find_peaks(smoothed, distance=minimum_distance, prominence=1.0)
    eligible = [index for index in peaks if 200 <= frequencies[index] <= maximum_hz]
    eligible.sort(key=lambda index: frequencies[index])
    chosen = eligible[:count]
    prominences = {int(index): float(prominence) for index, prominence in zip(peaks, properties["prominences"])}
    return [float(frequencies[index]) for index in chosen], [prominences[index] for index in chosen]


def _html_table(rows: list[dict[str, Any]], fields: list[str]) -> str:
    header = "".join(f"<th>{html.escape(field)}</th>" for field in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row.get(field, '')))}</td>" for field in fields) + "</tr>" for row in rows)
    return f"<table border='1'><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"


def run_pitch_and_formant_qc(source_manifest_path: Path, interval_manifest_path: Path, specification_path: Path, output_dir: Path) -> dict[str, Any]:
    sources = read_tsv(source_manifest_path)
    intervals = read_tsv(interval_manifest_path)
    specification = yaml.safe_load(specification_path.read_text(encoding="utf-8"))
    if not all(row.get("data_status") == "SYNTHETIC_TEACHING_FIXTURE" for row in sources + intervals):
        raise ValueError("Bundled Chapter 10 source and interval rows must remain explicitly synthetic")
    source_by_id = {row["file_id"]: row for row in sources}
    profiles = specification["sensitivity"]["prespecified_profiles"]
    raw_rows: list[dict[str, Any]] = []
    flag_rows: list[dict[str, Any]] = []
    previous_f0: dict[tuple[str, str], float] = {}
    for interval in intervals:
        source = source_by_id[interval["file_id"]]
        audio_path = (source_manifest_path.parent / source["source_path"]).resolve()
        if sha256_file(audio_path).lower() != source["sha256"].lower():
            raise ValueError(f"Source hash mismatch for {source['file_id']}")
        sample_rate, signal = _read_mono_pcm(audio_path)
        start = round(float(interval["interval_start_s"]) * sample_rate)
        end = round(float(interval["interval_end_s"]) * sample_rate)
        segment = signal[start:end]
        for profile in profiles:
            profile_id = profile["profile_id"]
            if profile["measure"] == "f0":
                frame_length = round(float(specification["window"]["window_length_ms"]) * sample_rate / 1000)
                frame_step = round(float(specification["window"]["frame_step_ms"]) * sample_rate / 1000)
                for frame_index, offset in enumerate(range(0, max(1, len(segment) - frame_length + 1), frame_step)):
                    frame = segment[offset : offset + frame_length]
                    if len(frame) < frame_length:
                        continue
                    value, confidence = _estimate_f0(frame, sample_rate, float(profile["floor_hz"]), float(profile["ceiling_hz"]))
                    status = "ok" if value is not None else "missing"
                    raw_rows.append({"observation_id": interval["observation_id"], "file_id": interval["file_id"], "blinded_condition": interval["condition_blinded"], "measure": "f0", "component": "F0", "profile_id": profile_id, "frame_index": frame_index, "time_s": float(interval["interval_start_s"]) + (offset + frame_length / 2) / sample_rate, "value_hz": "" if value is None else value, "confidence": confidence, "estimator_status": status, "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
                    flags: list[str] = []
                    if value is None:
                        flags.append("missing_frame")
                    else:
                        floor = float(profile["floor_hz"])
                        ceiling = float(profile["ceiling_hz"])
                        if value <= floor * 1.05 or value >= ceiling * 0.95:
                            flags.append("near_search_limit")
                        key = (interval["observation_id"], profile_id)
                        if key in previous_f0 and abs(math.log2(value / previous_f0[key])) > 0.40:
                            flags.append("abrupt_jump")
                        previous_f0[key] = value
                    for flag in flags:
                        flag_rows.append({"observation_id": interval["observation_id"], "measure": "f0", "component": "F0", "profile_id": profile_id, "frame_index": frame_index, "flag": flag, "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
            elif profile["measure"] == "formant":
                values, prominences = _estimate_formants(segment, sample_rate, float(profile["maximum_hz"]), int(profile["peak_count"]))
                for formant_index in range(1, int(profile["peak_count"]) + 1):
                    available = formant_index <= len(values)
                    value = values[formant_index - 1] if available else None
                    raw_rows.append({"observation_id": interval["observation_id"], "file_id": interval["file_id"], "blinded_condition": interval["condition_blinded"], "measure": "formant", "component": f"F{formant_index}", "profile_id": profile_id, "frame_index": "interval", "time_s": (float(interval["interval_start_s"]) + float(interval["interval_end_s"])) / 2, "value_hz": "" if value is None else value, "confidence": prominences[formant_index - 1] if available else 0, "estimator_status": "ok" if available else "missing", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
                    if not available:
                        flag_rows.append({"observation_id": interval["observation_id"], "measure": "formant", "component": f"F{formant_index}", "profile_id": profile_id, "frame_index": "interval", "flag": "insufficient_formants", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
                    elif value >= float(profile["maximum_hz"]) * 0.95:
                        flag_rows.append({"observation_id": interval["observation_id"], "measure": "formant", "component": f"F{formant_index}", "profile_id": profile_id, "frame_index": "interval", "flag": "near_search_limit", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})

    raw_fields = ["observation_id", "file_id", "blinded_condition", "measure", "component", "profile_id", "frame_index", "time_s", "value_hz", "confidence", "estimator_status", "data_status"]
    flag_fields = ["observation_id", "measure", "component", "profile_id", "frame_index", "flag", "data_status"]
    output_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(output_dir / "raw_acoustic_estimates.tsv", raw_rows, raw_fields)
    write_tsv(output_dir / "measurement_flags.tsv", flag_rows, flag_fields)
    summaries: list[dict[str, Any]] = []
    for profile_id in sorted({row["profile_id"] for row in raw_rows}):
        subset = [row for row in raw_rows if row["profile_id"] == profile_id]
        numeric = [float(row["value_hz"]) for row in subset if row["value_hz"] != ""]
        summaries.append({"profile_id": profile_id, "requested": len(subset), "missing": sum(row["estimator_status"] != "ok" for row in subset), "flag_count": sum(row["profile_id"] == profile_id for row in flag_rows), "median_hz": float(np.median(numeric)) if numeric else ""})
    report = "<!doctype html><meta charset='utf-8'><title>Settings comparison</title><h1>Settings comparison</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Estimates come from teaching algorithms and generated signals, not validated human-speech measurements.</p>" + _html_table(summaries, ["profile_id", "requested", "missing", "flag_count", "median_hz"])
    (output_dir / "settings_comparison.html").write_text(report, encoding="utf-8")
    flagged_keys = {(row["observation_id"], row["measure"], row["component"], row["profile_id"], str(row["frame_index"])) for row in flag_rows}
    review_rows = []
    for row in raw_rows:
        key = (row["observation_id"], row["measure"], row["component"], row["profile_id"], str(row["frame_index"]))
        selected = key in flagged_keys or int(hashlib.sha256("|".join(key).encode()).hexdigest()[:8], 16) % 50 == 0
        if selected:
            review_rows.append({"review_id": hashlib.sha256("|".join(key).encode()).hexdigest()[:16], "measure": row["measure"], "component": row["component"], "profile_id": row["profile_id"], "frame_index": row["frame_index"], "value_hz": row["value_hz"], "flagged": key in flagged_keys, "source_condition_hidden": True, "review_decision": "unreviewed", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
    write_tsv(output_dir / "review_sample.tsv", review_rows, ["review_id", "measure", "component", "profile_id", "frame_index", "value_hz", "flagged", "source_condition_hidden", "review_decision", "data_status"])
    gates = [{"measure": measure, "status": "review_required" if any(row["measure"] == measure for row in flag_rows) else "accept_fixture_only", "scope": "synthetic teaching fixture", "decision_basis": "signal-level flags before outcome analysis"} for measure in ("f0", "formant")]
    (output_dir / "measurement_gate.json").write_text(json.dumps(gates, indent=2), encoding="utf-8")
    provenance = {"tool": "phonetic_research_companion.ch10.run_pitch_and_formant_qc", "tool_version": __version__, "numpy_version": np.__version__, "run_at_utc": datetime.now(timezone.utc).isoformat(), "input_hashes": {str(path.resolve()): sha256_file(path) for path in (source_manifest_path, interval_manifest_path, specification_path)}, "source_hashes": {row["file_id"]: row["sha256"] for row in sources}}
    (output_dir / "run_provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return {"raw": raw_rows, "flags": flag_rows, "summaries": summaries, "review": review_rows, "gates": gates}


def run_duration_validation(automatic_path: Path, reference_path: Path, validation_manifest_path: Path, correction_path: Path, output_dir: Path) -> dict[str, Any]:
    raw_hash_before = sha256_file(automatic_path)
    automatic = read_tsv(automatic_path)
    references = {row["observation_id"]: row for row in read_tsv(reference_path)}
    validation = {row["observation_id"]: row for row in read_tsv(validation_manifest_path)}
    corrections = {row["observation_id"]: row for row in read_tsv(correction_path)}
    if not all(row.get("data_status") == "SYNTHETIC_TEACHING_FIXTURE" for row in automatic + list(references.values()) + list(validation.values()) + list(corrections.values())):
        raise ValueError("Bundled duration fixtures must remain explicitly synthetic")
    if len({row["observation_id"] for row in automatic}) != len(automatic):
        raise ValueError("Automatic measurement observation_id must be unique")
    validation_rows: list[dict[str, Any]] = []
    analysis_rows: list[dict[str, Any]] = []
    normalized_corrections: list[dict[str, Any]] = []
    for row in automatic:
        observation_id = row["observation_id"]
        if observation_id not in references or observation_id not in validation:
            raise ValueError(f"Missing reference or validation record for {observation_id}")
        reference = references[observation_id]
        auto_onset = float(row["automatic_onset_ms"]) if row["automatic_onset_ms"] else None
        auto_offset = float(row["automatic_offset_ms"]) if row["automatic_offset_ms"] else None
        ref_onset = float(reference["reference_onset_ms"])
        ref_offset = float(reference["reference_offset_ms"])
        onset_error = None if auto_onset is None else auto_onset - ref_onset
        offset_error = None if auto_offset is None else auto_offset - ref_offset
        automatic_duration = None if auto_onset is None or auto_offset is None else auto_offset - auto_onset
        reference_duration = ref_offset - ref_onset
        duration_error = None if automatic_duration is None else automatic_duration - reference_duration
        duration_bin = "short" if reference_duration < 90 else ("medium" if reference_duration < 140 else "long")
        validation_rows.append({"observation_id": observation_id, "speaker_id": row["speaker_id"], "context": row["context"], "duration_bin": duration_bin, "automatic_onset_ms": "" if auto_onset is None else auto_onset, "reference_onset_ms": ref_onset, "onset_error_ms": "" if onset_error is None else onset_error, "absolute_onset_error_ms": "" if onset_error is None else abs(onset_error), "automatic_offset_ms": "" if auto_offset is None else auto_offset, "reference_offset_ms": ref_offset, "offset_error_ms": "" if offset_error is None else offset_error, "absolute_offset_error_ms": "" if offset_error is None else abs(offset_error), "automatic_duration_ms": "" if automatic_duration is None else automatic_duration, "reference_duration_ms": reference_duration, "duration_error_ms": "" if duration_error is None else duration_error, "absolute_duration_error_ms": "" if duration_error is None else abs(duration_error), "extractor_status": row["extractor_status"], "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
        analysis_onset, analysis_offset = auto_onset, auto_offset
        correction_applied, reason = False, ""
        if observation_id in corrections:
            correction = corrections[observation_id]
            if not correction.get("reason_code"):
                raise ValueError(f"Correction lacks reason_code: {observation_id}")
            analysis_onset = float(correction["corrected_onset_ms"]) if correction["corrected_onset_ms"] else analysis_onset
            analysis_offset = float(correction["corrected_offset_ms"]) if correction["corrected_offset_ms"] else analysis_offset
            correction_applied, reason = True, correction["reason_code"]
            normalized_corrections.append({"observation_id": observation_id, "raw_onset_ms": "" if auto_onset is None else auto_onset, "raw_offset_ms": "" if auto_offset is None else auto_offset, "corrected_onset_ms": analysis_onset, "corrected_offset_ms": analysis_offset, "correction_action": correction["correction_action"], "reason_code": reason, "reviewer_code": correction["reviewer_code"], "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
        analysis_rows.append({"observation_id": observation_id, "speaker_id": row["speaker_id"], "context": row["context"], "raw_onset_ms": "" if auto_onset is None else auto_onset, "raw_offset_ms": "" if auto_offset is None else auto_offset, "analysis_onset_ms": "" if analysis_onset is None else analysis_onset, "analysis_offset_ms": "" if analysis_offset is None else analysis_offset, "analysis_duration_ms": "" if analysis_onset is None or analysis_offset is None else analysis_offset - analysis_onset, "correction_applied": correction_applied, "reason_code": reason, "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
    output_dir.mkdir(parents=True, exist_ok=True)
    validation_fields = list(validation_rows[0])
    write_tsv(output_dir / "duration_validation.tsv", validation_rows, validation_fields)
    write_tsv(output_dir / "measurement_corrections.tsv", normalized_corrections, ["observation_id", "raw_onset_ms", "raw_offset_ms", "corrected_onset_ms", "corrected_offset_ms", "correction_action", "reason_code", "reviewer_code", "data_status"])
    write_tsv(output_dir / "analysis_measurements.tsv", analysis_rows, list(analysis_rows[0]))
    summaries = []
    for context in sorted({row["context"] for row in validation_rows}):
        subset = [row for row in validation_rows if row["context"] == context]
        onset = [float(row["absolute_onset_error_ms"]) for row in subset if row["absolute_onset_error_ms"] != ""]
        offset = [float(row["absolute_offset_error_ms"]) for row in subset if row["absolute_offset_error_ms"] != ""]
        duration = [float(row["absolute_duration_error_ms"]) for row in subset if row["absolute_duration_error_ms"] != ""]
        summaries.append({"context": context, "n": len(subset), "median_absolute_onset_error_ms": float(np.median(onset)), "median_absolute_offset_error_ms": float(np.median(offset)), "median_absolute_duration_error_ms": float(np.median(duration)), "missing_duration": sum(row["automatic_duration_ms"] == "" for row in subset)})
    shifted_accurate = [row for row in validation_rows if row["onset_error_ms"] != "" and row["offset_error_ms"] != "" and abs(float(row["onset_error_ms"])) >= 10 and abs(float(row["offset_error_ms"])) >= 10 and abs(float(row["duration_error_ms"])) <= 2]
    report = "<!doctype html><meta charset='utf-8'><title>Duration diagnostics</title><h1>Duration diagnostics</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Errors are generated for method instruction and do not estimate an automatic aligner.</p>" + _html_table(summaries, ["context", "n", "median_absolute_onset_error_ms", "median_absolute_offset_error_ms", "median_absolute_duration_error_ms", "missing_duration"]) + f"<p>Cases with two boundaries shifted by at least 10 ms but duration error no greater than 2 ms: {len(shifted_accurate)}.</p>"
    (output_dir / "duration_diagnostics.html").write_text(report, encoding="utf-8")
    raw_hash_after = sha256_file(automatic_path)
    if raw_hash_before != raw_hash_after:
        raise RuntimeError("Raw automatic measurement file changed during correction processing")
    provenance = {"tool": "phonetic_research_companion.ch10.run_duration_validation", "tool_version": __version__, "run_at_utc": datetime.now(timezone.utc).isoformat(), "input_hashes": {str(path.resolve()): sha256_file(path) for path in (automatic_path, reference_path, validation_manifest_path, correction_path)}, "raw_automatic_sha256_before": raw_hash_before, "raw_automatic_sha256_after": raw_hash_after, "raw_unchanged": True}
    (output_dir / "run_provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return {"validation": validation_rows, "corrections": normalized_corrections, "analysis": analysis_rows, "summaries": summaries, "shifted_accurate": shifted_accurate, "raw_unchanged": True}
