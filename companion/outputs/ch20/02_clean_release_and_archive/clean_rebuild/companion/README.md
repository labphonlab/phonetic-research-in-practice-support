# Companion materials architecture

The companion materials implement the book's evidential chain. They are not a collection of software demonstrations. Each chapter package begins with a research decision, accepts documented inputs, creates inspectable intermediate records, and ends with an output that can be connected to a calibrated claim.

## Organization

Each computational chapter has a directory under `notebooks/chNN/`. Its `README.md` defines the notebooks, primary language, input contract, expected outputs, validation checks, and connection to the chapter exercises. Shared schemas and blank records live in `templates/`. Small synthetic teaching data live in `data/`, with one manifest recording source, license, generation procedure, and checksum. Rendered teaching outputs are not treated as source data.

The package contains 28 notebooks: two for each of Chapters 7–20. The first notebook in a chapter teaches and validates the chapter's core research decision; the second integrates that decision with diagnostics, evaluation, or release. Each specification names the exercises it supports. The fixed count prevents the phrase “chapter notebook” from expanding into an unmaintainable collection of demonstrations.

Python is primary for acquisition, validation, automation, and release workflows. R is primary for statistical modeling chapters. A chapter receives a parallel-language notebook only when it teaches a substantively useful comparison; maintaining duplicate implementations is not the default. Every notebook must be runnable outside Colab from an environment lock file. Colab is a delivery surface, not the preservation format.

## Notebook contract

Every notebook states a learning objective, estimated completion time, prerequisite chapter, data provenance, software environment, and expected files before executing code. It separates supplied code, learner decisions, validation tests, and interpretive writing. Random procedures use recorded seeds. The final cells write machine-readable outputs and a short decision record rather than relying on notebook display state.

Notebooks fail clearly when an input violates its schema. They do not download restricted audio, embed credentials, or silently replace missing data with examples. Demonstration values are visibly synthetic at the point of use. Outputs include version, input hashes, settings, and warnings sufficient to reconstruct the run; time-dependent execution records are kept separate from canonical source notebooks.

## Licensing and free distribution

The package is distributed free of charge. Code is released under the MIT License (`LICENSE`); data, templates, and written material are released under Creative Commons Attribution 4.0 International (`LICENSE-DATA.txt`). `NOTICE.md` states the scope and the citation form, and `CITATION.cff` carries the machine-readable citation. Every data object is a synthetic teaching fixture, so the package contains no human-subject data and no restricted-corpus material, and `data/MANIFEST.tsv` records the license and checksum of each object.

## Release and maintenance

Tagged companion releases will be archived with a DOI-bearing repository such as Zenodo when publisher policy permits. GitHub will support issue tracking and current development; an archival release will preserve the version matched to each printing. Continuous checks will execute notebooks, validate schemas, confirm that no restricted or identifying source data are present, and compare required output files with the documented contract.

The maintained package includes a tested local route in addition to the planned Colab delivery surface. This protects the materials against hosted-runtime changes and permits controlled use with sensitive data that must not leave an institution. Maintenance notes identify supported language and library versions, known platform constraints, and migrations that change outputs.

## Implementation status

Chapters 7–20 are executable vertical slices. All twenty-eight notebooks, synthetic recording, perception, annotation, acoustic-estimation, duration, segmental, normalization, pitch-trajectory, rhythm, coordinate, synchronization, kinematic, measurement-error, sensitivity-universe, corpus-query, representativeness, pipeline-contract, clean-reproduction, mixed-model, diagnostic, prediction, dynamic-model, observation-process, leakage-audit, scope-gating, equivalence, design-risk, claim-evidence, privacy, license, clean-release, and archival-preparation fixtures, provenance manifest, reusable Python and R modules, dependency files, local sequential-cell runners, and tests are implemented. The runners deliberately reject notebook magics and shell escapes so that passing execution does not depend on undocumented interactive state. Cross-platform, hosted-Colab, and continuous-integration verification remain separate release checks.

`companion/scripts/validate_implemented_companions.sh` is the current single validation entry point. It regenerates the implemented fixtures and notebooks, checks the global data manifest and every artifact hash, runs the Python and R tests, executes every implemented notebook in a clean process, and then reruns the manuscript audit. It validates the recorded local environment; it does not stand in for the still-pending Colab, cross-platform, or continuous-integration matrix.
