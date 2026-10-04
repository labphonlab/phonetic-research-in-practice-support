# Chapter 10 notebook specification

**Primary language:** Python

**Implementation status:** Both specified Python notebooks are implemented with generated source-filter signals, prespecified F0 and formant profiles, long-form candidates and failures, blinded review sampling, synthetic reference landmarks, and a separate reason-coded correction layer. They pass four Chapter 10 tests and the clean Python runner. The estimators are explicitly pedagogical and are not represented as validated human-speech measurement tools.

Chapter 10 treats every acoustic output as an estimate with settings and quality evidence. Notebooks operate on synthetic or openly licensed audio by default and write a row for every requested observation, including failures.

## `01_pitch_and_formant_qc.ipynb`

This notebook runs prespecified F0 and formant settings profiles, preserves all candidates, detects missing frames, search-limit contact, abrupt jumps, formant crossings, and other risk indicators, and generates blinded review panels. Learners define a setting rule from signal-level quality rather than a group outcome plot.

Required inputs are a source manifest, interval manifest, `acoustic_measurement_spec.yaml`, and approved audio. Outputs are `raw_acoustic_estimates.tsv`, `measurement_flags.tsv`, `settings_comparison.html`, `review_sample.tsv`, and `run_provenance.json`. Source recordings and prior estimates are never overwritten.

The notebook supports Exercises 10.1 and 10.2. A completed run ends with a measure-specific gate: accept, restrict, amend and rerun, or reject.

## `02_duration_validation_and_corrections.ipynb`

This notebook compares automatic and reference onset and offset times, separates boundary error from duration error, summarizes failure by context, and creates a correction layer keyed to stable observation identifiers. It rebuilds the final analysis variable from raw values and reason-coded corrections.

Required inputs are automatic measurements, independently created reference landmarks, a validation manifest, and a correction decision file. Outputs are `duration_validation.tsv`, `duration_diagnostics.html`, `measurement_corrections.tsv`, `analysis_measurements.tsv`, and `run_provenance.json`.

The notebook supports Exercises 10.3 and 10.4. It must demonstrate that raw output is byte-for-byte unchanged after corrections are applied.
