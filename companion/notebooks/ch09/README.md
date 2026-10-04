# Chapter 9 notebook specification

**Primary language:** R

**Implementation status:** Both specified R notebooks are implemented with explicitly synthetic independent judgments, speaker-cluster bootstrap uncertainty, continuous boundary-difference retention, and a counterbalanced automation audit. They pass the Chapter 9 test and clean Rscript notebook runner. Colab and cross-platform verification remain part of P-001.

Chapter 9 uses synthetic categorical annotations and boundary times. The exercises preserve first-pass judgments, automatic defaults, corrections, and adjudication in separate fields so that agreement is never computed from consensus labels.

## `01_categorical_agreement.ipynb`

This notebook validates an annotation schema and two or more independent label files, constructs label-frequency tables and confusion matrices, calculates percent agreement and prespecified chance-corrected agreement, and quantifies uncertainty using a cluster-respecting procedure. Learners change prevalence and category distance to see how the interpretation changes.

Required inputs are `annotation_schema.yaml`, `annotation_assignments.tsv`, and long-form independent judgments. Outputs are `categorical_agreement.tsv`, `confusion_matrices.tsv`, `agreement_diagnostics.html`, `analysis_decisions.yaml`, and `run_provenance.json`. The notebook must stop if adjudicated labels are supplied in place of independent judgments.

The notebook supports Exercises 9.1 and 9.2. Assessment requires a decision about the usability of each category rather than a pass/fail judgment from one coefficient.

## `02_boundary_and_automation_audit.ipynb`

This notebook compares continuous landmark times using signed and absolute differences, condition- and boundary-specific summaries, diagnostic plots, and substantively defined tolerances. A second section compares annotation from scratch with correction of automatic defaults while preserving default, correction, final judgment, time, and confidence.

Required inputs are independent boundary judgments, the annotation assignment table, and an optional automatic-proposal audit. Outputs are `boundary_differences.tsv`, `boundary_diagnostics.html`, `automation_bias.tsv`, `review_decisions.tsv`, and `run_provenance.json`.

The notebook supports Exercises 9.3 and 9.4. It must not convert continuous differences to binary agreement without also retaining and reporting the original difference distribution.
