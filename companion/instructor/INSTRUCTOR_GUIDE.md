# Instructor Guide

## Purpose and status

This guide translates the manuscript into an operational graduate course. It is complete at the level of learning sequence, assignments, capstone routes, assessment, and notebook contracts. The separate `INSTRUCTOR_EXERCISE_NOTES.md` supplies first-draft assessment guidance for all sixty-eight exercises. Twenty-eight executable notebooks, synthetic fixtures, automated tests, and recorded Python and R environment files have passed local clean execution. Cross-platform, hosted-Colab, remote-CI verification, and publisher review of the instructor materials remain production work under checklist item P-001 and must not be advertised as completed.

## Preparing the course

Instructors should select the course pathway before selecting datasets. The one-semester pathway privileges one complete evidential chain and uses tightly scoped data. The two-semester pathway permits independent pilots and deeper measurement validation. The statistics-light pathway supplies validated model objects while preserving interpretation and design responsibilities. Attempting full new-data collection, all measurement modalities, and advanced modeling in one semester will weaken the cumulative structure.

Before the course begins, the instructor should verify institutional policies for research with human participants, classroom recordings, cloud services, licensed corpora, data retention, accessibility, and generative tools. A classroom exercise is not exempt from governance because it is not intended for publication. If students may later publish their projects, the distinction between teaching activity and research must be settled prospectively.

The instructor should also choose one small open teaching dataset or explicitly synthetic fixture that can support shared demonstrations. Licensed or identifiable data can be used in separate controlled projects, but they should not be required for basic participation. Every supplied dataset receives a manifest containing source, license, checksum, schema, and known limitations.

## Standard class sequence

A ninety-minute seminar can use a four-movement structure. The opening problem presents a plausible research decision with incomplete information. The conceptual discussion identifies distinctions from the chapter and compares defensible options. The evidence workshop audits a paper, protocol, dataset, or diagnostic. The final period begins the capstone object and ends with a decision record. Longer laboratory sessions can then implement and validate the object.

Students should submit a short pre-class decision rather than a generic reading summary. Examples include choosing between two population definitions, identifying the estimand implied by a figure, or stating what evidence would invalidate an acoustic measure. Returning to the initial decision after discussion makes conceptual change visible.

## Chapter-to-teaching map

| Chapter | Central teaching question | Primary student object | Common misconception to diagnose |
|---:|---|---|---|
| 1 | What connects a result to a defensible claim? | Study graph | Reproducibility begins when code is uploaded |
| 2 | Which observation distinguishes competing explanations? | Prediction and replication table | A directional result is itself a hypothesis |
| 3 | What evidence makes an operational variable valid? | Construct-to-measure map | A familiar acoustic measure is the construct |
| 4 | Who has authority over collection, access, and reuse? | Governance and sharing plan | Deidentification makes speech freely shareable |
| 5 | What does the design identify? | Design comparison and threat register | Experiments are causal and corpora are merely descriptive by label |
| 6 | Which units and populations provide information? | Sampling and precision plan | Token count is sample size for every claim |
| 7 | Which signal chain produced the waveform? | Recording and calibration record | Lossless format corrects poor acquisition |
| 8 | Which behavior does the task measure? | Trial manifest and behavioral estimand | A psychometric boundary is a stored phoneme boundary |
| 9 | Which judgment created the annotation? | Annotation schema and agreement plan | Agreement validates the underlying construct automatically |
| 10 | Which estimator produced the acoustic value? | Acoustic measurement specification | Software reads F0 or formants directly from the signal |
| 11 | What information does normalization remove and retain? | Raw/transformed measure manifest | Normalization is neutral cleaning |
| 12 | Which temporal representation answers the question? | Trajectory specification | More frames create more independent evidence |
| 13 | Which coordinate, calibration, and synchronization system defines movement? | Multimodal session record | Device precision is constant and factory-defined |
| 14 | Which conclusion survives defensible error and decision profiles? | Sensitivity universe | Robustness is a vote among significant models |
| 15 | Which population does the corpus sample support? | Candidate manifest and corpus gate | Large corpora are representative by size |
| 16 | Which declared dependencies regenerate the result? | Pipeline graph and clean-run record | A notebook is a complete reproducibility system |
| 17 | Which structure makes rows informative about new units? | Estimand and model-attempt registry | Random intercepts solve all repeated-measure dependence |
| 18 | What complexity is required, supported, and validated? | Model-scope gate | Better fit expands the population claim |
| 19 | How strong and broad can the conclusion be? | Claim-evidence map | Statistical significance identifies importance or mechanism |
| 20 | What can be released, to whom, under whose authority? | Release manifest and availability statement | FAIR means every file must be public |

## Formative assignments

Formative assignments should be small enough to revise. Each receives three kinds of feedback: whether the scientific decision is defensible, whether its consequence is propagated, and whether another researcher could reconstruct it. A student can therefore receive credit for a defensible restriction even when the original plan proves infeasible.

Recommended formative checkpoints are the question and competing-prediction table after Chapter 2, construct map after Chapter 3, governance and design memo after Chapter 5, sample-support report after Chapter 6, source-data protocol after Chapters 7–9, measurement-validation report after Chapter 10 or the selected modality chapter, sensitivity map after Chapter 14, pipeline and sample freeze after Chapter 16, model and diagnostics report after Chapter 18, and claim-release package after Chapter 20.

Peer review should use the chapter decision checklist rather than open-ended stylistic comments. Reviewers identify one supported decision, one missing dependency, one claim that exceeds current evidence, and one revision that would change downstream work. Students respond in a decision log.

## Capstone package

Every capstone route produces a common package even when empirical content differs. The package contains a bounded question, competing prediction table, construct map, governance and access record, design and sampling plan, candidate or trial manifest, source metadata, annotation or measurement specification, validation evidence, sensitivity universe, pipeline specification, estimand, model registry, diagnostics, claim-evidence map, and release plan.

The new-data route additionally provides authorization and consent scope, recruitment flow, session logs, and source-data storage documentation. The existing-data route provides corpus or dataset version, license, query denominator, compatibility assessment, and source citation. The reproduction or synthetic route provides the target result, reproduction level, fixture generator, assumptions, seed, and a statement of which empirical claims it cannot support.

Students should submit machine-readable objects alongside prose. A PDF alone is insufficient because it cannot demonstrate the pipeline, schemas, or stable identifiers. Raw restricted data should not be submitted through a learning-management system unless institutional policy explicitly authorizes that route.

## Capstone rubric

The rubric uses six dimensions scored on a four-level scale. The labels describe evidence quality rather than aesthetic polish.

| Dimension | 4 — defensible and reconstructable | 3 — adequate with bounded omissions | 2 — consequential weakness | 1 — unsupported or absent |
|---|---|---|---|---|
| Question and construct | Competing predictions and measures discriminate the target alternatives | Question and measures align but alternatives are incompletely separated | Operationalization partly mismatches the question | Result is not connected to a defined construct or question |
| Governance and sampling | Authority, access, target population, units, and selection flow are explicit | Core permissions and units are clear; one scope dimension is weak | Important permission, population, or denominator is unresolved | Unauthorized use or untraceable sample |
| Measurement | Procedure, settings, target-domain validation, failures, and error are documented | Procedure and validation exist but risk coverage is incomplete | Values are produced with weak validation or overwritten corrections | Measure is treated as direct truth or provenance is absent |
| Analysis | Estimand, dependence, model support, diagnostics, and uncertainty align | Primary model aligns; diagnostics or sensitivity are limited | Model fits but misrepresents a consequential structure | Rows, scales, or tests do not answer the stated question |
| Claim calibration | Force and reach match results, limitations, sensitivity, and evidence level | Main claim is defensible with minor overreach or omitted alternative | Claim depends on threshold language or selective evidence | Mechanistic, causal, predictive, or population claims are unsupported |
| Reproducibility and stewardship | Permitted route cleanly rebuilds outputs; manifest, license, citation, and release gates align | Most artifacts reconstruct; one noncritical dependency remains | Shared materials omit important dependencies or access detail | Release is irreconstructable, unauthorized, or exposes restricted content |

An instructor can convert dimension scores to local grades, but failure in governance cannot be compensated by stronger statistical output. Unauthorized or privacy-violating work is returned for remediation and may be subject to institutional procedures.

## Oral defense

The capstone defense should test decision reasoning rather than code recall. Students identify the most vulnerable link, explain one revision made after validation, distinguish the primary claim from an attractive unsupported claim, and demonstrate the permitted clean route or its protected equivalent. They should be able to state what observation would change their conclusion.

A useful defense includes one adversarial scenario chosen by the instructor: the aligner fails more often in one group, a random-slope model is singular, a corpus version changes, an equivalence bound lacks justification, or a repository license conflicts with the data source. The student explains which gate fails and what can still be claimed.

## Notebook and solution policy

Student notebooks should contain learner decisions in clearly identified cells or companion files. Supplied code can perform routine imports, plotting, and tests, but it should not conceal the scientific choice. Automated tests should check schema and invariants without revealing every interpretive answer.

Instructor solutions should include more than successful output. `INSTRUCTOR_EXERCISE_NOTES.md` implements this principle by naming expected evidence, common failure modes, and acceptable variation for every exercise without prescribing one answer where several research decisions are defensible. Solutions containing restricted data remain in governed storage and are never bundled with the public companion release.

## Feedback language

Feedback should distinguish correctness, support, and scope. “This estimate is computed correctly” does not mean “this is the right estimand.” “The model fits” does not mean “the dependence structure is adequate.” “The conclusion is plausible” does not mean “the design identifies it.” Naming the link that fails helps students revise without interpreting criticism as a demand for a different favored software package.

## Production checklist for instructors

Before teaching from a release, verify that the manuscript edition matches the companion tag, every assigned notebook executes in the supported environment, datasets and fixtures have licenses and checksums, external links are current, answer materials are separated, accessibility alternatives are available, and institutional governance has been reviewed. Record the date and environment of this verification.

During the term, preserve discovered errors and platform changes in an instructor issue log. Do not silently correct a notebook in a way that changes student outputs after submission. At term end, classify corrections as documentation, computational, or scientific and incorporate them into a new versioned release.
