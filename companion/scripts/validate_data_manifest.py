#!/usr/bin/env python3
"""Validate every companion teaching-data artifact against the global manifest."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "companion" / "data"
MANIFEST = DATA_ROOT / "MANIFEST.tsv"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    with MANIFEST.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"artifact_id", "relative_path", "data_status", "source", "license", "sha256", "contains_human_data"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("The global data manifest is empty or lacks required columns")
    identifiers = [row["artifact_id"] for row in rows]
    paths = [row["relative_path"] for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Duplicate artifact_id in data manifest")
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate relative_path in data manifest")
    for row in rows:
        artifact = DATA_ROOT / row["relative_path"]
        if not artifact.is_file():
            raise FileNotFoundError(f"Manifest artifact missing: {artifact}")
        if sha256_file(artifact).lower() != row["sha256"].lower():
            raise ValueError(f"Hash mismatch: {row['artifact_id']} {artifact}")
        if row["data_status"] == "SYNTHETIC_TEACHING_FIXTURE" and row["contains_human_data"].lower() != "false":
            raise ValueError(f"Synthetic artifact cannot be marked as human data: {row['artifact_id']}")
        if not row["license"]:
            raise ValueError(f"Missing license or rights state: {row['artifact_id']}")
    print(f"PASS data manifest: {len(rows)} artifacts")


if __name__ == "__main__":
    main()
