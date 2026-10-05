# Exercise 7.4: Design an accessible remote protocol
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import numpy as np, pandas as pd
ev = pd.read_csv("companion/data/ch07/synthetic_recordings/timing_events.tsv", sep="\t")
lag_ms = (ev.observed_time_s - ev.expected_time_s) * 1000
slope, offset = np.polyfit(ev.expected_time_s, lag_ms, 1)
print(f"offset at t = 0: {offset:.2f} ms; drift: {slope:.2f} ms per s "
      f"({slope * 3600 / 1000:.2f} s per hour)")
