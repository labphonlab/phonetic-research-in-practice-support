"""Chapter 7 recording-quality and metadata validation functions.

The functions in this module never modify source audio. They operate on PCM WAV
fixtures or authorized local study files and write derived audit records only.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import struct
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

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


def _pcm_samples(raw: bytes, sample_width: int) -> tuple[list[int], int]:
    if sample_width == 1:
        return [value - 128 for value in raw], 127
    if sample_width == 2:
        count = len(raw) // 2
        return list(struct.unpack(f"<{count}h", raw)), 32767
    if sample_width == 3:
        values: list[int] = []
        for position in range(0, len(raw), 3):
            chunk = raw[position : position + 3]
            unsigned = int.from_bytes(chunk, byteorder="little", signed=False)
            values.append(unsigned - (1 << 24) if unsigned & (1 << 23) else unsigned)
        return values, (1 << 23) - 1
    if sample_width == 4:
        count = len(raw) // 4
        return list(struct.unpack(f"<{count}i", raw)), (1 << 31) - 1
    raise ValueError(f"Unsupported PCM sample width: {sample_width} bytes")


def wav_properties(path: Path) -> dict[str, Any]:
    with wave.open(str(path), "rb") as source:
        channels = source.getnchannels()
        sample_width = source.getsampwidth()
        sample_rate = source.getframerate()
        frame_count = source.getnframes()
        compression = source.getcomptype()
        raw = source.readframes(frame_count)
    if compression != "NONE":
        raise ValueError(f"Only uncompressed PCM WAV is supported; found {compression}")
    samples, maximum = _pcm_samples(raw, sample_width)
    absolute = [abs(value) for value in samples]
    peak = max(absolute, default=0) / maximum
    rms = math.sqrt(sum(value * value for value in samples) / max(len(samples), 1)) / maximum
    clipped = sum(value >= maximum - 1 for value in absolute)
    return {
        "sample_rate_hz": sample_rate,
        "bit_depth": sample_width * 8,
        "channels": channels,
        "frame_count": frame_count,
        "sample_count": len(samples),
        "duration_s": frame_count / sample_rate if sample_rate else 0.0,
        "peak_normalized": peak,
        "rms_normalized": rms,
        "clipped_samples": clipped,
        "clipped_fraction": clipped / max(len(samples), 1),
    }


def _as_int(value: str, field: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field} must be an integer; found {value!r}") from error


def run_recording_qc(manifest_path: Path, output_dir: Path) -> list[dict[str, Any]]:
    """Validate a WAV manifest and emit measure-specific recording QC records."""

    required = {
        "file_id",
        "session_id",
        "source_path",
        "expected_sample_rate_hz",
        "expected_bit_depth",
        "expected_channels",
        "data_status",
    }
    rows = read_tsv(manifest_path)
    if not rows:
        raise ValueError("The recording manifest contains no records")
    missing_columns = required.difference(rows[0])
    if missing_columns:
        raise ValueError(f"Recording manifest is missing columns: {sorted(missing_columns)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for row in rows:
        source_path = (manifest_path.parent / row["source_path"]).resolve()
        record: dict[str, Any] = {
            "file_id": row["file_id"],
            "session_id": row["session_id"],
            "source_path": str(source_path),
            "data_status": row["data_status"],
            "readable": False,
            "qc_status": "fail",
            "warnings": "",
        }
        try:
            properties = wav_properties(source_path)
            record.update(properties)
            record["readable"] = True
            mismatches: list[str] = []
            if properties["sample_rate_hz"] != _as_int(row["expected_sample_rate_hz"], "expected_sample_rate_hz"):
                mismatches.append("sample_rate_mismatch")
            if properties["bit_depth"] != _as_int(row["expected_bit_depth"], "expected_bit_depth"):
                mismatches.append("bit_depth_mismatch")
            if properties["channels"] != _as_int(row["expected_channels"], "expected_channels"):
                mismatches.append("channel_count_mismatch")
            if properties["clipped_fraction"] > 0.0001:
                mismatches.append("possible_digital_clipping")
            if properties["rms_normalized"] < 0.001:
                mismatches.append("near_silent")
            record["warnings"] = ";".join(mismatches)
            record["qc_status"] = "pass" if not mismatches else "warning"
            record["usable_for_duration"] = True
            record["usable_for_relative_amplitude"] = not any(
                warning in mismatches for warning in ("possible_digital_clipping", "near_silent")
            )
            record["usable_for_spectral_measures"] = not mismatches
        except Exception as error:  # surfaced in the audit table rather than hidden
            record["warnings"] = f"read_error:{type(error).__name__}:{error}"
            record["usable_for_duration"] = False
            record["usable_for_relative_amplitude"] = False
            record["usable_for_spectral_measures"] = False
        results.append(record)

    fields = [
        "file_id",
        "session_id",
        "data_status",
        "source_path",
        "readable",
        "sample_rate_hz",
        "bit_depth",
        "channels",
        "duration_s",
        "peak_normalized",
        "rms_normalized",
        "clipped_samples",
        "clipped_fraction",
        "qc_status",
        "warnings",
        "usable_for_duration",
        "usable_for_relative_amplitude",
        "usable_for_spectral_measures",
    ]
    write_tsv(output_dir / "recording_qc.tsv", results, fields)

    header = "".join(f"<th>{html.escape(field)}</th>" for field in fields)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(record.get(field, '')))}</td>" for field in fields) + "</tr>"
        for record in results
    )
    report = (
        "<!doctype html><meta charset='utf-8'><title>Recording QC summary</title>"
        "<h1>Recording QC summary</h1>"
        "<p><strong>Teaching data:</strong> the supplied fixture is explicitly synthetic.</p>"
        f"<table border='1'><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"
    )
    (output_dir / "recording_qc_summary.html").write_text(report, encoding="utf-8")
    provenance = {
        "tool": "phonetic_research_companion.ch07.run_recording_qc",
        "tool_version": __version__,
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "manifest": str(manifest_path.resolve()),
        "manifest_sha256": sha256_file(manifest_path),
        "source_hashes": {row["file_id"]: sha256_file(Path(row["source_path"])) for row in results if row["readable"]},
        "thresholds": {"clipped_fraction": 0.0001, "near_silent_rms_normalized": 0.001},
    }
    (output_dir / "run_provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return results


def _required_metadata_values(metadata: dict[str, Any]) -> list[tuple[str, Any]]:
    return [
        ("session.session_id", metadata.get("session", {}).get("session_id")),
        ("session.protocol_version", metadata.get("session", {}).get("protocol_version")),
        ("session.consent_scope_code", metadata.get("session", {}).get("consent_scope_code")),
        ("signal_chain.microphone_model", metadata.get("signal_chain", {}).get("microphone_model")),
        ("signal_chain.mouth_distance_cm", metadata.get("signal_chain", {}).get("mouth_distance_cm")),
        ("file_configuration.sample_rate_hz", metadata.get("file_configuration", {}).get("sample_rate_hz")),
        ("file_configuration.bit_depth", metadata.get("file_configuration", {}).get("bit_depth")),
        ("pre_departure_decision.status", metadata.get("pre_departure_decision", {}).get("status")),
    ]


def _linear_timing_fit(events: list[dict[str, str]]) -> dict[str, Any]:
    expected = [float(row["expected_time_s"]) for row in events]
    observed = [float(row["observed_time_s"]) for row in events]
    if len(expected) < 2:
        raise ValueError("At least two timing events are required")
    x_mean = sum(expected) / len(expected)
    y_mean = sum(observed) / len(observed)
    denominator = sum((value - x_mean) ** 2 for value in expected)
    if denominator == 0:
        raise ValueError("Timing events require distinct expected times")
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(expected, observed)) / denominator
    intercept = y_mean - slope * x_mean
    residuals = [y - (intercept + slope * x) for x, y in zip(expected, observed)]
    return {
        "intercept_s": intercept,
        "slope": slope,
        "drift_ppm": (slope - 1.0) * 1_000_000,
        "max_absolute_residual_ms": max(abs(value) for value in residuals) * 1000,
        "residuals_s": residuals,
    }


def validate_session_metadata(
    metadata_path: Path,
    manifest_path: Path,
    timing_events_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Validate session metadata, WAV headers, and a simple timing check."""

    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise ValueError("Session metadata must contain a YAML mapping")
    manifest = read_tsv(manifest_path)
    timing_events = read_tsv(timing_events_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    deviations: list[dict[str, Any]] = []
    for field, value in _required_metadata_values(metadata):
        if value in (None, "", [], "undecided"):
            deviations.append(
                {"severity": "error", "field": field, "observed": value, "expected": "documented value", "message": "required metadata missing"}
            )

    configured = metadata.get("file_configuration", {})
    for row in manifest:
        source_path = (manifest_path.parent / row["source_path"]).resolve()
        properties = wav_properties(source_path)
        comparisons = {
            "sample_rate_hz": properties["sample_rate_hz"],
            "bit_depth": properties["bit_depth"],
            "channel_count": properties["channels"],
        }
        for field, observed in comparisons.items():
            expected = configured.get(field)
            try:
                matches = int(expected) == int(observed)
            except (TypeError, ValueError):
                matches = False
            if not matches:
                deviations.append(
                    {
                        "severity": "error",
                        "field": f"file_configuration.{field}:{row['file_id']}",
                        "observed": observed,
                        "expected": expected,
                        "message": "WAV header differs from session metadata",
                    }
                )

    expected_files = metadata.get("post_session", {}).get("expected_file_count")
    observed_files = len(manifest)
    if str(expected_files) != str(observed_files):
        deviations.append(
            {
                "severity": "error",
                "field": "post_session.expected_file_count",
                "observed": observed_files,
                "expected": expected_files,
                "message": "manifest count differs from expected file count",
            }
        )

    timing = _linear_timing_fit(timing_events)
    precision = float(metadata.get("claim_requirements", {}).get("required_timing_precision_ms") or 0)
    for row, residual in zip(timing_events, timing["residuals_s"]):
        row["residual_ms"] = residual * 1000
    if precision and timing["max_absolute_residual_ms"] > precision:
        deviations.append(
            {
                "severity": "error",
                "field": "claim_requirements.required_timing_precision_ms",
                "observed": timing["max_absolute_residual_ms"],
                "expected": f"<= {precision}",
                "message": "timing residual exceeds the claim requirement",
            }
        )

    error_count = sum(row["severity"] == "error" for row in deviations)
    normalized = {
        "schema_version": metadata.get("schema_version"),
        "validation_status": "pass" if error_count == 0 else "fail",
        "validation_note": "Internal consistency only; equipment accuracy is not certified.",
        "metadata": metadata,
        "observed_file_count": observed_files,
        "timing_fit": {key: value for key, value in timing.items() if key != "residuals_s"},
    }
    (output_dir / "validated_session_metadata.json").write_text(json.dumps(normalized, indent=2), encoding="utf-8")
    write_tsv(
        output_dir / "recording_deviations.tsv",
        deviations,
        ["severity", "field", "observed", "expected", "message"],
    )
    write_tsv(
        output_dir / "timing_check.tsv",
        timing_events,
        ["event_id", "expected_time_s", "observed_time_s", "residual_ms", "data_status"],
    )
    provenance = {
        "tool": "phonetic_research_companion.ch07.validate_session_metadata",
        "tool_version": __version__,
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            str(path.resolve()): sha256_file(path)
            for path in (metadata_path, manifest_path, timing_events_path)
        },
    }
    (output_dir / "run_provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return normalized
