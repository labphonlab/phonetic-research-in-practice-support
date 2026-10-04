# Instructor Exercise Notes

## Purpose and use

These notes provide assessment guidance for all sixty-eight hands-on exercises. They are not single model answers, because most exercises require students to make a defensible research decision from a stated question, dataset, or governance context. A strong submission makes its assumptions visible, preserves the requested evidence, distinguishes computation from scientific judgment, and narrows the claim when a gate fails. Instructors should accept more than one conclusion when the decision follows coherently from the evidence and the student records its downstream consequences.

The notes use three recurring standards. First, the submitted object must be reconstructable: another reader should be able to identify inputs, decisions, and outputs. Second, the interpretation must be calibrated: a correct calculation does not license a broader population, construct, causal, or mechanistic claim than the design supports. Third, failures must remain visible. A student should not receive less credit merely because a defensible audit rejects a measure, model, or release; suppressing the failed case is the more serious error.

## Chapter 1. Phonetic Research as an Evidential Chain

### Exercise 1.1: Reverse-engineer an evidential chain

A strong response begins with a claim quoted or accurately paraphrased from the selected article and traces it through the reported result to the design and source observations. The graph should distinguish an absent report from an apparently weak decision: “not reconstructable” is not evidence that the authors failed to perform the step. The written evaluation should identify one genuinely well-supported dependency and one missing dependency whose absence changes the permissible force or reach of the claim. Merely listing software and statistical tests does not demonstrate an evidential chain.

### Exercise 1.2: Initialize the capstone record

The project record should contain stable names for the proposed claim, evidence objects, decisions, and gates. Each stop/go gate needs an observable criterion, a decision owner, and a consequence that propagates to the design or claim; “inspect the data” is not a gate. The narrow claim should be supportable under the present plan, while the broader prohibited claim should fail for a named reason such as population coverage, construct validity, causal identification, or measurement validation.

## Chapter 2. Questions, Hypotheses, Predictions, and Replication

### Exercise 2.1: Convert topics into discriminating questions

Each revised question should name the population, comparison, measure, and context rather than merely append “Does X affect Y?” to a topic. In the selected prediction table, the competing accounts must predict observably different patterns, and the manipulation or phenomenon check must not be identical to the focal outcome. Full credit requires an outcome favoring neither account and a boundary between the claim supported by the design and a stronger unsupported interpretation.

### Exercise 2.2: Design a replication decision memo

The replication type should follow from the unresolved uncertainty. A computational replication holds the inferential target and source evidence fixed while checking reconstruction; a direct replication evaluates recurrence under closely matched conditions; a conceptual replication evaluates a more general theoretical relation under justified changes. The four outcome interpretations should include successful recurrence, a precise discrepancy, an imprecise result, and a result complicated by a failed manipulation or changed population. A memo that calls every repetition a direct replication has not identified the decision problem.

## Chapter 3. Constructs, Variables, and Measurement Validity

### Exercise 3.1: Audit a theoretical variable

The construct–measure map should separate the theoretical attribute from the stored variable and show every transformation between source observation and analysis value. A strong audit names plausible competing influences and distinguishes repeatability from evidence that the variable measures the intended construct. The proposed validation study must target the weakest link, not simply collect a larger sample with the same measurement assumptions.

### Exercise 3.2: Compare normalization estimands

The analysis should retain raw values, define each reference sample, and make ineligible speakers or missing reference categories visible. The student should compare coefficients, uncertainty, speaker ordering, and geometry without treating statistical significance as a vote for a transformation. The preferred procedure is justified by the question and estimand—for example, reducing speaker scale while retaining within-speaker category geometry—not by producing the largest group difference.

## Chapter 4. Ethics, Governance, and Open Research Plans

### Exercise 4.1: Build a speech-data governance matrix

Every research object should have an explicit purpose, risk, access role, retention rule, withdrawal behavior, and release tier. Audio and transcripts require separate judgments because voice, linguistic content, and contextual metadata can remain identifying after names are removed. A strong explanation recognizes that read speech and interviews differ in disclosure risk, third-party content, contextual sensitivity, and likely expectations of reuse; one consent event does not erase those differences.

### Exercise 4.2: Repair an inconsistent open research plan

The repaired plan must treat the actual consent scope as the governing constraint. Code, schemas, synthetic fixtures, aggregate results, and suitably reviewed derivatives may be public; raw audio, reusable transcripts, or trained models require separate authority and may need controlled or closed routes. The student should record the deviation from the original openness promise rather than silently rewriting history. The participant-facing explanation should state plainly what will and will not be shared and should not imply that technical deidentification eliminates voice risk.

## Chapter 5. Experiments, Observations, and Corpora

### Exercise 5.1: Reverse-engineer a design from its claim

The three maps should show how assignment, selection, population, controls, and alternative explanations differ across controlled, corpus, and newly recorded observational designs. A defensible recommendation may select one design or a sequence, but it must name the uncertainty each stage resolves. The main error to diagnose is treating the design label as sufficient for causal or descriptive status without examining actual assignment, comparability, and measurement.

### Exercise 5.2: Audit a corpus extraction

The student need not obtain restricted data, but must reconstruct corpus version, source population, recording frame, searchable units, annotation coverage, and selection path from authoritative documentation. The proposed extraction should include exact metadata and signal requirements and retain denominators through each exclusion. The fallback claim should remain valid under plausible differential exclusion—for example, a description of measurable tokens in the retained domain rather than a claim about all speakers or contexts represented nominally by the corpus.

## Chapter 6. Speakers, Items, Tasks, and Sampling

### Exercise 6.1: Build a multidimensional sampling plan

Both allocations should have the same nominal token total while differing in information at the speaker and item levels. A strong explanation connects the allocation to the intended generalization: additional repetitions can improve within-unit precision but cannot substitute mechanically for new speakers or items. The plan should specify recruitment, item generation, counterbalancing, occasions, and expected missingness rather than treating all recorded rows as exchangeable observations.

### Exercise 6.2: Produce a sampling manifest and flow report

The manifest must use synthetic identifiers and visibly label simulated withdrawal, device failure, missing responses, and quality exclusions. Counts in the Methods paragraph should be generated from the manifest and reconcile across recruited listeners, sessions, lists, talkers, items, and retained trials. The correct conclusion is procedural: the exercise validates a reconstructable sampling flow, not an empirical attrition rate or population pattern.

## Chapter 7. Recording, Calibration, and Metadata

### Exercise 7.1: Audit a signal chain

The diagram should begin with the talker and acoustic environment and continue through transduction, gain, conversion, software, file format, transfer, and archival source. Each component should be linked to a possible change in bandwidth, level, timing, noise, or behavior and marked by evidence state. The supported and unsupported claims should be measure-specific; a chain adequate for duration may still be inadequate for absolute level or fine spectral comparison.

### Exercise 7.2: Measure-specific device comparison

Students should use the synthetic fixture or permitted recordings, preserve source files, and report clipping, noise, spectra, duration, and level separately. A strong answer produces different adequacy decisions when the evidence warrants them and explicitly notes that playback testing does not reproduce live speech radiation, room interaction, participant behavior, or microphone placement variability. A single global device ranking is not an acceptable substitute.

### Exercise 7.3: Build a session record

The partner should be able to reconstruct equipment, connection order, channel map, calibration, filenames, deviations, and measure-specific quality decisions without oral repair. Fields that required explanation should be revised in the record, not merely mentioned in reflection. The expected product is an operational session document with stable identifiers and links to source and calibration objects.

### Exercise 7.4: Design an accessible remote protocol

The protocol should make access needs part of design rather than an afterthought. It must address qualification, instructions, monitoring, local capture, secure transfer, fallbacks, and prespecified acceptance rules. The conclusion should name unresolved device and environment heterogeneity and restrict the intended acoustic or population claim accordingly; remote participation alone is neither a validity failure nor evidence of equivalence with laboratory collection.

## Chapter 8. Perception Experiments and Behavioral Measures

### Exercise 8.1: Reverse-engineer a task claim

The five statements should keep stimulus properties, participant action, recorded response, statistical estimand, and theory distinct. The alternative process must be capable of producing the same observed response pattern, such as response bias, memory, lexical knowledge, strategy, or audibility. The proposed control or second task should change the accounts' predictions rather than simply replicate the original response measure.

### Exercise 8.2: Fit and critique a psychometric function

The model should operate on trial-level responses, report location and slope with uncertainty, and inspect participant variation and fit. Changing continuum sampling or lapse treatment should reveal which conclusions depend on design and modeling choices. A boundary estimate may describe the observed classification function; it does not by itself demonstrate a categorical mental representation.

### Exercise 8.3: Separate sensitivity and criterion

The student should calculate sensitivity and bias from hits and false alarms under stated distributional and correction assumptions. Similar percent correct can coexist with different discrimination and response strategies, so the interpretation must not collapse the two. The redesigned task should manipulate or reward criterion in a way that makes response policy the target rather than a nuisance.

### Exercise 8.4: Audit an online experiment

The audit should verify hashes, realized trials, mappings, order, timing origins, timeouts, and device logs before interpreting behavior. Cross-configuration timing differences should be evaluated against the temporal precision required by the claim. The decision may preserve response-choice claims while rejecting fine response-time or audiovisual synchrony claims; “the experiment ran” is not a sufficient timing validation.

## Chapter 9. Annotation as Measurement

### Exercise 9.1: Turn a label into a measurement rule

The specification should define the unit, allowed evidence, positive cues, counterevidence, uncertainty, and exclusions in language another annotator can apply. Borderline examples are essential because they reveal where the rule is underdetermined. A partner's need for oral explanation identifies a documentation failure to repair, not merely an annotator disagreement.

### Exercise 9.2: Diagnose categorical agreement

Students should report raw agreement, a justified chance-corrected coefficient, label prevalence, and the confusion matrix. The altered-prevalence comparison should show why a coefficient can change even when an annotator's conditional behavior is similar. The final decision should be category- and purpose-specific rather than based on one universal cutoff.

### Exercise 9.3: Analyze boundary differences

The analysis should preserve signed and absolute differences, distributional summaries, clusters, and the substantive tolerance. A 15 ms contrast may be obscured by boundary disagreement that is inconsequential for a 100 ms contrast. A high correlation or accurate mean duration does not establish interchangeability for onset, offset, or coordination claims.

### Exercise 9.4: Audit automation-induced bias

Defaults, corrections, final values, time, confidence, difficulty, and counterbalance order must remain distinct. The student should test whether correction starts shift labels or boundaries, especially in difficult cases, and propose independent or counterbalanced review when anchoring is evident. Agreement computed only after consensus or correction cannot answer the automation-bias question.

## Chapter 10. Acoustic Measurement as Scientific Measurement

### Exercise 10.1: Write a measurement specification

The specification should allow implementation without hidden conventions and should connect the measurand to the construct and intended claim. It must define input and annotation requirements, target region, algorithm, settings, units, expected failure, flags, validation sample, and decision rule. Ambiguities found by the partner are expected evidence for revision; matching output obtained through undocumented oral guidance is not sufficient.

### Exercise 10.2: Diagnose a pitch tracker

The comparison should use prespecified profiles and retain missing estimates, discontinuities, limit-adjacent values, and source-level diagnostics. A valid selection rule is based on signal behavior and intended measurement, not on which settings maximize a desired group difference. Synthetic and open signals can test software behavior and recognizable failure modes, but they do not establish accuracy across the target population without representative validation.

### Exercise 10.3: Audit automated duration

Onset, offset, and duration errors should be reported separately by context and relevant token properties. The shifted-boundary example should demonstrate that two similarly displaced landmarks can yield an accurate interval but an inaccurate location in time. Consequently, acceptance for a duration contrast cannot be transferred automatically to synchronization or coordination research.

### Exercise 10.4: Build a traceable correction layer

The raw extractor output should remain immutable. Corrections belong in a keyed table with reason, reviewer, and status, and analysis values should be regenerated by a documented join and transformation. Tests should fail on unmatched or duplicate keys and should demonstrate that the original output is recoverable.

## Chapter 11. Segmental Measures and Speaker Normalization

### Exercise 11.1: Build an event dictionary

The dictionary should define landmarks through observable evidence and specify how difficult cases change eligibility for each measure. Multiple bursts, incomplete closure, absent periodicity, and lack of a steady state should not be forced into a single default rule. Partner disagreement should be traced to missing or ambiguous instructions, and any revision should preserve the first-pass judgments for audit.

### Exercise 11.2: Compare laryngeal cue representations

The submission should display signed VOT together with closure voicing and vowel-onset F0 before modeling. A VOT-only claim can describe the timing dimension in eligible tokens, while a cue-profile claim requires joint evidence and explicit treatment of unavailable cues. Missing landmarks and context imbalance must remain visible; treating absent measurements as neutral values is a substantive error.

### Exercise 11.3: Audit vowel normalization

Preservation and reduction criteria should be declared before group labels are inspected. Students should report reference requirements, ineligible speakers, parameter stability under resampling, and changes in the focal contrast across raw, log, z-score, and ΔF-style representations. The selected transformation should match an estimand and should not be chosen because it increases separation or statistical significance.

### Exercise 11.4: Create a reconstructable normalization record

The manifest should retain raw measurements, reference membership, parameters, transformed values, and failure reasons in separate fields. Exact reconstruction from the stored parameters is required. Removing a vowel category should expose whether the reference is stable enough for the intended comparison and may justify restricting speakers or the claim rather than silently imputing a reference.

## Chapter 12. Prosody and Time-Varying Measures

### Exercise 12.1: Build a requested-frame table

Every requested frame must remain in the table, including structural voicelessness and each kind of technical or quality failure. The denominator should therefore be defined before successful estimation. A summary based only on returned values should be identified as conditional on measurement success and potentially biased when success differs by condition or speaker.

### Exercise 12.2: Compare time coordinates

The same source trajectories should be represented in onset milliseconds, proportional time, and time from the second landmark without overwriting the original coordinate. Each display answers a different temporal question and may hide duration or alignment information that another preserves. The student's three claims should therefore differ in estimand, not simply in wording.

### Exercise 12.3: Diagnose a dynamic model

The comparison should include residual temporal dependence, speaker-specific variation, uncertainty, and the focal condition difference. Adding many frames increases resolution but does not create independent speakers or events. A strong response explains whether the richer model changes the estimate, its uncertainty, or only local fit, and keeps frame count separate from the replication unit.

### Exercise 12.4: Stress-test a rhythm claim

Results should be shown across speakers, materials, metrics, and defensible segmentation choices. A pooled score is insufficient for typological classification. The final scope decision should distinguish description of the observed sample, evidence for a bounded group contrast, and the much stronger claim that a language has a stable rhythm type.

## Chapter 13. Articulatory and Multimodal Data

### Exercise 13.1: Build an observability matrix

The matrix should describe what each modality observes directly, what it proxies, what remains invisible, and the consequences of resolution, calibration, burden, and synchronization. The chosen modality set should be the smallest set that makes competing explanations observably different. Selecting the most technologically elaborate system without connecting it to the question is not a defensible answer.

### Exercise 13.2: Reconstruct a coordinate chain

Students should preserve native coordinates and apply documented transformations in order. The deliberately drifting reference sensor should move an apparently stationary articulator after correction, revealing the invalid interval through reference or stationary-target diagnostics rather than condition labels. A correct transformation matrix cannot rescue an invalid reference signal.

### Exercise 13.3: Audit multimodal synchronization

The single-offset and drift-corrected models should be compared against known anchors while preserving dropped frames. Residual timing error must be expressed on the scale relevant to the coordination claim. A model may support coarse event ordering while being inadequate for millisecond-level lag or phase claims.

### Exercise 13.4: Stress-test a kinematic landmark

All candidate peaks and parameter profiles should remain available, including plateaued, multi-peaked, noisy, and missing trajectories. The nonidentifiability rule should generate an explicit eligibility decision rather than a fabricated numeric landmark. Students should report how filters and thresholds change the analyzed event population as well as the landmark values.

## Chapter 14. Measurement Error, Sensitivity, and Robustness

### Exercise 14.1: Construct an error map

The map should locate errors by stage, direction, dependency level, condition specificity, diagnostic, validation source, and possible estimand effect. At least one error should operate differentially or at a higher level than a tokenwise reliability coefficient can reveal. A generic list of “noise” sources without propagation to the claim does not meet the task.

### Exercise 14.2: Propagate boundary alternatives

Alternative annotations should preserve token and annotator dependence and generate onset, offset, duration, and alignment variables separately. Students should compare the substantive contrast across versions and a repeated-measurement representation. The key expected insight is that cancellation can stabilize duration while leaving absolute alignment wrong.

### Exercise 14.3: Design a bounded sensitivity universe

The universe should contain a small set of scientifically defensible decisions defined before outcomes are compared. Estimand-changing branches must be labeled rather than counted with estimand-preserving variants. The result table should retain failed configurations, samples, diagnostics, estimates, and uncertainty, and the claim-stability rule must not reduce the exercise to a vote among significant results.

### Exercise 14.4: Calibrate the conclusion

The overclaim should ignore at least one known constraint, while the vague claim should discard useful stable evidence. The calibrated claim should map its direction, magnitude, population, and conditions to the result universe and acknowledge differential missingness and failed specifications. Every phrase should be traceable; unsupported causal, mechanistic, or population language should be removed.

## Chapter 15. Corpus Phonetics and Representativeness

### Exercise 15.1: Define the five populations

The five definitions should not collapse the target population into the corpus label. Students should identify transitions from corpus population to searchable universe, measurable sample, and analysis sample where coverage, annotation, signal availability, or metadata can be differential. The final claim should name the population actually supported.

### Exercise 15.2: Produce a candidate-to-analysis flow

One row per raw hit should be retained with stable identity and flags for every gate. Counts should reconcile by speaker, item, condition, and stage. Deleting rejected rows or reporting only the final sample prevents assessment of the selection process and is therefore incorrect even if the final measurement table is usable.

### Exercise 15.3: Audit forced alignment

The validation sample should cover common, reduced, overlapping, and rare contexts and compare independent reference onset and offset landmarks. Signed errors and context-specific failure are required; a pooled absolute error alone cannot support measure-specific decisions. Duration and temporal-alignment uses should receive separate accept, restrict, or reject judgments.

### Exercise 15.4: Build a cross-corpus compatibility table

Compatibility should be evaluated across population, era, style, task, equipment, annotation, lexical coverage, and measurement rather than inferred from shared file formats. The proposed overlapping domain should be explicit. A narrower matched comparison can be defensible even when a broad corpus effect is not.

## Chapter 16. Automation and Reproducible Pipelines

### Exercise 16.1: Draw the dependency graph

The graph should connect source objects to the selected manuscript figure through configurations, manual decisions, transformations, models, and release artifacts. Hidden constants, spreadsheet edits, local paths, software defaults, or undocumented exclusions should be converted into versioned inputs. Merely drawing the order of scripts without data and decision dependencies is insufficient.

### Exercise 16.2: Replace a manual correction

The original table must be restored and preserved. A keyed correction layer should contain the proposed value, reason, and provenance, and the transformed derivative should be reproducible by code. Duplicate and unmatched keys must fail rather than being silently dropped or multiplied.

### Exercise 16.3: Build a scientific test suite

The fixture should exercise valid, missing, duplicate, negative, Unicode, and measurement-failure cases. Schema, join, invariant, and integration tests establish declared software behavior; only tests linked to independently justified scientific expectations provide limited measurement validation. A green suite is not proof that a construct is valid or a population claim is correct.

### Exercise 16.4: Perform a clean-room run

The run should start without derived outputs, use the declared environment, rebuild artifacts, render notebooks, and compare against a manifest at declared tolerance. Differences in dependencies, warnings, hashes, or numeric results must be recorded and classified. Passing reconstruction establishes computational consistency of the declared route, not automatic scientific correctness.

## Chapter 17. Regression for Structured Phonetic Data

### Exercise 17.1: Write the estimand and unit graph

The estimand should identify outcome scale, comparison, population, and averaging distribution in one sentence. The graph must distinguish speakers, items, sessions, tokens, and repeated measurements and show where each predictor varies. A row-level model description without a population or unit structure is incomplete.

### Exercise 17.2: Recode the same question

Treatment, sum, and custom contrasts should yield equivalent fitted cell means when they span the same model space, even though intercepts and coefficients differ. Students should interpret each coefficient relative to its coding and choose the coding that makes the scientific comparison direct. A change in coefficient meaning must not be mistaken for a change in the underlying fitted data pattern.

### Exercise 17.3: Audit the random-effects path

The initial candidate structure should follow the design, and every fit attempt, warning, singularity, variance, correlation, and simplification should remain in a registry. The prespecified simplification rule should protect scientifically necessary variation while addressing unsupported complexity. Selecting the model that makes the focal effect significant is a failure regardless of convergence.

### Exercise 17.4: Translate coefficients into claims

Predictions and contrasts should be produced on the response scale with the averaging distribution and target units stated. Students must separate predictions for observed units from predictions for new speakers or items and mark unsupported combinations or extrapolation. A coefficient alone is not yet a research-scale claim.

## Chapter 18. Modeling Complex Phonetic Data: Structure, Error, and Scope

### Exercise 18.1: Preserve or summarize a trajectory

The scalar question and full-curve question should be genuinely different. Students should state what the scalar discards and describe dependence at speaker, item, token, and residual-time levels for the dynamic analysis. The full curve is warranted only when its additional structure bears on the question and is supported by the design.

### Exercise 18.2: Build a missingness map

Structural absence, recording failure, measurement failure, quality rejection, and missing metadata must be separate states. Availability should be evaluated by condition and higher-level unit. The complete-case estimand should be named explicitly, and any alternative analysis should state its assumptions rather than presenting imputation as automatic recovery of missing truth.

### Exercise 18.3: Criticize a fitted model

The report should examine response-scale predictions, residual distribution, variance structure, temporal dependence where applicable, and cluster influence. One diagnosed failure should demonstrably change the claim or uncertainty; another may affect fit without changing the focal conclusion. Diagnostic severity is determined by its consequence for the estimand and claim, not by the presence of an imperfect plot alone.

### Exercise 18.4: Redesign predictive validation

All observations from held-out speakers or items must remain outside their corresponding training folds, and preprocessing must be learned within each fold. Students should compare accuracy, calibration, and uncertainty across row-random, new-speaker, and new-item evaluations. Each score supports only the deployment domain represented by its partition; predictive performance does not establish causation or mechanism.

## Chapter 19. Interpretation and Calibrated Claims

### Exercise 19.1: Rewrite a threshold conclusion

The revision should foreground the estimated contrast, uncertainty, research scale, observed support, and diagnostics rather than significant/nonsignificant labels. Students should distinguish conclusions that genuinely change from statements that only become more precise. A nonsignificant coefficient cannot be rewritten automatically as no effect or equivalence.

### Exercise 19.2: Define a meaningful bound

The smallest difference of interest needs an evidential source appropriate to the claim: perceptual, clinical, theoretical, measurement, or decision based. The interval should then be assessed against the bound to distinguish meaningful difference, equivalence, and unresolved magnitude. A convenient round number or the observed estimate itself is not a prospective justification.

### Exercise 19.3: Construct the conclusion map

Every defensible branch should retain direction, magnitude, scope, diagnostics, and estimand. A stable conclusion holds across the prespecified claim-relevant universe; a conditional conclusion identifies the decision or domain on which it depends; the unsupported conclusion exceeds the evidence. Failed branches and estimand changes must remain visible and cannot be outvoted.

### Exercise 19.4: Build a claim-evidence map

Each clause should be classified and linked to the design, measurement, result, diagnostics, and population evidence it requires. Association must not be upgraded to mechanism or causation, and within-sample fit must not be upgraded to external prediction. The expected product is revised prose whose force and reach can be checked clause by clause.

## Chapter 20. Reproducible Release and Research Stewardship

### Exercise 20.1: Classify the research objects

The inventory should assign owner or authority, access class, license, provenance, and release disposition to every object. Recordings, annotations, third-party code, trained models, and publisher text may have different rights and cannot inherit a default project license automatically. Unresolved rights should default to restricted rather than public.

### Exercise 20.2: Build protected and public routes

Both profiles should invoke the same transformation logic while resolving different authorized inputs. The protected route should not expose canonical paths or data in public logs, and the public route should use permitted or visibly synthetic materials. Students must state which empirical results the public route reproduces and which it only demonstrates procedurally.

### Exercise 20.3: Assemble and audit a release candidate

The candidate should be constructed from an allowlist in a clean directory and accompanied by artifact, checksum, license, provenance, and review records. Automated scans should cover identifiers, secrets, private paths, notebook outputs, media, and license incompatibility, while human governance approval remains a separate gate. Technical success does not authorize deposit or publication.

### Exercise 20.4: Write the availability and stewardship statement

Every sentence should resolve to the release manifest or an explicit author/publisher placeholder. The statement should identify versions, access routes, restrictions, permitted capabilities, citation, maintenance, correction, and withdrawal. A DOI or public availability claim must not appear until an authorized deposit exists; an honest statement that release is pending is the correct answer when approval remains open.

## Applying these notes consistently

For formative work, instructors should mark the first unsupported dependency and allow revision rather than scoring only the final conclusion. For summative work, the six-dimensional capstone rubric in `INSTRUCTOR_GUIDE.md` remains authoritative. These exercise notes supply task-specific evidence for that rubric; they do not replace institutional rules on grading, accommodations, academic integrity, human-participant work, or protected data.
