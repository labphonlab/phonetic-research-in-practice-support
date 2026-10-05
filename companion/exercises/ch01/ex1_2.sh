#!/bin/sh
# Exercise 1.2: Initialize the capstone record
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

mkdir capstone && cd capstone && git init
printf 'claim_id\tclaim\tevidence\tstatus\n' > claim_evidence_map.tsv
printf 'date\tdecision\treason\talternatives_rejected\n' > decision_log.tsv
printf 'source_id\tcitation_or_path\tversion\tlicense_or_terms\tdate_accessed\n' > source_ledger.tsv
printf 'object\taccess_class\tbasis\n' > data_access.tsv
printf 'gate\tevidence_checked\tdecision_controlled\tconsequence_of_failure\n' > gates.tsv
printf 'G1\tpilot clipping and noise-floor summary\tkeep, re-record, or drop the measure\tmeasure removed from target claim\n' >> gates.tsv
