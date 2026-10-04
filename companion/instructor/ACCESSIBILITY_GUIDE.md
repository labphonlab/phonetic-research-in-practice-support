# Accessibility Guide for Teaching and Companion Materials

## Scope

This guide helps instructors preserve the learning objectives of *Phonetic Research in Practice* when students encounter barriers involving hearing, vision, motor interaction, speech production, attention, language processing, computing access, or laboratory participation. It is a pedagogical design guide, not a certification of compliance with any jurisdictional standard. Instructors remain responsible for consulting the institution's disability-access service, technology policy, and course-specific accommodation process.

The book's central learning outcome is decision quality, not performance of a particular sensory or motor action. A student should be able to demonstrate how a research question, measurement, validation result, and claim depend on one another without being required to hear an uncaptioned distinction, produce a target pronunciation, drag a boundary with high motor precision, distinguish colors, or use a hosted service. An alternative should preserve the construct being assessed while changing the access route.

## Materials supplied in more than one form

Notebook conclusions should never depend on color alone. Figures should combine color with line type, symbol, direct label, panel, or textual summary. Tables and machine-readable outputs should accompany plots whenever exact values or classifications matter. Plot captions should identify the question, variables, unit, direction of the displayed contrast, and any missing-data or eligibility pattern that affects interpretation.

Audio-based exercises should include metadata and a nonaudio representation suitable for the task. Depending on the learning objective, this may be an annotated waveform and spectrogram, a measurement table, a landmark file, a textual event description, or a synthetic signal specification. A transcript is useful for linguistic content but does not substitute for acoustic evidence. Conversely, requiring a student to identify an acoustic event by listening is inappropriate when the objective is to evaluate a measurement rule or provenance record.

Instructions, schemas, templates, and expected outputs should remain available as text outside rendered notebook cells. Code cells should have short functional descriptions, and generated files should use stable names. Long console output should be summarized in a small decision table. Keyboard operation and non-drag alternatives should be available for tasks that would otherwise require interactive boundary placement or point selection.

## Accessible alternatives by task family

For recording exercises, a student who cannot produce or monitor the target speech can audit an existing synthetic signal chain, inspect a session record, or design a measure-specific acceptance protocol. The assessed outcome is whether the student can connect acquisition conditions to measurement and claim, not whether the student can serve as a convenient speaker. Remote and field protocols should offer written instructions, test recordings, progress confirmation, and a nonpunitive fallback when the recording environment is unusable.

For perception exercises, instructors should not require students to act as unconsented pilot participants or to demonstrate typical hearing. Students can work from the synthetic trial tables, examine stimulus specifications, audit timing logs, or evaluate a psychometric model. When listening is educationally relevant, volume, repetition, pacing, and a parallel visual or tabular route should be available, while the instructor should explain which acoustic information the alternative representation does and does not preserve.

For annotation exercises, students may use prepared landmark candidates and decision records instead of manually manipulating a display. A keyboard-entered time, row-based classification, or review of paired annotations can assess the same reasoning as mouse-based segmentation. Time pressure should not be used to measure annotation competence unless speed is itself the declared construct and has been approved as part of the course assessment.

For acoustic and articulatory measurement, the package should provide numeric source descriptors and quality flags alongside plots. Students unable to inspect a dense spectrogram or trajectory visually can evaluate a structured measurement table, thresholds, residuals, missingness, and decision records. Students unable to hear the source can still assess whether the proposed acoustic measure is valid, provided the evidence supplied is adequate for that decision. An instructor should not describe either alternative as a simplified version when it tests the same evidential reasoning.

For statistics and programming, a student may submit a completed machine-readable decision object and interpretation using instructor-supplied validated output when coding is not the learning objective. The statistics-light pathway formalizes this option. Code execution remains required only when the objective is reproducible workflow construction, and even then the assessment should emphasize declared inputs, successful validation, retained failures, and reconstructable outputs rather than typing speed or memorized syntax.

For oral defense, instructors should permit an equivalent live, recorded, written, or augmentative-communication format consistent with institutional accommodations. The defense must still test whether the student can identify the vulnerable link, explain a revision, distinguish a supported from an unsupported claim, and respond to an adversarial scenario. Fluency, accent, speech rate, or spontaneous turn-taking should not enter the score unless they are independently justified course outcomes.

## Notebook and document practices

Every notebook begins with its purpose, prerequisites, data status, and expected outputs. Instructors should distribute a static HTML or equivalent rendered copy when students cannot or need not execute code during reading. The executable notebook remains the source for computational work, but a static copy helps screen-reader navigation and protects students from losing conceptual access when a runtime is unavailable.

Markdown headings should remain hierarchical, links should use descriptive labels, and tables should have a header row with one meaning per column. Images require concise alternative text and, when they carry analytical content, a longer textual interpretation or paired table. Equations should be accompanied by a verbal definition of symbols and the scientific quantity being estimated. File formats should be chosen for actual access needs rather than assumed universality.

The companion uses synthetic fixtures so that basic participation does not require access to restricted speech, specialist laboratories, or personal recording. Synthetic status must remain visible because accessibility does not justify presenting generated data as human evidence. When a student's authorized local data cannot be moved to a cloud service, the tested local route is the required accessibility and governance route.

## Planning an accessible class session

Instructors should publish the activity, input files, expected object, approximate duration, and required technology before class. A student should be able to request an alternative without disclosing more personal information than institutional procedure requires. Pair work should divide scientific roles—such as specification writer, auditor, analyst, and claim reviewer—rather than assigning a student permanently to a task based on a perceived limitation.

Time estimates in notebooks are planning aids, not speed standards. When a task is slowed by assistive technology, language processing, or a prescribed alternative interface, additional time should not be treated as evidence of weaker research judgment. Staged submission can separate a scientific decision from technical formatting and makes it easier to identify which barrier requires repair.

## Accessibility preflight

Before assigning a chapter, the instructor should verify that every essential figure has a textual or tabular counterpart, color is not the sole signal, audio-dependent steps have a scientifically appropriate alternative, interactive operations have a keyboard or row-based route, files open with institutionally supported software, and the assignment can be completed without uploading protected data. The instructor should also verify that alternative routes lead to the same rubric dimensions and do not quietly reduce the opportunity to demonstrate high-level reasoning.

Accessibility findings should enter the same issue and version process as computational defects. A barrier discovered during teaching is evidence about the material, not an individual student's failure. Corrections that change an assignment's assessed construct, required output, or grading rule should be announced and versioned rather than applied silently after some students have submitted work.
