# Chapter 16 notebook specification and implementation record

**Primary language:** Python

Chapter 16 turns the book's evidential chain into an executable dependency graph. The notebooks are teaching and inspection interfaces, not the sole implementation of the workflow. Reusable logic belongs in tested modules or workflow rules, and each notebook must execute in a clean kernel against declared inputs.

## `01_pipeline_graph_and_data_contracts.ipynb`

This notebook reads `pipeline_spec.yaml`, validates its schema, and renders the path from immutable source manifests through queries, measurements, review decisions, analysis tables, models, figures, and claim artifacts. It checks identifier uniqueness, declared join cardinality, expected schemas, configuration units, input hashes, and the distinction among protected inputs, permitted derivatives, and public fixtures. A deliberately defective fixture demonstrates how duplicate keys, silent defaults, and direct edits to generated data are detected.

Required inputs are `pipeline_spec.yaml`, data schemas, source manifests, correction tables, and small permitted or synthetic fixtures. Outputs are `pipeline_graph.svg`, `contract_validation.tsv`, `join_audit.tsv`, `configuration_resolved.yaml`, `scientific_invariants.tsv`, and `run_provenance.json`.

The notebook supports Exercises 16.1–16.3. It explains each validation failure but delegates canonical transformation logic to the companion package rather than redefining it in cells.

## `02_clean_run_and_reproduction.ipynb`

This notebook launches or inspects a clean reference run with derived-data directories empty and stale caches disabled or independently verified. It compares regenerated artifacts with a verified manifest, applies exact or declared numerical tolerances, checks scientific invariants and privacy allowlists, and distinguishes exact, numerical, and substantive reproduction. Protected and public profiles use the same transformation code while resolving different authorized inputs.

Required inputs are the resolved pipeline specification, environment lockfile, workflow entry point, expected-artifact manifest, tolerance policy, and protected or public access profile. Outputs are `clean_run_summary.json`, `artifact_comparison.tsv`, `test_report.xml`, `privacy_scan.tsv`, `reproduction_assessment.yaml`, `verified_artifact_manifest.tsv`, and `run_provenance.json`.

The notebook supports Exercise 16.4. A successful run means that the declared inputs and decisions regenerated all required artifacts and passed their gates; it does not by itself establish that the study's scientific interpretation is warranted.

## Implementation status

Both notebooks, the twelve-artifact synthetic pipeline fixture, the reusable Python module, three automated tests, and the clean local execution route are implemented. The contract notebook renders an explicit dependency graph, materializes configuration defaults, verifies canonical schemas and joins, and confirms that duplicate keys, negative intervals, and missing required values fail as designed. The immutable source hash is preserved, and the protected route remains configuration-only without accessing or copying protected data.

The clean-run notebook regenerates an eleven-row public analysis table and summary from empty output state. The analysis table matches its reviewed reference byte-for-byte, the summary matches within the declared numerical tolerance, the failed source measurement remains absent, and every public table field passes the allowlist. The assessment distinguishes exact, numerical, substantive, privacy, and interpretive claims: the public fixture passes the first four gates but does not warrant a scientific interpretation or reproduce a protected-data result.

The fixture is regenerated with `python3 companion/scripts/generate_ch16_fixture.py`, the notebooks with `python3 companion/scripts/build_ch16_notebooks.py`, and the tests with `python3 -m unittest companion/tests/test_ch16.py -v`. Both notebooks pass the clean Python runner in the recorded local environment; Colab, cross-platform, protected-infrastructure, and continuous-integration verification remain open under P-001.
