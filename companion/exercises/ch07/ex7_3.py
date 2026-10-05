# Exercise 7.3: Build a session record
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import yaml, wave
base = "companion/data/ch07/synthetic_recordings/"
meta = yaml.safe_load(open(base + "recording_session_metadata.yaml"))
required = ["session", "claim_requirements", "signal_chain", "file_configuration",
            "checks", "post_session", "pre_departure_decision"]
print("missing sections:", [k for k in required if k not in meta])
placeholders = [k for k, v in meta["signal_chain"].items() if str(v).startswith(("NOT_APPLICABLE", "UNKNOWN"))]
print("signal_chain fields not applicable or unknown:", len(placeholders))
with wave.open(base + "synthetic_good.wav") as w:
    cfg = meta["file_configuration"]
    print("header matches record:", w.getframerate() == cfg["sample_rate_hz"],
          8 * w.getsampwidth() == cfg["bit_depth"], w.getnchannels() == cfg["channel_count"])
