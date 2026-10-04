# Chapter 12 notebook specification and implementation record

**Primary language:** R

Chapter 12 treats a trajectory as a set of requested frames, time coordinates, preprocessing decisions, and dependent observations. The notebooks use synthetic or openly licensed data and preserve the distinction among structural voicelessness, failed estimation, quality rejection, and interpolation.

## `01_pitch_trajectory_preparation.ipynb`

This notebook creates a requested-frame table, joins raw F0 candidates and selected estimates, assigns reason-coded gaps, and derives absolute, landmark-relative, and proportional time. It compares documented scaling and bounded interpolation profiles without using the target condition effect to select a profile.

Required inputs are source and interval manifests, landmarks, raw frame estimates, and `prosodic_trajectory_spec.yaml`. Outputs are `requested_frames.tsv`, `trajectory_preprocessing.tsv`, `trajectory_coverage.tsv`, `trajectory_diagnostics.html`, `preprocessing_decision.yaml`, and `run_provenance.json`.

The notebook supports Exercises 12.1 and 12.2. All figures distinguish observed from reconstructed values and display the number of contributing units across time.

## `02_dynamic_models_and_rhythm.ipynb`

This notebook contrasts naive aggregate smoothing with a model that represents speaker- and item-level variation and residual serial dependence. A second module calculates duration-based rhythm metrics across speakers and material subsets and demonstrates their sensitivity to elicitation and segmentation choices.

Required inputs are the prepared trajectory table, series-boundary indicators, speaker and item metadata, segmented interval data, and a prespecified model-comparison file. Outputs are `dynamic_model_diagnostics.html`, `trajectory_predictions.tsv`, `residual_dependence.tsv`, `rhythm_metrics_by_unit.tsv`, `rhythm_sensitivity.tsv`, `model_warnings.tsv`, `trajectory_gate.yaml`, and `run_provenance.json`.

The notebook supports Exercises 12.3 and 12.4. It does not treat frame count as the number of independent replications and does not classify a language's rhythm from one pooled score.

## Implementation status

Both notebooks, the synthetic fixture generator, the reusable R module, the Chapter 12 test, and the clean local execution route are implemented. The fixture contains generated contours and interval sequences only and is labeled `SYNTHETIC_TEACHING_FIXTURE` in every manifested artifact. The verified run retains all requested frames, four distinct gap codes, bounded interpolation, multiple time coordinates, speaker-level scaling parameters, contribution counts, residual-dependence diagnostics, and rhythm sensitivity by material subset and segmentation profile.

The structured model produced a repeated-smooth warning in the recorded environment. The implementation captures that warning in `model_warnings.tsv` instead of suppressing or concealing it. Residual lag-one dependence also remained substantial after the structured fit. The decision gate therefore restricts interpretation to the synthetic sample and explicitly prohibits treating frame count as replication or using the pooled metrics for language-level rhythm classification.

The fixture is regenerated with `python3 companion/scripts/generate_ch12_fixture.py`, the notebooks with `python3 companion/scripts/build_ch12_notebooks.py`, and the chapter test with `Rscript --vanilla companion/tests/test_ch12.R`. Both notebooks pass the clean Rscript runner in the recorded local environment; Colab, cross-platform, and continuous-integration verification remain open under P-001.
