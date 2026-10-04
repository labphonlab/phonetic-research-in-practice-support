#!/usr/bin/env python3
"""Generate explicitly synthetic Chapter 11 segmental-measure fixtures."""

from __future__ import annotations

import csv
import hashlib
import math
import random
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "companion" / "data"
CHAPTER_ROOT = DATA_ROOT / "ch11" / "synthetic_segmental"
SEED = 11042026


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rng = random.Random(SEED)
    CHAPTER_ROOT.mkdir(parents=True, exist_ok=True)
    event_dictionary = {
        "schema_version": "0.1",
        "data_status": "SYNTHETIC_TEACHING_FIXTURE",
        "events": {
            "closure_start_s": "first sustained reduction in oral airflow proxy before stop release",
            "release_s": "selected primary release when multiple release candidates exist",
            "voicing_onset_s": "first sustained periodic cycle after release",
            "vowel_onset_s": "first interval meeting the synthetic vowel-onset rule",
            "vowel_offset_s": "last interval meeting the synthetic vowel-offset rule",
            "fricative_start_s": "first sustained aperiodic interval",
            "fricative_end_s": "end of sustained aperiodic interval",
        },
        "difficult_cases": ["multiple_release", "incomplete_closure", "absent_periodicity", "no_steady_state"],
        "interpretive_limit": "generated event times are not annotations of speech",
    }
    (CHAPTER_ROOT / "event_dictionary.yaml").write_text(yaml.safe_dump(event_dictionary, sort_keys=False), encoding="utf-8")

    annotations: list[dict[str, object]] = []
    acoustics: list[dict[str, object]] = []
    requests: list[dict[str, object]] = []
    splits: list[dict[str, object]] = []
    vowel_targets = {"i": (300, 2300, 3000), "a": (750, 1200, 2500), "u": (350, 900, 2200)}
    observation_number = 0
    for speaker_index in range(1, 31):
        speaker = f"SYN_SEG_SPK_{speaker_index:02d}"
        split = "training" if speaker_index <= 20 else "evaluation"
        inventory = "i,a,u" if speaker_index not in (4, 9, 17) else "i,a"
        splits.append({"speaker_id": speaker, "split": split, "reference_inventory": inventory, "selection_rule": "speaker index <=20 assigned to training before inspection", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
        scale = rng.uniform(0.86, 1.18)
        session_base = speaker_index * 100.0
        for token_class in ("stop", "vowel", "fricative"):
            token_repetitions = 12
            for repetition in range(1, token_repetitions + 1):
                observation_number += 1
                token_id = f"SYN_SEG_{observation_number:04d}"
                context = ["initial", "medial", "final"][(repetition - 1) % 3]
                row: dict[str, object] = {"token_id": token_id, "speaker_id": speaker, "session_id": f"SYN_SESSION_{speaker_index:02d}", "token_class": token_class, "context_id": context, "vowel_category": "", "closure_start_s": "", "release_s": "", "voicing_onset_s": "", "vowel_onset_s": "", "vowel_offset_s": "", "fricative_start_s": "", "fricative_end_s": "", "annotation_status": "ok", "ambiguity_code": "", "data_status": "SYNTHETIC_TEACHING_FIXTURE"}
                acoustic = {"token_id": token_id, "f0_vowel_onset_hz": "", "f1_hz": "", "f2_hz": "", "f3_hz": "", "fricative_cog_hz": "", "estimate_status": "ok", "data_status": "SYNTHETIC_TEACHING_FIXTURE"}
                base = session_base + repetition
                if token_class == "stop":
                    closure = base
                    release = closure + rng.uniform(0.045, 0.110)
                    vot = rng.uniform(-0.020, 0.085)
                    row.update({"closure_start_s": round(closure, 6), "release_s": round(release, 6), "voicing_onset_s": round(release + vot, 6), "vowel_onset_s": round(release + max(vot, 0.005), 6)})
                    acoustic["f0_vowel_onset_hz"] = round((115 + 28 * (vot > 0.035) + rng.gauss(0, 6)) / math.sqrt(scale), 3)
                    if observation_number % 97 == 0:
                        row["voicing_onset_s"] = ""
                        row["annotation_status"] = "missing"
                        row["ambiguity_code"] = "absent_periodicity"
                    if observation_number % 89 == 0:
                        row["ambiguity_code"] = "multiple_release"
                    for measure in ("vot", "closure_duration", "vowel_onset_f0"):
                        requests.append({"observation_id": f"REQ_{token_id}_{measure}", "source_id": "SYN_CH11", "speaker_id": speaker, "session_id": row["session_id"], "token_id": token_id, "measure_id": measure, "context_id": context, "landmark_start_s": "", "landmark_end_s": "", "raw_value": "", "raw_unit": "ms" if measure != "vowel_onset_f0" else "Hz", "quality_status": "requested", "missingness_code": "", "reference_sample_id": "", "transformation_id": "raw", "reference_center": "", "reference_scale": "", "transformed_value": "", "transformed_unit": "", "provenance_id": "SYN_GENERATOR_11042026", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
                elif token_class == "vowel":
                    category = ("i", "a", "u")[(repetition - 1) % 3]
                    if speaker_index in (4, 9, 17) and category == "u":
                        category = "a"
                    onset = base
                    offset = onset + rng.uniform(0.075, 0.220)
                    row.update({"vowel_category": category, "vowel_onset_s": round(onset, 6), "vowel_offset_s": round(offset, 6)})
                    f1, f2, f3 = vowel_targets[category]
                    acoustic.update({"f1_hz": round(f1 * scale + rng.gauss(0, 22), 3), "f2_hz": round(f2 * scale + rng.gauss(0, 45), 3), "f3_hz": round(f3 * scale + rng.gauss(0, 55), 3)})
                    if observation_number % 113 == 0:
                        row["vowel_offset_s"] = ""
                        row["annotation_status"] = "missing"
                        row["ambiguity_code"] = "no_steady_state"
                    for measure in ("vowel_duration", "f1", "f2", "f3"):
                        requests.append({"observation_id": f"REQ_{token_id}_{measure}", "source_id": "SYN_CH11", "speaker_id": speaker, "session_id": row["session_id"], "token_id": token_id, "measure_id": measure, "context_id": context, "landmark_start_s": "", "landmark_end_s": "", "raw_value": "", "raw_unit": "ms" if measure == "vowel_duration" else "Hz", "quality_status": "requested", "missingness_code": "", "reference_sample_id": split, "transformation_id": "raw", "reference_center": "", "reference_scale": "", "transformed_value": "", "transformed_unit": "", "provenance_id": "SYN_GENERATOR_11042026", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
                else:
                    start = base
                    end = start + rng.uniform(0.070, 0.180)
                    row.update({"fricative_start_s": round(start, 6), "fricative_end_s": round(end, 6)})
                    acoustic["fricative_cog_hz"] = round((6200 if context == "initial" else 4800) * scale + rng.gauss(0, 240), 3)
                    for measure in ("fricative_duration", "fricative_cog"):
                        requests.append({"observation_id": f"REQ_{token_id}_{measure}", "source_id": "SYN_CH11", "speaker_id": speaker, "session_id": row["session_id"], "token_id": token_id, "measure_id": measure, "context_id": context, "landmark_start_s": "", "landmark_end_s": "", "raw_value": "", "raw_unit": "ms" if measure == "fricative_duration" else "Hz", "quality_status": "requested", "missingness_code": "", "reference_sample_id": "", "transformation_id": "raw", "reference_center": "", "reference_scale": "", "transformed_value": "", "transformed_unit": "", "provenance_id": "SYN_GENERATOR_11042026", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
                annotations.append(row)
                acoustics.append(acoustic)
    write_tsv(CHAPTER_ROOT / "annotation_manifest.tsv", annotations, list(annotations[0]))
    write_tsv(CHAPTER_ROOT / "acoustic_estimates.tsv", acoustics, list(acoustics[0]))
    write_tsv(CHAPTER_ROOT / "segmental_measure_manifest.tsv", requests, list(requests[0]))
    write_tsv(CHAPTER_ROOT / "split_manifest.tsv", splits, list(splits[0]))

    files = sorted(path for path in CHAPTER_ROOT.iterdir() if path.is_file())
    chapter_rows = [{"artifact_id": f"CH11_SYN_{index+1:02d}", "relative_path": str(path.relative_to(DATA_ROOT)), "data_status": "SYNTHETIC_TEACHING_FIXTURE", "source": "generated locally by companion/scripts/generate_ch11_fixture.py", "license": "CC-BY-4.0", "sha256": sha256_file(path), "contains_human_data": "false"} for index, path in enumerate(files)]
    global_manifest = DATA_ROOT / "MANIFEST.tsv"
    preserved: list[dict[str, str]] = []
    if global_manifest.exists():
        with global_manifest.open("r", encoding="utf-8", newline="") as source:
            preserved = [row for row in csv.DictReader(source, delimiter="\t") if not row["artifact_id"].startswith("CH11_")]
    write_tsv(global_manifest, sorted(preserved + chapter_rows, key=lambda row: row["artifact_id"]), ["artifact_id", "relative_path", "data_status", "source", "license", "sha256", "contains_human_data"])


if __name__ == "__main__":
    main()
