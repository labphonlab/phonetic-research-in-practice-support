"""Chapter 13 coordinate, synchronization, and kinematic audits."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import yaml
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

from . import __version__


DATA_STATUS = "SYNTHETIC_TEACHING_FIXTURE"


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


def html_table(rows: list[dict[str, Any]], fields: list[str]) -> str:
    header = "".join(f"<th>{html.escape(field)}</th>" for field in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row.get(field, '')))}</td>" for field in fields) + "</tr>" for row in rows)
    return f"<table border='1'><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"


def apply_matrix(matrix: np.ndarray, x: float, y: float) -> tuple[float, float]:
    result = matrix @ np.array([x, y, 1.0])
    return float(result[0]), float(result[1])


def matrix_from_row(row: dict[str, str]) -> np.ndarray:
    return np.array([[float(row[f"m{r}{c}"]) for c in range(1, 4)] for r in range(1, 4)])


def validate_synthetic(rows: list[dict[str, str]], name: str) -> None:
    if not rows or not all(row.get("data_status") == DATA_STATUS for row in rows):
        raise ValueError(f"Bundled Chapter 13 {name} must remain explicitly synthetic")


def write_provenance(path: Path, tool: str, inputs: list[Path], decisions: dict[str, Any]) -> None:
    payload = {
        "tool": tool,
        "tool_version": __version__,
        "python_version": __import__("sys").version,
        "numpy_version": np.__version__,
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_hashes": {str(item.resolve()): sha256_file(item) for item in inputs},
        "decisions": decisions,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_coordinate_and_sync_audit(
    session_path: Path,
    stream_manifest_path: Path,
    native_path: Path,
    transform_path: Path,
    sync_event_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    native_hash_before = sha256_file(native_path)
    session = yaml.safe_load(session_path.read_text(encoding="utf-8"))
    streams = read_tsv(stream_manifest_path)
    native = read_tsv(native_path)
    transforms = read_tsv(transform_path)
    sync_events = read_tsv(sync_event_path)
    for rows, name in ((streams, "stream manifest"), (native, "native coordinates"), (transforms, "transforms"), (sync_events, "synchronization events")):
        validate_synthetic(rows, name)
    if session.get("data_status") != DATA_STATUS:
        raise ValueError("Bundled Chapter 13 session metadata must remain explicitly synthetic")

    transform_index = {(int(row["frame_index"]), row["transform_id"]): matrix_from_row(row) for row in transforms}
    coordinate_rows: list[dict[str, Any]] = []
    by_frame_sensor = {(int(row["frame_index"]), row["sensor_id"]): row for row in native}
    frames = sorted({int(row["frame_index"]) for row in native})
    reference_errors: dict[int, float] = {}
    tolerance = float(session["coordinates"]["reference_distance_tolerance_mm"])
    expected_distance = float(session["coordinates"]["reference_distance_mm"])
    stationary_errors: list[float] = []
    for frame in frames:
        ref_a = by_frame_sensor[(frame, "REF_A")]
        ref_b = by_frame_sensor[(frame, "REF_B")]
        distance = math.hypot(float(ref_b["native_x_mm"]) - float(ref_a["native_x_mm"]), float(ref_b["native_y_mm"]) - float(ref_a["native_y_mm"]))
        reference_errors[frame] = distance - expected_distance
        native_to_head = transform_index[(frame, "native_to_head")]
        head_to_anatomical = transform_index[(frame, "head_to_anatomical")]
        for sensor in ("REF_A", "REF_B", "TONGUE", "STATIONARY"):
            row = by_frame_sensor[(frame, sensor)]
            nx, ny = float(row["native_x_mm"]), float(row["native_y_mm"])
            hx, hy = apply_matrix(native_to_head, nx, ny)
            ax, ay = apply_matrix(head_to_anatomical, hx, hy)
            error = math.hypot(hx - float(row["generator_head_x_mm"]), hy - float(row["generator_head_y_mm"]))
            if sensor == "STATIONARY":
                stationary_errors.append(error)
            coordinate_rows.append({
                "frame_index": frame,
                "native_time_s": row["native_time_s"],
                "sensor_id": sensor,
                "native_x_mm": nx,
                "native_y_mm": ny,
                "head_corrected_x_mm": hx,
                "head_corrected_y_mm": hy,
                "anatomical_x_mm": ax,
                "anatomical_y_mm": ay,
                "reference_distance_error_mm": reference_errors[frame],
                "coordinate_error_mm_known_fixture": error,
                "coordinate_status": "reference_geometry_failure" if abs(reference_errors[frame]) > tolerance else "within_fixture_tolerance",
                "data_status": DATA_STATUS,
            })

    observed = [(float(row["reference_time_s"]), float(row["articulatory_time_s"]), row["event_id"]) for row in sync_events if row["event_status"] == "observed"]
    reference_times = np.array([row[0] for row in observed])
    articulatory_times = np.array([row[1] for row in observed])
    offset = float(np.median(articulatory_times - reference_times))
    offset_residuals = articulatory_times - (reference_times + offset)
    slope, intercept = np.polyfit(reference_times, articulatory_times, 1)
    drift_residuals = articulatory_times - (intercept + slope * reference_times)
    sync_models = [
        {"model_id": "single_offset", "intercept_s": offset, "slope": 1.0, "drift_ppm": 0.0, "observed_events": len(observed), "median_absolute_residual_ms": float(np.median(np.abs(offset_residuals)) * 1000), "maximum_absolute_residual_ms": float(np.max(np.abs(offset_residuals)) * 1000), "data_status": DATA_STATUS},
        {"model_id": "linear_drift", "intercept_s": float(intercept), "slope": float(slope), "drift_ppm": float((slope - 1) * 1e6), "observed_events": len(observed), "median_absolute_residual_ms": float(np.median(np.abs(drift_residuals)) * 1000), "maximum_absolute_residual_ms": float(np.max(np.abs(drift_residuals)) * 1000), "data_status": DATA_STATUS},
    ]
    residual_rows: list[dict[str, Any]] = []
    observed_map = {event_id: (reference, articulatory) for reference, articulatory, event_id in observed}
    for event in sync_events:
        if event["event_id"] not in observed_map:
            for model_id in ("single_offset", "linear_drift"):
                residual_rows.append({"event_id": event["event_id"], "model_id": model_id, "reference_time_s": event["reference_time_s"], "articulatory_time_s": "", "residual_ms": "", "event_status": event["event_status"], "data_status": DATA_STATUS})
            continue
        reference, articulatory = observed_map[event["event_id"]]
        for model_id, predicted in (("single_offset", reference + offset), ("linear_drift", intercept + slope * reference)):
            residual_rows.append({"event_id": event["event_id"], "model_id": model_id, "reference_time_s": reference, "articulatory_time_s": articulatory, "residual_ms": (articulatory - predicted) * 1000, "event_status": "observed", "data_status": DATA_STATUS})

    expected_frames = set(range(240))
    missing_frames = sorted(expected_frames - set(frames))
    drift_frames = [frame for frame, error in reference_errors.items() if abs(error) > tolerance]
    quality_rows = [
        {"stream_id": "SYN_EMA", "quality_domain": "reference_geometry", "requested_units": 240, "failed_units": len(drift_frames), "metric": "absolute_reference_distance_error_mm", "observed_value": max(abs(value) for value in reference_errors.values()), "acceptance_limit": tolerance, "decision": "restrict", "reason": "localized reference-sensor drift", "data_status": DATA_STATUS},
        {"stream_id": "SYN_EMA", "quality_domain": "frame_continuity", "requested_units": 240, "failed_units": len(missing_frames), "metric": "missing_frame_count", "observed_value": len(missing_frames), "acceptance_limit": 0, "decision": "restrict", "reason": "dropped frames retained as gaps", "data_status": DATA_STATUS},
        {"stream_id": "SYN_EMA", "quality_domain": "stationary_target", "requested_units": len(stationary_errors), "failed_units": sum(value > 1 for value in stationary_errors), "metric": "p95_head_corrected_error_mm", "observed_value": float(np.quantile(stationary_errors, 0.95)), "acceptance_limit": 1.0, "decision": "restrict", "reason": "known-fixture validation detects correction error during reference drift", "data_status": DATA_STATUS},
        {"stream_id": "SYN_AUDIO_CLOCK+SYN_EMA", "quality_domain": "synchronization", "requested_units": len(sync_events), "failed_units": sum(row["event_status"] != "observed" for row in sync_events), "metric": "linear_model_max_absolute_residual_ms", "observed_value": sync_models[1]["maximum_absolute_residual_ms"], "acceptance_limit": float(session["synchronization"]["acceptance_rule_ms"]), "decision": "accept_fixture_only", "reason": "linear drift model meets the declared residual tolerance for observed anchors; one anchor is missing", "data_status": DATA_STATUS},
    ]

    output_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(output_dir / "stream_quality.tsv", quality_rows, list(quality_rows[0]))
    write_tsv(output_dir / "coordinate_transforms.tsv", coordinate_rows, list(coordinate_rows[0]))
    write_tsv(output_dir / "sync_model.tsv", sync_models, list(sync_models[0]))
    write_tsv(output_dir / "sync_residuals.tsv", residual_rows, list(residual_rows[0]))
    report = "<!doctype html><meta charset='utf-8'><title>Coordinate and synchronization diagnostics</title><h1>Coordinate and synchronization diagnostics</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Native coordinates and timestamps remain immutable; corrected layers are derivatives.</p><h2>Stream quality</h2>" + html_table(quality_rows, list(quality_rows[0])) + "<h2>Synchronization models</h2>" + html_table(sync_models, list(sync_models[0]))
    (output_dir / "coordinate_sync_diagnostics.html").write_text(report, encoding="utf-8")
    native_hash_after = sha256_file(native_path)
    if native_hash_before != native_hash_after:
        raise RuntimeError("Native coordinate source changed during reconstruction")
    decisions = {"data_status": DATA_STATUS, "native_unchanged": True, "drift_frames": drift_frames, "missing_frames": missing_frames, "coordinate_decision": "restrict", "sync_decision": "accept_fixture_only", "interpretive_limit": "synthetic geometry and clocks do not validate a physical system"}
    write_provenance(output_dir / "run_provenance.json", "phonetic_research_companion.ch13.run_coordinate_and_sync_audit", [session_path, stream_manifest_path, native_path, transform_path, sync_event_path], decisions)
    return {"coordinates": coordinate_rows, "quality": quality_rows, "sync_models": sync_models, "sync_residuals": residual_rows, "decisions": decisions, "native_unchanged": True}


def run_kinematic_landmarks(trajectory_path: Path, profile_path: Path, stream_quality_path: Path, output_dir: Path) -> dict[str, Any]:
    trajectory_hash_before = sha256_file(trajectory_path)
    rows = read_tsv(trajectory_path)
    validate_synthetic(rows, "kinematic trajectories")
    profiles_payload = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    if profiles_payload.get("data_status") != DATA_STATUS:
        raise ValueError("Bundled Chapter 13 landmark profiles must remain explicitly synthetic")
    stream_quality = read_tsv(stream_quality_path)
    validate_synthetic(stream_quality, "stream-quality decisions")
    by_event: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_event.setdefault(row["event_id"], []).append(row)

    candidates: list[dict[str, Any]] = []
    landmarks: list[dict[str, Any]] = []
    for event_id, event_rows in sorted(by_event.items()):
        event_rows.sort(key=lambda row: int(row["sample_index"]))
        times = np.array([float(row["time_ms"]) for row in event_rows])
        values = np.array([float(row["displacement_mm"]) if row["displacement_mm"] else np.nan for row in event_rows])
        missing_fraction = float(np.mean(~np.isfinite(values)))
        valid = np.isfinite(values)
        if valid.any():
            working = np.interp(times, times[valid], values[valid])
        else:
            working = np.zeros_like(times)
        for profile in profiles_payload["profiles"]:
            profile_id = profile["profile_id"]
            filtered = gaussian_filter1d(working, float(profile["filter_sigma_samples"])) if profile["filter"] == "gaussian" else working.copy()
            velocity = np.gradient(filtered, times / 1000)
            excursion = float(np.max(filtered) - np.min(filtered))
            peak_velocity = float(np.max(velocity))
            peak_threshold = max(0.0, peak_velocity * float(profile["peak_fraction"]))
            peak_indices, properties = find_peaks(velocity, height=peak_threshold, distance=4)
            for candidate_number, index in enumerate(peak_indices, start=1):
                candidates.append({"event_id": event_id, "speaker_id": event_rows[0]["speaker_id"], "shape_class": event_rows[0]["shape_class"], "profile_id": profile_id, "candidate_id": f"{event_id}_{profile_id}_C{candidate_number:02d}", "candidate_time_ms": times[index], "candidate_velocity_mm_s": velocity[index], "threshold_mm_s": peak_threshold, "selected_by_rule": candidate_number == 1, "data_status": DATA_STATUS})
            status = "eligible"
            reason = "prespecified earliest positive velocity peak"
            onset = target = duration = ""
            target_span = 0.0
            if missing_fraction > float(profiles_payload["nonidentifiable_rules"]["maximum_missing_fraction"]):
                status, reason = "phonetic_nonidentifiability", "missing_fraction_above_limit"
            elif excursion < float(profile["minimum_excursion_mm"]):
                status, reason = "phonetic_nonidentifiability", "excursion_below_profile_minimum"
            elif len(peak_indices) == 0:
                status, reason = "software_failure", "no_positive_velocity_candidate_returned"
            else:
                selected_index = int(peak_indices[0])
                crossings = np.where(velocity[: selected_index + 1] >= peak_threshold)[0]
                onset = float(times[int(crossings[0])]) if len(crossings) else float(times[selected_index])
                near_target = np.where(filtered >= np.max(filtered) * 0.98)[0]
                target_span = float(times[near_target[-1]] - times[near_target[0]]) if len(near_target) else 0.0
                target = float(np.median(times[near_target])) if len(near_target) else float(times[int(np.argmax(filtered))])
                duration = target - onset
                if target_span > float(profiles_payload["nonidentifiable_rules"]["maximum_target_plateau_ms"]):
                    status, reason = "phonetic_nonidentifiability", "target_plateau_exceeds_limit"
                    onset = target = duration = ""
                elif len(peak_indices) > 1:
                    status, reason = "eligible_with_multiple_candidates", "all_candidates_retained; earliest_selected_by_rule"
            landmarks.append({"event_id": event_id, "speaker_id": event_rows[0]["speaker_id"], "shape_class": event_rows[0]["shape_class"], "profile_id": profile_id, "missing_fraction": missing_fraction, "excursion_mm": excursion, "candidate_count": len(peak_indices), "onset_time_ms": onset, "target_time_ms": target, "movement_duration_ms": duration, "target_plateau_span_ms": target_span, "landmark_status": status, "reason_code": reason, "data_status": DATA_STATUS})

    availability: list[dict[str, Any]] = []
    for shape in sorted({row["shape_class"] for row in landmarks}):
        for profile in sorted({row["profile_id"] for row in landmarks}):
            subset = [row for row in landmarks if row["shape_class"] == shape and row["profile_id"] == profile]
            availability.append({"shape_class": shape, "profile_id": profile, "requested_events": len(subset), "eligible_events": sum(str(row["landmark_status"]).startswith("eligible") for row in subset), "phonetic_nonidentifiability": sum(row["landmark_status"] == "phonetic_nonidentifiability" for row in subset), "software_failure": sum(row["landmark_status"] == "software_failure" for row in subset), "data_status": DATA_STATUS})
    sensitivity: list[dict[str, Any]] = []
    for event_id in sorted(by_event):
        subset = [row for row in landmarks if row["event_id"] == event_id and str(row["landmark_status"]).startswith("eligible")]
        onset_values = [float(row["onset_time_ms"]) for row in subset]
        target_values = [float(row["target_time_ms"]) for row in subset]
        duration_values = [float(row["movement_duration_ms"]) for row in subset]
        sensitivity.append({"event_id": event_id, "shape_class": by_event[event_id][0]["shape_class"], "eligible_profiles": len(subset), "onset_range_ms": max(onset_values) - min(onset_values) if onset_values else "", "target_range_ms": max(target_values) - min(target_values) if target_values else "", "duration_range_ms": max(duration_values) - min(duration_values) if duration_values else "", "claim_scope": "synthetic profile sensitivity only", "data_status": DATA_STATUS})

    coordinate_restricted = any(row["quality_domain"] in {"reference_geometry", "frame_continuity"} and row["decision"] == "restrict" for row in stream_quality)
    gate = {
        "data_status": DATA_STATUS,
        "stream_decisions": [
            {"stream_id": "SYN_EMA_coordinates", "decision": "restrict" if coordinate_restricted else "accept_fixture_only", "reason": "exclude the recorded reference-drift interval and preserve dropped-frame gaps"},
            {"stream_id": "SYN_EMA_kinematics", "decision": "restrict", "reason": "eligibility depends on trajectory shape and prespecified landmark profile"},
            {"stream_id": "SYN_AUDIO_CLOCK+SYN_EMA", "decision": "accept_fixture_only", "reason": "linear-drift residuals meet the synthetic tolerance for observed anchors"},
        ],
        "combined_decision": "restrict",
        "claim_restrictions": ["synthetic fixtures do not validate a physical instrument", "exclude reference-drift and dropped-frame intervals", "do not coerce nonidentifiable landmarks into numeric values", "report profile-dependent eligible populations"],
        "one_global_reliability_label_permitted": False,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(output_dir / "kinematic_candidates.tsv", candidates, list(candidates[0]))
    write_tsv(output_dir / "kinematic_landmarks.tsv", landmarks, list(landmarks[0]))
    write_tsv(output_dir / "landmark_availability.tsv", availability, list(availability[0]))
    write_tsv(output_dir / "landmark_sensitivity.tsv", sensitivity, list(sensitivity[0]))
    report = "<!doctype html><meta charset='utf-8'><title>Kinematic landmark diagnostics</title><h1>Kinematic landmark diagnostics</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Candidate retention and nonidentifiability rules are instructional and do not estimate performance on human movement.</p><h2>Availability</h2>" + html_table(availability, list(availability[0])) + "<h2>Profile sensitivity</h2>" + html_table(sensitivity, list(sensitivity[0]))
    (output_dir / "kinematic_diagnostics.html").write_text(report, encoding="utf-8")
    (output_dir / "multimodal_gate.yaml").write_text(yaml.safe_dump(gate, sort_keys=False), encoding="utf-8")
    trajectory_hash_after = sha256_file(trajectory_path)
    if trajectory_hash_before != trajectory_hash_after:
        raise RuntimeError("Validated trajectory source changed during landmark analysis")
    write_provenance(output_dir / "run_provenance.json", "phonetic_research_companion.ch13.run_kinematic_landmarks", [trajectory_path, profile_path, stream_quality_path], {"raw_unchanged": True, "gate": gate})
    return {"candidates": candidates, "landmarks": landmarks, "availability": availability, "sensitivity": sensitivity, "gate": gate, "raw_unchanged": True}
