#!/usr/bin/env python3
"""Supplement to "ISO Sept 28 Status": copy the downloaded third-party inputs into inputs/.

Pete asked on 29 Sep 2026 for the left-out downloaded items to be included. Everything without an
explicit restrictive notice is copied, with the MH371 truth file labelled off-limits to the MH371
control. Items with an explicit notice (a paid standard, "all rights
reserved" manuals) are linked to their public sources instead. Files too large for plain Git
(over 95 MB) are listed for the Hugging Face companion dataset or regeneration.
"""
import csv, hashlib, shutil
from pathlib import Path
import pymupdf

INPUTS = Path("/jackbox/home/MH370-inputs")
REPO = Path("/jackbox/home/MH370")
OUT = Path("/jackbox/home/MH370-export/ISO Sept 28 Status")
DEST = OUT / "inputs"
MAX = 95_000_000

# Linked instead of copied: path in MH370-inputs -> (reason, where to get it).
LINKED = {
    "fuel/ulich-9M-MRO-fuel-model-v5.6-public.xlsm": (
        "its colour key says some cells are 'from a Boeing FPPM from a confidential source' (provenance, not a stated restriction); linked pending Pete's decision",
        "author's public copy: https://drive.google.com/file/d/1Wt9DOU0Z53W7NERzSsK2sxcyrojmN7Sq"),
    "papers/aero/bada-standard-licence-information.pdf": ("EUROCONTROL, all rights reserved", "https://www.eurocontrol.int/model/bada"),
    "papers/aero/bada4-licence.pdf": ("EUROCONTROL, all rights reserved", "https://www.eurocontrol.int/model/bada"),
    "papers/aero/overview-bada-apm.pdf": ("EUROCONTROL, all rights reserved", "https://www.eurocontrol.int/model/bada"),
    "papers/aero/eurocontrol-user-guide-bada-access.pdf": ("(c) EUROCONTROL", "https://www.eurocontrol.int/model/bada"),
    "papers/aero/eurocontrol-showcase-summit-bada-latest-evolutions.pdf": ("EUROCONTROL presentation", "https://www.eurocontrol.int/model/bada"),
    "papers/aero/cwl.pdf": ("(c) The MathWorks", "MathWorks documentation"),
    "papers/aero/piano-x-guide.pdf": ("(c) Lissys Ltd", "https://www.lissys.uk/PianoX.html"),
}
# Their text extracts follow the same rule.
for pdf in list(LINKED):
    if pdf.endswith(".pdf"):
        txt = pdf[:-4] + ".txt"
        LINKED.setdefault(txt, ("text extract of " + Path(pdf).name, LINKED[pdf][1]))

REDACT = {"antenna/ball-airlink-hgas-spec-compilation.pdf": "ARINC CHARACTERISTIC 741"}
BIG_PUBLIC = {"ocean": "CMEMS/NASA/CSIRO/NOAA public sources; .sources/ocean-drift/ scripts",
              "imos-acoustic": "s3://imos-data/IMOS/ANMN/Acoustic/MH370.zip (AODN, CC BY 4.0)"}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while b := f.read(1 << 22):
            h.update(b)
    return h.hexdigest()


def main():
    DEST.mkdir(exist_ok=True)
    rows = []
    for p in sorted(INPUTS.rglob("*")):
        if p.is_symlink() or not p.is_file():
            continue
        rel = p.relative_to(INPUTS).as_posix()
        top = rel.split("/")[0]
        size = p.stat().st_size
        if rel in LINKED:
            reason, where = LINKED[rel]
            rows.append([rel, size, sha256(p), "linked", reason, where])
        elif top in BIG_PUBLIC or size > MAX:
            rows.append([rel, size, sha256(p), "too large for plain Git", "public; see source",
                         BIG_PUBLIC.get(top, "Hugging Face companion dataset on request")])
        elif rel in REDACT:
            doc = pymupdf.open(p)
            drop = [i for i in range(len(doc)) if REDACT[rel] in doc[i].get_text()]
            for i in reversed(drop):
                doc.delete_page(i)
            target = DEST / (rel[:-4] + "-without-ARINC-page.pdf")
            target.parent.mkdir(parents=True, exist_ok=True)
            doc.save(target)
            rows.append([rel, size, sha256(p), "copied, redacted",
                         f"page(s) {[i + 1 for i in drop]} of ARINC Characteristic 741 Part 1 removed (paid standard)",
                         target.relative_to(OUT).as_posix()])
        else:
            target = DEST / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
            note = ("MH371 TRUTH: off-limits to the MH371 blind control; only its scorer may read it"
                    if top == "acars" else "")
            rows.append([rel, size, sha256(p), "copied", note, target.relative_to(OUT).as_posix()])
    # Weather grids from the code repository's data/: the small ones copied, the large ones listed.
    for p in sorted((REPO / "data").glob("*.bin")):
        rel = f"repo-data/{p.name}"
        if p.stat().st_size <= 50_000_000:
            target = DEST / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
            rows.append([rel, p.stat().st_size, sha256(p), "copied", "place in MH370/data/", target.relative_to(OUT).as_posix()])
        else:
            rows.append([rel, p.stat().st_size, sha256(p), "too large for plain Git",
                         "regenerable (.sources/era5-weather/extend.py, .sources/weather-sensitivity/)",
                         "Hugging Face companion dataset on request"])
    (DEST / "MH371-TRUTH-WARNING.txt").write_text(
        "inputs/acars/ holds the ACARS workbook, which contains the MH371 truth track.\n"
        "The MH371 known-flight control is blind: only its scorer (report/mh371_score.py) may read that\n"
        "file. No agent building, configuring or tuning the estimator may open it or any copy of it\n"
        "(this folder, mh371-acars.xlsx at the repository root, or the Hugging Face dissertation\n"
        "spreadsheets).\n")
    with open(OUT / "data" / "INPUTS_PUBLICATION.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["path_in_MH370-inputs", "bytes", "sha256", "status", "note", "where"])
        w.writerows(rows)
    counts = {}
    for r in rows:
        counts[r[3]] = counts.get(r[3], 0) + 1
    print(counts, round(sum(r[1] for r in rows if r[3].startswith("copied")) / 1e6, 1), "MB copied")


if __name__ == "__main__":
    main()
