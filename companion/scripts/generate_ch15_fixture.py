#!/usr/bin/env python3
"""Generate explicitly synthetic Chapter 15 corpus-sampling fixtures."""

from __future__ import annotations

import csv
import hashlib
import random
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "companion" / "data"
CHAPTER_ROOT = DATA_ROOT / "ch15" / "synthetic_corpus"
SEED = 15042026


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rng = random.Random(SEED)
    CHAPTER_ROOT.mkdir(parents=True, exist_ok=True)
    hits: list[dict[str, object]] = []
    links: list[dict[str, object]] = []
    hit_index = 0
    for speaker_index in range(1, 31):
        corpus = "SYN_CORPUS_A" if speaker_index <= 18 else "SYN_CORPUS_B"
        region = "north" if speaker_index % 3 else "south"
        style = "casual" if speaker_index % 2 else "interview"
        era = "2010s" if corpus == "SYN_CORPUS_A" else "2020s"
        speaker = f"SYN_CORP_SPK_{speaker_index:02d}"
        for item_index in range(1, 21):
            hit_index += 1
            token_id = f"SYN_TOKEN_{hit_index:04d}"
            context = not (item_index % 13 == 0)
            signal = not ((corpus == "SYN_CORPUS_B" and style == "casual" and item_index % 5 == 0) or item_index % 17 == 0)
            measurement = signal and not (item_index % 19 == 0)
            quality = measurement and not (speaker_index % 11 == 0 and item_index % 4 == 0)
            metadata = not (speaker_index % 10 == 0 and item_index % 6 == 0)
            base = {"source_hit_id": f"HIT_{hit_index:04d}", "source_token_id": token_id, "corpus_id": corpus, "corpus_version": "SYN_1.0", "recording_id": f"REC_{speaker_index:02d}", "speaker_id": speaker, "session_id": f"SESSION_{speaker_index:02d}", "conversation_id": f"CONV_{(speaker_index - 1) // 2 + 1:02d}", "item_id": f"ITEM_{item_index:02d}", "condition_id": "SYN_C1" if item_index % 2 else "SYN_C2", "region": region, "style": style, "era": era, "query_term": "SYN_TARGET", "context_eligible": str(context).lower(), "signal_available": str(signal).lower(), "measurement_success": str(measurement).lower(), "quality_approved": str(quality).lower(), "metadata_complete": str(metadata).lower(), "source_interval_start_s": round(hit_index * 0.75, 3), "source_interval_end_s": round(hit_index * 0.75 + rng.uniform(.08, .22), 3), "data_status": "SYNTHETIC_TEACHING_FIXTURE"}
            hits.append(base)
            status = "matched"
            if hit_index % 29 == 0: status = "ambiguous"
            elif hit_index % 37 == 0: status = "unmatched"
            links.append({"source_token_id": token_id, "lexical_key": f"LEX_{item_index:02d}" if status == "matched" else "", "linkage_status": status, "candidate_count": 1 if status == "matched" else (2 if status == "ambiguous" else 0), "lexicon_version": "SYN_LEX_1.0", "data_status": "SYNTHETIC_TEACHING_FIXTURE"})
            if hit_index % 15 == 0:
                duplicate = dict(base); duplicate["source_hit_id"] = f"HIT_{hit_index:04d}_DUP"; duplicate["source_interval_start_s"] = round(float(base["source_interval_start_s"]) + .001, 3)
                hits.append(duplicate)
    write_tsv(CHAPTER_ROOT / "searchable_hits.tsv", hits, list(hits[0]))
    write_tsv(CHAPTER_ROOT / "linkage_table.tsv", links, list(links[0]))
    query = {"schema_version":"0.1","data_status":"SYNTHETIC_TEACHING_FIXTURE","query_id":"SYN_QUERY_001","query_expression":"query_term == 'SYN_TARGET'","corpus_versions":{"SYN_CORPUS_A":"SYN_1.0","SYN_CORPUS_B":"SYN_1.0"},"annotation_version":"SYN_ANN_1.0","normalization":"none","duplicate_key":["corpus_id","source_token_id"],"stage_order":["raw_hit","deduplicated","context_eligible","signal_available","measurement_success","quality_approved","metadata_complete","linkage_matched","final_inclusion"],"exclusion_priority":["duplicate","context_ineligible","signal_unavailable","measurement_failure","quality_rejected","metadata_missing","linkage_ambiguous","linkage_unmatched"]}
    (CHAPTER_ROOT / "query_config.yaml").write_text(yaml.safe_dump(query, sort_keys=False), encoding="utf-8")
    access = {"schema_version":"0.1","data_status":"SYNTHETIC_TEACHING_FIXTURE","profile_id":"PUBLIC_SYNTHETIC","access_mode":"bundled generated fixture","canonical_protected_paths":[],"redistribution":"fixture only","warning":"No licensed recordings, transcripts, or participant identifiers are included."}
    (CHAPTER_ROOT / "corpus_access_profile.yaml").write_text(yaml.safe_dump(access, sort_keys=False), encoding="utf-8")
    target = {"schema_version":"0.1","data_status":"SYNTHETIC_TEACHING_FIXTURE","claim":"method demonstration for a two-corpus target population","dimensions":{"region":["north","south","central"],"style":["casual","interview","read"],"era":["2010s","2020s"],"condition_id":["SYN_C1","SYN_C2"]},"minimum_included_per_cell":10,"higher_level_minimums":{"speakers":20,"conversations":10,"items":15},"interpretive_limit":"support categories are generated and cannot establish empirical representativeness"}
    (CHAPTER_ROOT / "target_population.yaml").write_text(yaml.safe_dump(target, sort_keys=False), encoding="utf-8")
    design = [
        {"corpus_id":"SYN_CORPUS_A","population":"synthetic speakers 01-18","era":"2010s","styles":"casual|interview","task":"conversation|interview","recording":"headset_48k","annotation":"manual_words","lexical_coverage":"20 generated items","measurement":"common synthetic pipeline","data_status":"SYNTHETIC_TEACHING_FIXTURE"},
        {"corpus_id":"SYN_CORPUS_B","population":"synthetic speakers 19-30","era":"2020s","styles":"casual|interview","task":"conversation|interview","recording":"tabletop_44k1","annotation":"automatic_words","lexical_coverage":"20 generated items","measurement":"common synthetic pipeline","data_status":"SYNTHETIC_TEACHING_FIXTURE"},
    ]
    write_tsv(CHAPTER_ROOT / "corpus_design.tsv", design, list(design[0]))
    compatibility = [
        {"dimension":"population","corpus_a":"synthetic speakers 01-18","corpus_b":"synthetic speakers 19-30","compatibility":"restricted","overlap_rule":"generated adults only"},
        {"dimension":"era","corpus_a":"2010s","corpus_b":"2020s","compatibility":"incompatible","overlap_rule":"no common era"},
        {"dimension":"style","corpus_a":"casual|interview","corpus_b":"casual|interview","compatibility":"compatible","overlap_rule":"casual and interview"},
        {"dimension":"task","corpus_a":"conversation|interview","corpus_b":"conversation|interview","compatibility":"compatible","overlap_rule":"matched task labels only"},
        {"dimension":"recording","corpus_a":"headset_48k","corpus_b":"tabletop_44k1","compatibility":"incompatible","overlap_rule":"no equipment equivalence"},
        {"dimension":"annotation","corpus_a":"manual_words","corpus_b":"automatic_words","compatibility":"restricted","overlap_rule":"independent boundary validation required"},
        {"dimension":"lexical_coverage","corpus_a":"20 generated items","corpus_b":"20 generated items","compatibility":"compatible","overlap_rule":"same 20 items"},
        {"dimension":"measurement","corpus_a":"common synthetic pipeline","corpus_b":"common synthetic pipeline","compatibility":"compatible","overlap_rule":"same versioned procedure"},
    ]
    for row in compatibility: row["data_status"] = "SYNTHETIC_TEACHING_FIXTURE"
    write_tsv(CHAPTER_ROOT / "cross_corpus_map.tsv", compatibility, list(compatibility[0]))
    files = sorted(path for path in CHAPTER_ROOT.iterdir() if path.is_file())
    chapter_rows = [{"artifact_id":f"CH15_SYN_{i+1:02d}","relative_path":str(path.relative_to(DATA_ROOT)),"data_status":"SYNTHETIC_TEACHING_FIXTURE","source":"generated locally by companion/scripts/generate_ch15_fixture.py","license":"CC-BY-4.0","sha256":sha256_file(path),"contains_human_data":"false"} for i,path in enumerate(files)]
    manifest = DATA_ROOT / "MANIFEST.tsv"; preserved=[]
    if manifest.exists():
        with manifest.open("r",encoding="utf-8",newline="") as source: preserved=[row for row in csv.DictReader(source,delimiter="\t") if not row["artifact_id"].startswith("CH15_")]
    write_tsv(manifest, sorted(preserved+chapter_rows,key=lambda row:row["artifact_id"]), ["artifact_id","relative_path","data_status","source","license","sha256","contains_human_data"])


if __name__ == "__main__": main()
