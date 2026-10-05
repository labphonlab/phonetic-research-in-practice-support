# Exercise 9.1: Turn a label into a measurement rule
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import yaml
tpl = yaml.safe_load(open("companion/templates/annotation_schema.yaml"))
mine = yaml.safe_load(open("my_schema.yaml"))
def paths(d, p=""):
    for k, v in d.items():
        if isinstance(v, dict): yield from paths(v, p + k + ".")
        else: yield p + k, v
print("empty:",
      [k for k, v in paths(mine) if v in ("", None, [])])
print("missing:", sorted({k for k, _ in paths(tpl)}
                         - {k for k, _ in paths(mine)}))
