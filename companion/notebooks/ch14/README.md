# Chapter 14 notebook specification and implementation record

**Primary language:** R

Chapter 14 propagates observed or explicitly hypothetical measurement uncertainty into a bounded result universe. Synthetic data are used only to demonstrate known error mechanisms and remain labeled as simulation outputs.

## `01_error_propagation.ipynb`

This notebook joins validation pairs, repeated measurements, failure codes, and the error map. It demonstrates distinct consequences of outcome, predictor, landmark, shared-reference, and differential error. Perturbations operate at the level where the error arises and preserve speaker, item, session, annotator, and trajectory dependence.

Required inputs are `sensitivity_analysis_spec.yaml`, validation and repeatability manifests, raw and alternative measurement layers, and the frozen primary estimand. Outputs are `error_components.tsv`, `propagated_datasets_manifest.tsv`, `measurement_effects.tsv`, `error_diagnostics.html`, and `run_provenance.json`.

The notebook supports Exercises 14.1 and 14.2. Every simulated error distribution records assumptions, seed, generator, and the validation evidence or hypothetical range on which it is based.

## `02_sensitivity_universe.ipynb`

This notebook executes the primary configuration first and then a prespecified set of defensible alternatives. It records estimate, uncertainty, sample, exclusions, estimand, measurement profile, diagnostics, and failure status for every attempted specification. It groups results by consequential decisions and evaluates direction, magnitude, scope, and diagnostic stability without counting significant results as votes.

Required inputs are the frozen analysis data, a machine-readable configuration table, claim-stability rules, and locked environments. Outputs are `specification_results.tsv`, `specification_failures.tsv`, `claim_stability.tsv`, `specification_curve.html`, `conclusion_map.yaml`, `claim_stability_gate.yaml`, and `run_provenance.json`.

The notebook supports Exercises 14.3 and 14.4. Post-result branches are recorded as exploratory and cannot replace the primary configuration silently.

## Implementation status

Both notebooks, a six-artifact synthetic fixture, the reusable R module, the chapter test, and the clean local execution route are implemented. The first notebook records six distinct error mechanisms and generates 240 hash-addressed propagation records from six mechanisms with forty repetitions each. Validation-derived scales, repeatability-derived scales, generator-known hypothetical ranges, and observed fixture missingness are explicitly distinguished. Perturbations occur at the observation, speaker, or group level declared by the error map, and the frozen raw analysis file remains unchanged.

The second notebook executes the primary configuration first, retains seven successful configurations and one intended failure, and separates same-estimand, changed-estimand, and exploratory branches. In the generated fixture, successful high-priority same-estimand configurations have positive estimates within the prespecified magnitude region and retain both groups and all twenty-four synthetic speakers. The gate therefore records `stable` for this teaching universe while prohibiting significance voting and warning that the result does not quantify uncertainty in empirical measurements.

The fixture is regenerated with `python3 companion/scripts/generate_ch14_fixture.py`, the notebooks with `python3 companion/scripts/build_ch14_notebooks.py`, and the test with `Rscript --vanilla companion/tests/test_ch14.R`. Both notebooks pass the clean Rscript runner in the recorded local environment; Colab, cross-platform, and continuous-integration verification remain open under P-001.
