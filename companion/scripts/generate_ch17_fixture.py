#!/usr/bin/env python3
"""Generate explicitly synthetic Chapter 17 regression fixtures."""
from __future__ import annotations

import csv
import hashlib
import math
import random
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "companion" / "data"
CHAPTER_ROOT = DATA_ROOT / "ch17" / "synthetic_regression"
STATUS = "SYNTHETIC_TEACHING_FIXTURE"
SEED = 17042026


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rng = random.Random(SEED)
    CHAPTER_ROOT.mkdir(parents=True, exist_ok=True)
    speakers = [f"SYN_SPK_{i:02d}" for i in range(1, 25)]
    items = [f"SYN_ITEM_{i:02d}" for i in range(1, 19)]
    conditions = ["BASE", "SHIFT_A", "SHIFT_B"]
    speaker_intercepts = {s: rng.gauss(0, 3.2) for s in speakers}
    speaker_slopes_a = {s: rng.gauss(0, 1.1) for s in speakers}
    speaker_slopes_b = {s: rng.gauss(0, 0.9) for s in speakers}
    item_effects = {item: rng.gauss(0, 1.7) for item in items}
    rows: list[dict] = []
    index = 0
    for speaker_index, speaker in enumerate(speakers):
        speaker_rate = rng.gauss(0, 0.45)
        for item_index, item in enumerate(items):
            for condition in conditions:
                index += 1
                raw_rate = 4.6 + speaker_rate + 0.12 * (condition == "SHIFT_B") + rng.gauss(0, 0.34)
                condition_effect = {"BASE": 0.0, "SHIFT_A": 5.4, "SHIFT_B": -2.8}[condition]
                slope_effect = 0.0
                if condition == "SHIFT_A":
                    slope_effect = speaker_slopes_a[speaker]
                elif condition == "SHIFT_B":
                    slope_effect = speaker_slopes_b[speaker]
                outcome = 102 + speaker_intercepts[speaker] + item_effects[item] + condition_effect + slope_effect + 1.65 * (raw_rate - 4.6) + rng.gauss(0, 2.35)
                rows.append({
                    "observation_id": f"SYN_REG_{index:04d}",
                    "speaker_id": speaker,
                    "item_id": item,
                    "condition": condition,
                    "speaking_rate": f"{raw_rate:.6f}",
                    "outcome": f"{outcome:.6f}",
                    "recording_order": item_index * 3 + conditions.index(condition) + 1,
                    "data_status": STATUS,
                })
    mean_rate = sum(float(row["speaking_rate"]) for row in rows) / len(rows)
    sd_rate = math.sqrt(sum((float(row["speaking_rate"]) - mean_rate) ** 2 for row in rows) / (len(rows) - 1))
    for row in rows:
        row["speaking_rate_z"] = f"{(float(row['speaking_rate']) - mean_rate) / sd_rate:.8f}"
    fields = ["observation_id", "speaker_id", "item_id", "condition", "speaking_rate", "speaking_rate_z", "outcome", "recording_order", "data_status"]
    write_tsv(CHAPTER_ROOT / "analysis_data.tsv", rows, fields)

    adverse = [dict(rows[0]), dict(rows[0])]
    adverse[0]["observation_id"] = "SYN_ADVERSE_DUP"
    adverse[1]["observation_id"] = "SYN_ADVERSE_DUP"
    for j, condition in enumerate(["BASE", "BASE", "SHIFT_A"], start=1):
        row = dict(rows[j + 10])
        row.update(observation_id=f"SYN_ADVERSE_SPARSE_{j}", speaker_id="SYN_SPK_SPARSE", condition=condition)
        adverse.append(row)
    write_tsv(CHAPTER_ROOT / "adverse_cases.tsv", adverse, fields)

    schema = {
        "schema_version": "1.0",
        "data_status": STATUS,
        "primary_key": ["observation_id"],
        "required_fields": fields,
        "types": {"outcome": "finite_number", "speaking_rate_z": "finite_number", "condition": "factor"},
        "factor_levels": {"condition": conditions},
        "support_rules": {"minimum_observations_per_speaker_condition_for_random_slope": 2},
    }
    (CHAPTER_ROOT / "analysis_schema.yaml").write_text(yaml.safe_dump(schema, sort_keys=False), encoding="utf-8")
    spec = {
        "schema_version": "1.0",
        "data_status": STATUS,
        "seed": SEED,
        "estimand": {
            "outcome": "synthetic continuous acoustic response",
            "observation_unit": "speaker-item-condition token",
            "target_population": "the generated speaker population and the 18 observed synthetic items",
            "focal_contrast": "marginal mean SHIFT_A minus BASE, averaged equally over observed items at speaking_rate_z = 0",
            "averaging_distribution": "equal weight over the 18 observed items",
            "purpose": "explanatory teaching example",
            "new_unit_scope": {"speakers": "supported only if a speaker random-effects model passes diagnostics", "items": "not supported; items are fixed blocking factors in the available nlme implementation"},
        },
        "outcome_family": {"family": "Gaussian", "link": "identity"},
        "predictors": {"condition": {"levels": conditions, "reference": "BASE"}, "speaking_rate_z": {"center": mean_rate, "scale": sd_rate}},
        "grouping": {"conceptual_design": "speakers crossed with items", "implemented_structure": "speaker random effects plus item fixed blocking effects", "engine": "nlme::lme"},
        "candidate_models": [
            {"model_id": "fixed_only", "random": "none"},
            {"model_id": "speaker_intercept", "random": "1 | speaker_id"},
            {"model_id": "speaker_slope", "random": "condition | speaker_id"},
        ],
        "prespecified_simplification": ["speaker_slope", "speaker_intercept", "fixed_only"],
        "diagnostics": ["residual distribution", "condition-wise residual spread", "leave-one-speaker-out influence", "predictor support and extrapolation"],
        "interpretive_constraints": ["no significance voting", "retain failed fits and warnings", "do not generalize to new items", "synthetic results are not empirical evidence"],
    }
    (CHAPTER_ROOT / "regression_analysis_spec.yaml").write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")

    contrast_rows = []
    codings = {
        "treatment_BASE": {"BASE": (0, 0), "SHIFT_A": (1, 0), "SHIFT_B": (0, 1)},
        "sum_to_zero": {"BASE": (-1, -1), "SHIFT_A": (1, 0), "SHIFT_B": (0, 1)},
        "custom_A_vs_BASE_B_vs_mean": {"BASE": (-1, -0.5), "SHIFT_A": (1, -0.5), "SHIFT_B": (0, 1)},
    }
    for coding, mapping in codings.items():
        for condition, values in mapping.items():
            contrast_rows.append({"coding_id": coding, "condition": condition, "column_1": values[0], "column_2": values[1], "data_status": STATUS})
    write_tsv(CHAPTER_ROOT / "condition_contrasts.tsv", contrast_rows, list(contrast_rows[0]))
    prediction_rows = []
    for condition in conditions:
        for rate in [-4.0, -1.5, 0.0, 1.5, 4.0]:
            prediction_rows.append({"prediction_id": f"{condition}_{rate:+.1f}", "condition": condition, "speaking_rate_z": rate, "averaging_distribution": "equal_observed_items", "data_status": STATUS})
    write_tsv(CHAPTER_ROOT / "prediction_grid.tsv", prediction_rows, list(prediction_rows[0]))
    focal = [
        {"contrast_id": "SHIFT_A_minus_BASE", "numerator": "SHIFT_A", "denominator": "BASE", "analysis_scale": "identity-link outcome units", "averaging_distribution": "equal_observed_items", "data_status": STATUS},
        {"contrast_id": "SHIFT_B_minus_BASE", "numerator": "SHIFT_B", "denominator": "BASE", "analysis_scale": "identity-link outcome units", "averaging_distribution": "equal_observed_items", "data_status": STATUS},
    ]
    write_tsv(CHAPTER_ROOT / "focal_contrasts.tsv", focal, list(focal[0]))
    analysis_manifest = [{"field": field, "role": "outcome" if field == "outcome" else "grouping" if field in {"speaker_id", "item_id"} else "predictor" if field in {"condition", "speaking_rate_z"} else "identifier_or_audit", "missing_values": 0, "data_status": STATUS} for field in fields]
    write_tsv(CHAPTER_ROOT / "analysis_manifest.tsv", analysis_manifest, list(analysis_manifest[0]))

    files = sorted(path for path in CHAPTER_ROOT.iterdir() if path.is_file())
    generated = [{
        "artifact_id": f"CH17_SYN_{index + 1:02d}",
        "relative_path": str(path.relative_to(DATA_ROOT)),
        "data_status": STATUS,
        "source": "generated locally by companion/scripts/generate_ch17_fixture.py",
        "license": "CC-BY-4.0",
        "sha256": sha256(path),
        "contains_human_data": "false",
    } for index, path in enumerate(files)]
    manifest_path = DATA_ROOT / "MANIFEST.tsv"
    preserved = []
    if manifest_path.exists():
        with manifest_path.open("r", encoding="utf-8", newline="") as source:
            preserved = [row for row in csv.DictReader(source, delimiter="\t") if not row["artifact_id"].startswith("CH17_")]
    write_tsv(manifest_path, sorted(preserved + generated, key=lambda row: row["artifact_id"]), ["artifact_id", "relative_path", "data_status", "source", "license", "sha256", "contains_human_data"])


if __name__ == "__main__":
    main()
