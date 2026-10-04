# Chapter 15 notebook specification and implementation record

**Primary language:** Python

Chapter 15 treats a corpus as a documented sampling mechanism rather than a neutral container of tokens. The notebooks preserve the complete route from searchable universe to final analysis sample. Any included example corpus must be openly redistributable or replaced with an explicitly labeled synthetic fixture; licensed recordings, transcripts, and participant identifiers remain at their canonical protected locations.

## `01_query_and_denominator_audit.ipynb`

This notebook executes a versioned corpus query and creates one candidate-manifest row for every raw hit. It validates stable identifiers, resolves duplicates without deleting their history, applies context and signal-availability rules, imports measurement and quality-review outcomes, and reports every transition from raw hit to final inclusion. Counts are produced both globally and by speaker, item, session, conversation, and condition so that differential attrition cannot hide behind a corpus-wide total.

Required inputs are `corpus_sample_manifest.tsv`, a corpus-access profile, query configuration, corpus and annotation versions, linkage tables, and the relevant measurement-validation outputs. Outputs are `query_run.json`, `candidate_manifest.tsv`, `token_flow.tsv`, `attrition_by_domain.tsv`, `linkage_audit.tsv`, `selection_diagnostics.html`, and `run_provenance.json`.

The notebook supports Exercises 15.1–15.3. A protected-data profile may resolve canonical corpus paths internally, while the public profile uses a permitted fixture with the same schema and test cases.

## `02_representativeness_and_cross_corpus.ipynb`

This notebook evaluates whether the analysis sample supports the intended population and domain. It compares target-population dimensions with corpus design and observed sample support, visualizes imbalance across higher-level units, identifies unsupported cells, and constructs a cross-corpus compatibility table for population, era, task, style, recording, annotation, lexical coverage, and measurement procedure. Weighting or restriction is demonstrated only where the required target margins and overlap exist.

Required inputs are the frozen candidate manifest, target-population specification, corpus-design metadata, external population margins where authorized and justified, and cross-corpus harmonization maps. Outputs are `population_support.tsv`, `higher_level_support.tsv`, `compatibility_table.tsv`, `unsupported_domains.tsv`, `corpus_inference_gate.yaml`, `representativeness_report.html`, and `run_provenance.json`.

The notebook supports Exercises 15.1 and 15.4. It cannot certify that a corpus is representative in the abstract; it records the dimensions and claims for which support is adequate, restricted, or absent.

## Implementation status

Both notebooks, the seven-artifact synthetic corpus fixture, the reusable Python module, four automated tests, and the clean local execution route are implemented. The query notebook preserves 640 raw hit rows, retains forty duplicate records with links to the first candidate, reconstructs 600 unique source tokens, and records every transition to 440 final inclusions. Attrition is reported globally and by corpus, speaker, item, session, conversation, and condition. Ambiguous and unmatched lexical links remain reason-coded in the denominator, and the searchable-hit source hash is unchanged.

The representativeness notebook evaluates ten generated target cells and higher-level support. It identifies the absent central-region and read-speech cells and records incompatible era and recording domains in the cross-corpus table. Because the target margins are illustrative rather than authorized population margins, weighting is prohibited. The inference gate is `restrict` and explicitly states that the synthetic fixture is not population evidence.

The fixture is regenerated with `python3 companion/scripts/generate_ch15_fixture.py`, the notebooks with `python3 companion/scripts/build_ch15_notebooks.py`, and the tests with `python3 -m unittest companion/tests/test_ch15.py -v`. Both notebooks pass the clean Python runner in the recorded local environment; Colab, cross-platform, and continuous-integration verification remain open under P-001.
