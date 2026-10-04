# Chapter 8 notebook specification

**Primary language:** R

**Implementation status:** Both specified R notebooks are implemented as valid notebook files, use explicitly synthetic trial-level fixtures and generated tone assets, and pass the repository's clean Rscript runner and Chapter 8 test suite. The analysis preserves participant and item rows, validates stimulus hashes, and writes declared outputs. Colab and cross-platform verification remain part of P-001.

Chapter 8 uses synthetic trial-level responses and openly redistributable stimuli. The notebooks retain participant and item structure and never begin from condition-level percentages.

## `01_psychometric_functions.ipynb`

This notebook validates a stimulus and trial manifest, visualizes individual and group response functions, fits a trial-level binary-response model, reports the model's probability definition, and compares location and slope summaries with uncertainty. Learners vary continuum sampling, lapse assumptions, and pooling to see which conclusions are design-dependent.

Required inputs are `perception_trial_manifest.tsv`, `stimulus_manifest.tsv`, and synthetic response data. Outputs are `psychometric_parameters.tsv`, `psychometric_diagnostics.html`, `analysis_decisions.yaml`, and `run_provenance.json`. The notebook must flag nonmonotonic or poorly supported functions rather than forcing a threshold for every participant.

The notebook supports Exercises 8.1 and 8.2. Its assessment distinguishes the observed classification function from claims about categorical perception.

## `02_signal_detection_and_rt.ipynb`

This notebook constructs hit, false-alarm, miss, and correct-rejection counts from event-level data; calculates sensitivity and criterion under declared corrections; plots condition-specific response-time distributions; and compares conclusions from accuracy alone with joint accuracy–time evidence. Timing fields retain the event used as time zero.

Required inputs are an event log following the chapter schema and a decision file defining trial types, correctness, response-time origin, and exclusions. Outputs are `signal_detection_summary.tsv`, `reaction_time_diagnostics.html`, `excluded_events.tsv`, `analysis_decisions.yaml`, and `run_provenance.json`.

The notebook supports Exercises 8.3 and 8.4. Learners must state whether a condition changes sensitivity, criterion, speed, accuracy, or an unresolved combination.
