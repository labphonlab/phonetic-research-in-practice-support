# Chapter 17 notebook specification

**Primary language:** R

Chapter 17 maps a phonetic estimand and the study's sampling graph to a structured regression model. The notebooks use small openly licensed or explicitly synthetic fixtures to expose design matrices, grouping relations, model failures, and predictions. They do not choose a model by whichever version produces the preferred focal result.

## `01_estimand_design_matrix_and_mixed_model.ipynb`

This notebook reads `regression_analysis_spec.yaml`, validates the analysis dataset against its schema, and renders the estimand, outcome family, factor levels, contrast matrix, scaling constants, and grouping graph before fitting. It compares fixed-effects-only, random-intercept, and design-justified random-slope structures to demonstrate how dependence and generalization change uncertainty. Deliberate duplicate keys and under-supported slopes are included as validation cases.

Required inputs are the frozen analysis manifest, analysis-data schema, `regression_analysis_spec.yaml`, contrast table, and permitted fixture data. Outputs are `estimand_record.yaml`, `design_matrix.tsv`, `grouping_graph.svg`, `data_support.tsv`, `model_attempts.tsv`, serialized fitted models, and `run_provenance.json`.

The notebook supports Exercises 17.1–17.3. It preserves warnings, singular fits, unsuccessful attempts, and every simplification step rather than exposing only the final model.

## `02_diagnostics_predictions_and_reporting.ipynb`

This notebook checks the selected outcome distribution, residual structure, higher-level influence, and observed predictor support. It generates the exact focal contrast on both analysis and response scales, distinguishes population predictions from conditional predictions for observed units, and records the averaging distribution. A machine-readable result table links every reported quantity to a model, estimand, prediction grid, and diagnostics gate.

Required inputs are the model-attempt registry, selected model object, frozen prediction grid, estimand record, and claim-stability output from Chapter 14. Outputs are `model_diagnostics.html`, `cluster_influence.tsv`, `prediction_support.tsv`, `model_predictions.tsv`, `focal_contrasts.tsv`, `structured_regression_gate.yaml`, and `run_provenance.json`.

The notebook supports Exercise 17.4. It reports extrapolated or weakly supported cells explicitly and does not convert a coefficient's significance into a substantive claim.
