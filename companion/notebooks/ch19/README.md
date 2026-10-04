# Chapter 19 notebook specification

**Primary language:** R

Chapter 19 converts verified results into bounded scientific claims. The notebooks do not generate prose from significance labels. They assemble research-scale quantities, uncertainty, diagnostics, sensitivity, and domain evidence, then require the learner to classify and justify each interpretive step.

## `01_results_uncertainty_and_equivalence.ipynb`

This notebook reads the primary estimand and model outputs, reproduces focal quantities on the research scale, and separates direction, magnitude, precision, and practical relevance. It visualizes intervals against prospectively justified meaningful bounds, performs equivalence or bounded-effect analysis where specified, and calculates Type S and Type M design diagnostics using externally justified effect scenarios rather than the observed estimate as truth.

Required inputs are the Chapter 17 result table, Chapter 18 scope gate, `claim_evidence_map.yaml`, prespecified meaningful-bound record, and sensitivity conclusion map. Outputs are `research_scale_results.tsv`, `meaningful_bounds.tsv`, `equivalence_assessment.tsv`, `sign_magnitude_risk.tsv`, `interpretation_diagnostics.html`, and `run_provenance.json`.

The notebook supports Exercises 19.1–19.3. An inconclusive interval remains inconclusive; the notebook does not turn failure to cross a threshold into equivalence or absence.

## `02_claim_evidence_map.ipynb`

This notebook joins each proposed manuscript claim to design, population, measurement, model, diagnostic, sensitivity, and theoretical-discrimination evidence. It classifies clauses as observation, association, prediction, mechanism hypothesis, or causal explanation and compares the proposed force and reach with the evidence. Unsupported clauses fail the calibrated-claim gate and remain visible with a required revision.

Required inputs are `claim_evidence_map.yaml`, the frozen result and conclusion tables, the corpus or experiment inference gate, the model-scope gate, and a draft claim registry. Outputs are `claim_registry.tsv`, `claim_support.tsv`, `unsupported_clauses.tsv`, `domain_statements.tsv`, `calibrated_claim_gate.yaml`, and `run_provenance.json`.

The notebook supports Exercise 19.4. Human scientific judgment approves final wording; the notebook supplies traceability and detects contradictions rather than composing claims from p-values.
