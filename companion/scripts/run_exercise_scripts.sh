#!/bin/sh
# Run every Python and R exercise script in companion/exercises/ in a clean
# working directory. Each run sees the companion package at ./companion (as in
# the book's paths) plus that chapter's example inputs in ./examples copied to
# the working directory, standing in for the files a learner would create.
# Shell scripts (Git, Quarto, Montreal Forced Aligner steps) are not run here.
set -eu

root_dir=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
work_root=$(mktemp -d)
trap 'rm -rf "$work_root"' EXIT
failures=0
count=0

for script in "$root_dir"/companion/exercises/ch*/ex*.py "$root_dir"/companion/exercises/ch*/ex*.R; do
    chapter_dir=$(dirname "$script")
    name=$(basename "$script")
    work="$work_root/${name%.*}_${name##*.}"
    mkdir -p "$work"
    ln -s "$root_dir/companion" "$work/companion"
    if [ -d "$chapter_dir/examples" ]; then
        cp "$chapter_dir"/examples/* "$work"/
    fi
    # Exercise 20.2 takes the access route as its argument.
    args=""
    case "$name" in
        ex20_2.py) args="public" ;;
    esac
    count=$((count + 1))
    case "$name" in
        *.py) runner="python3" ;;
        *.R) runner="Rscript --vanilla" ;;
    esac
    if (cd "$work" && $runner "$script" $args > output.txt 2> errors.txt); then
        printf 'PASS %s\n' "${script#"$root_dir"/}"
    else
        failures=$((failures + 1))
        printf 'FAIL %s\n' "${script#"$root_dir"/}"
        tail -n 5 "$work/errors.txt"
    fi
done

printf 'exercise_scripts=%s failures=%s\n' "$count" "$failures"
[ "$failures" -eq 0 ]
