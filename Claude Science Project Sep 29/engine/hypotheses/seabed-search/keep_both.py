#!/usr/bin/env python3
"""Resolve a coordination-file conflict by KEEPING BOTH entries, in time order.

    python hypotheses/seabed-search/keep_both.py <path to conflicted .md>

The coordination files are append-only inboxes shared by every module session, so two sessions
appending at once conflict on the last hunk nearly every time. The rule in the searched-areas brief is
that both entries are kept in chronological order and neither side is ever dropped; this automates it
rather than leaving it to a hand edit under time pressure. Each side is ordered by the first
`YYYY-MM-DD ... HH:MM` it contains, falling back to the order git gave them.

Exits non-zero if any conflict marker survives, so it can be used in a commit script.
"""
import pathlib
import re
import sys

TS = re.compile(r"(\d{4}-\d{2}-\d{2}).{0,4}?(\d{2}:\d{2})")


def stamp(block):
    for line in block:
        m = TS.search(line)
        if m:
            return m.group(1) + " " + m.group(2)
    return ""


def resolve(path):
    lines = pathlib.Path(path).read_text().split("\n")
    out, i, kept = [], 0, 0
    while i < len(lines):
        if not lines[i].startswith("<<<<<<<"):
            out.append(lines[i]); i += 1; continue
        mid = next(k for k in range(i, len(lines)) if lines[k].startswith("======="))
        end = next(k for k in range(mid, len(lines)) if lines[k].startswith(">>>>>>>"))
        a, b = lines[i + 1:mid], lines[mid + 1:end]
        first, second = (a, b) if stamp(a) <= stamp(b) else (b, a)
        out += first + second
        kept += 1
        i = end + 1
    text = "\n".join(out)
    if any(text.startswith(m) or ("\n" + m) in text for m in ("<<<<<<<", "=======", ">>>>>>>")):
        sys.exit(f"{path}: conflict markers survive")
    pathlib.Path(path).write_text(text)
    print(f"{path}: kept both sides of {kept} conflict(s), in time order")


if __name__ == "__main__":
    for p in sys.argv[1:] or sys.exit(__doc__):
        resolve(p)
