# Chapter 11 notebook specification

**Primary language:** R

**Implementation status:** Both specified R notebooks are implemented with 1,080 synthetic tokens, 3,240 requested measures retained through failure, signed-VOT handling, contextual coverage, prespecified training/evaluation membership, unequal vowel inventories, four transformation layers, bootstrap parameter stability, exact reconstruction, and raw-file hash preservation. They pass the Chapter 11 test and clean Rscript runner.

Chapter 11 separates raw segmental measurement from speaker normalization. Both notebooks use synthetic or openly licensed data by default, preserve raw measurements, and require a declared estimand before transformations are compared.

## `01_segmental_measure_audit.ipynb`

This notebook reconstructs VOT, closure, vowel-duration, formant, and fricative measures from stable event identifiers. It checks landmark order, absent and ambiguous events, contextual coverage, measurement flags, and consistency between stored intervals and recomputed values. It writes a row for every requested token rather than silently removing failures.

Required inputs are an event dictionary, annotation manifest, acoustic-estimate table, and `segmental_measure_manifest.tsv`. Outputs are `segmental_raw_measures.tsv`, `landmark_audit.tsv`, `coverage_by_context.tsv`, `segmental_diagnostics.html`, and `run_provenance.json`.

The notebook supports Exercises 11.1 and 11.2. It ends with a raw-measurement gate: accept, restrict, amend and rerun, or reject.

## `02_normalization_comparison.ipynb`

This notebook compares raw, log, within-speaker standardization, and an explicit vocal-tract-length-related scaling on a declared training sample. Learners define preservation and reduction targets before inspecting group outcomes. The notebook records eligibility, reference-token membership, speaker-specific parameters, resampling stability, and effects on the eligible population.

Required inputs are validated raw measures, category and context metadata, the normalization section of `segmental_measure_manifest.tsv`, and a split manifest. Outputs are `normalization_parameters.tsv`, `segmental_normalized_measures.tsv`, `normalization_stability.tsv`, `normalization_diagnostics.html`, `normalization_decision.yaml`, and `run_provenance.json`.

The notebook supports Exercises 11.3 and 11.4. It must demonstrate that normalized values can be rebuilt exactly from raw measures and recorded parameters and that raw columns remain byte-for-byte unchanged.
