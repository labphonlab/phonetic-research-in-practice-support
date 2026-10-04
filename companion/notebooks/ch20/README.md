# Chapter 20 notebook specification

**Primary language:** Python

Chapter 20 assembles and audits a reproducible release without treating public access as permission to redistribute speech data. The notebooks operate on explicit allowlists and access profiles. They never copy protected source recordings, transcripts, credentials, or participant identifiers into the public candidate.

## `01_release_manifest_and_privacy_audit.ipynb`

This notebook inventories research objects and validates owner, version, role, source or generator, checksum, license, access class, citation, and intended disposition. It builds a candidate directory from the allowlist, then scans file content and metadata for identifiers, secrets, private paths, unapproved media, stale notebook outputs, and incompatible licenses. Human governance review decisions are imported as signed or attributable records rather than inferred from filenames.

Required inputs are `release_spec.yaml`, `release_manifest.tsv`, license matrix, governance decision register, citation metadata, protected/public profiles, and the clean-run artifact manifest. Outputs are `release_candidate_manifest.tsv`, `checksum_manifest.txt`, `license_audit.tsv`, `privacy_scan.tsv`, `human_review.tsv`, `release_exclusions.tsv`, and `run_provenance.json`.

The notebook supports Exercises 20.1–20.3. Synthetic fixtures are marked in their own metadata and cannot be relabeled as participant observations.

## `02_clean_release_and_archive.ipynb`

This notebook executes the public route from an empty derived-data directory in the locked environment, verifies expected outputs and tolerances, renders notebooks cleanly, and compares the availability statement with the actual manifest. It prepares archival metadata for a version-specific release and a concept-level project identifier without depositing, publishing, or registering anything. External release remains an explicit author and publisher action.

Required inputs are the verified release candidate, `release_spec.yaml`, public workflow profile, environment locks, expected-artifact manifest, citation records, availability-statement template, and maintenance policy. Outputs are `public_clean_run.json`, `artifact_verification.tsv`, `availability_statement.md`, `archive_metadata.json`, `maintenance_and_withdrawal.md`, `reproducible_release_gate.yaml`, and `run_provenance.json`.

The notebook supports Exercises 20.3 and 20.4. A passing package is technically and scientifically prepared for an authorized release decision; it is not evidence that a deposit or public launch has occurred.
