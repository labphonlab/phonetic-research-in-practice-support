# Exercise 3.1: Audit a theoretical variable
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import math
import parselmouth
snd = parselmouth.Sound("companion/data/ch10/synthetic_acoustics/audio/SYN_VOWEL_01.wav")
vowel = snd.extract_part(from_time=0.1, to_time=0.5, preserve_times=True)
for ceiling in (4500, 5000, 5500, 6000, 6500):
    f = vowel.to_formant_burg(
        time_step=0.01, max_number_of_formants=5,
        maximum_formant=ceiling, window_length=0.025,
        pre_emphasis_from=50.0)
    # hertz; nan if no estimate
    f1, f2 = (f.get_value_at_time(i, 0.3) for i in (1, 2))
    if math.isnan(f1) or math.isnan(f2):
        print(ceiling, "no measurement")
    else:
        print(ceiling, round(f1), round(f2))
