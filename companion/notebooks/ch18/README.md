# Chapter 18 notebook specification

**Primary language:** R

Chapter 18 evaluates whether nonlinear, multivariate, measurement-error, missing-data, Bayesian, or predictive components are required by the scientific question. Each complex component must be paired with a data-support statement and a diagnostic. The notebooks use synthetic fixtures only for known error mechanisms and label them as workflow or estimator tests rather than population evidence.

## `01_dynamic_error_and_missingness.ipynb`

This notebook compares a simple scalar benchmark with a dynamic model that preserves trajectory shape, group-level functions, and within-series residual dependence. It then propagates validated or explicitly hypothetical measurement error and constructs a reason-coded missingness map separating structural absence, nonresponse, technical loss, algorithmic failure, quality rejection, and censoring. Optional imputation is performed only under a declared multilevel imputation model and never replaces structurally absent phonetic events.

Required inputs are `complex_model_spec.yaml`, the frozen trajectory or multivariate table, series boundaries, raw and transformed time coordinates, measurement-validation results, missingness codes, and the Chapter 14 sensitivity specification. Outputs are `trajectory_support.tsv`, fitted benchmark and dynamic models, `residual_dependence.tsv`, `measurement_error_results.tsv`, `missingness_map.tsv`, `imputation_diagnostics.html`, and `run_provenance.json`.

The notebook supports Exercises 18.1–18.3. Every hypothetical error or missingness mechanism records its assumption, range, generator, and seed at the point of use.

## `02_prediction_validation_and_scope.ipynb`

This notebook contrasts row-random validation with speaker-, item-, session-, and corpus-held-out partitions. All normalization, imputation, feature selection, dimension reduction, and tuning occur inside training folds. It evaluates calibration, error distributions, class-specific performance, and uncertainty resampled at the deployment unit, then joins predictive evidence with explanatory diagnostics and measurement sensitivity to produce a four-dimensional scope statement.

Required inputs are the candidate-model registry, frozen fold assignment policy, deployment-domain specification, permitted feature table, preprocessing recipe, outcome schema, and claim map. Outputs are `fold_assignments.tsv`, `leakage_audit.tsv`, `validation_performance.tsv`, `calibration.tsv`, `domain_errors.tsv`, `model_comparison.tsv`, `model_scope_gate.yaml`, and `run_provenance.json`.

The notebook supports Exercise 18.4. Its final record distinguishes population, measurement, predictor, and goal scope; predictive success is not reported as causal or mechanistic evidence.
