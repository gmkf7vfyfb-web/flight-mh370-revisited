"""Write paper/references.bib and paper/CITATIONS-LEDGER.md from handoff/citations.json.

Formats every reference in The Journal of Navigation's Harvard style, as verified in
paper/JON-RULES.md §6. Nothing is invented: a field that the project does not record is
left visibly empty and listed as an open item.
"""
import json, re, pathlib, collections, datetime

ROOT = pathlib.Path("repo2/Claude Science Project Sep 29")
PAPER = ROOT / "paper"; PAPER.mkdir(exist_ok=True)
data = json.load(open("handoff/citations.json"))
entries, summary = data["entries"], data["summary"]
TODAY = "12 October 2026"

# Davey et al. (2016) chapter-level DOIs and printed page ranges, retrieved from
# CrossRef 12 Oct 2026 (10.1007/978-981-10-0379-0_1 .. _11) and verified there.
DAVEY_CHAPTERS = [
    (1, "Introduction", "1\u20135", "Davey et al."),
    (2, "Factual Description of Accident and Available Information", "7\u20139", "Davey et al."),
    (3, "The Bayesian Approach", "11\u201317", "Davey et al."),
    (4, "Aircraft Prior Based on Primary Radar Data", "19\u201322", "Davey et al."),
    (5, "Measurement Model, Satellite Communications", "23\u201334", "Davey et al."),
    (6, "Aircraft Cruise Dynamics", "35\u201346", "Davey et al."),
    (7, "Aircraft Manoeuvre Dynamics", "47\u201354", "Davey et al."),
    (8, "Particle Filter Implementation", "55\u201361", "Davey et al."),
    (9, "Validation Experiments", "63\u201386", "Davey et al."),
    (10, "Application to the MH370 Accident", "87\u2013100", "Davey et al."),
    (11, "Ongoing Refinement", "101\u2013109", "Davey et al."),
]

ACCENT = {"'": "\u0301", "`": "\u0300", '"': "\u0308", "^": "\u0302",
          "~": "\u0303", "c": "\u0327", "v": "\u030c", "=": "\u0304"}

def detex(s):
    """Turn BibTeX accent commands into real characters: \\\"a -> a-umlaut."""
    import unicodedata as U
    def rep(m):
        acc, ch = m.group(1), m.group(2)
        comb = ACCENT.get(acc)
        return U.normalize("NFC", ch + comb) if comb else ch
    # Named commands first: the single-character accent rule below would otherwise
    # read the 'c' of \circ as a cedilla and corrupt the rest of the word.
    for a, b in (("\\circ", "\u00b0"), ("\\degree", "\u00b0"), ("\\deg", "\u00b0"),
                 ("\\times", "\u00d7"), ("\\pm", "\u00b1"), ("\\mu", "\u03bc"),
                 ("\\sigma", "\u03c3"), ("\\textdegree", "\u00b0")):
        s = s.replace(a + "{}", b).replace(a + " ", b).replace(a, b)
    s = re.sub(r"\$\s*\^?\s*(\S*?)\s*\$", r"\1", s)   # strip bare math mode
    s = re.sub(r"\\([\'`\"^~=cv])\s*\{?([A-Za-z])\}?", rep, s)
    for a, b in (("\\ss", "\u00df"), ("\\o", "\u00f8"), ("\\aa", "\u00e5"),
                 ("\\ae", "\u00e6"), ("\\&", "&"), ("\\%", "%"), ("\\_", "_")):
        s = s.replace(a, b)
    return s

def clean(s):
    s = detex((s or "").replace("{", "").replace("}", ""))
    s = s.replace("--", "\u2013")
    return re.sub(r"\s+", " ", s).strip()

def initialise(name):
    """'Davey, Samuel' -> 'Davey, S.'  |  'Griffin, David A.' -> 'Griffin, D. A.'

    JON's own reference examples give initials, never full given names. Only names
    written 'Surname, Given' are touched; a name with no comma is treated as
    corporate (an agency or data provider) and passed through unchanged.
    """
    if "," not in name:
        return name
    surname, given = name.split(",", 1)
    # A corporate name may contain a comma ('X Group, Y Subgroup'). Treat anything
    # whose leading part is more than two words, or whose trailing part is itself a
    # multi-word phrase, as corporate and leave it alone.
    if len(surname.split()) > 2 or len(given.split()) > 2:
        return name.strip()
    out = []
    for tok in given.replace(".", ". ").split():
        if not tok or not tok[0].isalpha():
            continue
        if "-" in tok:                      # Jean-Pierre -> J.-P.
            out.append("-".join(p[0].upper() + "." for p in tok.split("-") if p))
        else:
            out.append(tok[0].upper() + ".")
    return f"{surname.strip()}, {' '.join(out)}".strip().rstrip(",")

def jon_authors(raw):
    """'A and B and C' -> 'A, B and C'. Corporate names pass through."""
    parts = [initialise(clean(p)) for p in re.split(r"\s+and\s+", raw or "") if clean(p)]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]

def org_of(e):
    for k in ("institution", "organization", "publisher", "school"):
        if e.get(k):
            return clean(e[k])
    return ""

def jon_ref(e):
    a = jon_authors(e.get("author", "")) or org_of(e)
    y = clean(e.get("year", "")) or "n.d."
    t = clean(e.get("title", ""))
    ty = e["_type"]
    bits = [f"{a} ({y}). {t}." if a else f"{t} ({y})."]
    if ty == "article":
        j = clean(e.get("journal", ""))
        vol, pg = clean(e.get("volume", "")), clean(e.get("pages", ""))
        tail = j
        if vol:
            tail += f", {vol}"
        if pg:
            tail += f", {pg}"
        if tail:
            bits.append(tail + ".")
    elif ty in ("book", "inbook", "incollection", "booklet"):
        bt = clean(e.get("booktitle", ""))
        if bt and ty != "book":
            bits.append(bt + ".")
        if clean(e.get("publisher", "")):
            bits.append(clean(e["publisher"]) + ".")
    elif ty in ("techreport", "manual", "report", "standard"):
        inst, num = org_of(e), clean(e.get("number", ""))
        tail = inst + (f", {num}" if num else "")
        if tail:
            bits.append(tail + ".")
    elif ty in ("inproceedings", "conference", "proceedings"):
        bt, ad = clean(e.get("booktitle", "")), clean(e.get("address", ""))
        tail = bt + (f", {ad}" if ad else "")
        if tail:
            bits.append(tail + ".")
    elif ty in ("phdthesis", "mastersthesis"):
        kind = "PhD thesis" if ty == "phdthesis" else "Master's thesis"
        bits.append(f"{kind}, {org_of(e)}.")
    else:
        if org_of(e):
            bits.append(org_of(e) + ".")
    doi, url = clean(e.get("doi", "")), clean(e.get("url", ""))
    if doi:
        bits.append(f"https://doi.org/{doi}.")
    elif url:
        bits.append(url + ".")
    acc = clean(e.get("urldate", "")) or clean(e.get("accessed", ""))
    if (url or doi) and e["_type"] in ("misc", "manual", "standard") :
        bits.append(f"Accessed {acc}." if acc else "Accessed [DATE NOT RECORDED].")
    return " ".join(bits)

MODULE = {"hydroacoustics": "hydroacoustics", "ocean": "ocean drift / transport",
          "debris-drift": "ocean drift", "settling": "settling",
          "pleiades": "Pleiades", "end-of-flight": "end of flight",
          "seabed": "searched areas", "davey": "reproduction (Davey et al.)"}
def module_of(e):
    tags = set()
    for f in e["_files"]:
        for k, v in MODULE.items():
            if k in f:
                tags.add(v)
    return ", ".join(sorted(tags)) or "-"

# ----------------------------------------------------------------- bib output
by_key = {}
for e in entries:
    k = e["_keys"][0]
    while k in by_key:
        k += "a"
    by_key[k] = e
FIELD_ORDER = ["author", "title", "journal", "booktitle", "institution",
               "organization", "school", "publisher", "series", "volume",
               "number", "pages", "year", "address", "doi", "url", "urldate",
               "note", "howpublished", "type"]
lines = [
    "% MH370 Bayesian reconstruction - master citation library for the Journal of",
    "% Navigation paper. Generated by write_citation_outputs.py from the module",
    f"% bibliographies listed in paper/CITATIONS-LEDGER.md. Regenerated {TODAY}.",
    "%",
    "% DO NOT hand-edit: edit the module bibliography under results/ and regenerate,",
    "% so the module and the paper cannot disagree.",
    "%",
    f"% {len(entries)} entries, deduplicated from {summary['raw_entries']} raw entries",
    f"% across {len(summary['bib_files'])} module bibliographies.",
    "",
]
for k, e in by_key.items():
    lines.append(f"@{e['_type']}{{{k},")
    for f in FIELD_ORDER:
        if e.get(f):
            lines.append(f"  {f} = {{{e[f]}}},")
    lines.append("}")
    lines.append("")
(PAPER / "references.bib").write_text("\n".join(lines))

# -------------------------------------------------------------- ledger output
g_counts = collections.Counter(e["_grade"] for e in entries)
v_counts = collections.Counter(e["_verify"].split(" (")[0] for e in entries)

L = []
w = L.append
w("# Master citation ledger — MH370 paper")
w("")
w("Owner: paper drafting and citations module (`PAPER_CITATIONS_MODULE`).")
w(f"Generated {TODAY} by `write_citation_outputs.py` from `build_citation_library.py`.")
w("Companion file: `paper/references.bib` (generated from the same index — never")
w("hand-edited). Reference style follows `paper/JON-RULES.md` §6 (Harvard).")
w("")
w("## 1. What was gathered")
w("")
w("| Source | Result |")
w("|---|---|")
w(f"| Module bibliographies under `results/*.bib` | {len(summary['bib_files'])} files, "
  f"{summary['raw_entries']} raw entries |")
w(f"| After deduplication by DOI, else by first author, year and title | "
  f"**{len(entries)} entries** |")
w(f"| Repository files scanned for in-text use | {summary['scanned_files']} "
  "(`results/**/*.md`, `ARCHITECTURE.md`, `README.md`, `RUNBOOK.md`, "
  "`threads/master-prompts/`, `coordination/`, and the engine's Rust, TOML and Python) |")
w(f"| Entries whose use in the project could be traced to a file | "
  f"{summary['entries_with_usage']} of {len(entries)} |")
w(f"| Local candidate copies indexed (`~/Downloads`, `mh370-exchange`) | "
  f"{summary['local_candidates_indexed']} files |")
w("")
w("Still to be folded in, and therefore **not** represented in the counts below:")
w("Pete's Google Drive; `deskstar`; the prose ledgers `results/*-references.md` "
  "(which carry the printed pages and the per-claim provenance); "
  "`results/davey-2016-reference.md`; `results/hydroacoustics-bibliography.csv`; "
  "`results/seabed-search-references.md`.")
w("")
w("## 2. Counts by grade")
w("")
w("Grades follow the module brief §1: **official** (publisher, agency, standards body), "
  "**peer-reviewed**, **grey** (reports, theses, preprints), **unofficial** (blogs, "
  "forums, independent analysts).")
w("")
w("| Grade | Entries |")
w("|---|---|")
for g in ("official", "peer-reviewed", "grey", "unofficial"):
    w(f"| {g} | {g_counts.get(g, 0)} |")
w(f"| **total** | **{len(entries)}** |")
w("")
w("Every grade below is assigned by rule from the entry type and the publisher, "
  "institution or URL field, and each entry records the basis. **The grades are "
  "heuristic and need Pete's or architecture's confirmation on the `misc` entries in "
  "particular**, where the entry type carries no information.")
w("")
w("No entry graded **unofficial** is present in the module bibliographies. That is "
  "worth noting rather than celebrating: independent analysts' work (for example "
  "370location.org) is cited in project prose and in the hydroacoustics discussion, so "
  "either those citations are missing from the bibliographies or they are being used "
  "without being cited. See §5.")
w("")
w("## 3. Verification status")
w("")
N_DOI = sum(1 for e in entries if (e.get("doi") or "").strip())
N_NODOI = len(entries) - N_DOI
N_NOTFOUND = v_counts.get("UNVERIFIED, DOI NOT FOUND", 0)
N_VER = v_counts.get("METADATA VERIFIED", 0)
N_MIS = v_counts.get("METADATA MISMATCH", 0)
AG = collections.Counter((e.get("_crossref") or {}).get("agency")
                         for e in entries
                         if (e.get("_crossref") or {}).get("status") == "resolved")
w(f"Of **{len(entries)}** entries, **{N_DOI}** carry a DOI and **{N_NODOI}** do not. "
  f"Every DOI was looked up at CrossRef and, on a 404 there, at DataCite — "
  f"{AG.get('CrossRef', 0)} are registered with CrossRef and {AG.get('DataCite', 0)} "
  "with DataCite (datasets, data products and arXiv deposits are DataCite's, and 404 "
  "at CrossRef without being broken).")
w("")
w("| Status | Entries | Meaning |")
w("|---|---|---|")
w(f"| METADATA VERIFIED | {N_VER} | the DOI resolves and the registered title and year "
  "agree with ours |")
w(f"| METADATA MISMATCH | {N_MIS} | the DOI resolves but a field disagrees — listed in §4 |")
w(f"| UNVERIFIED, no DOI | {N_NODOI} | the entry carries no DOI, so there was nothing "
  "to check automatically |")
w(f"| UNVERIFIED, DOI not found | {N_NOTFOUND} | a DOI is recorded but neither registry "
  "knows it — these need attention, listed in §4.5 |")
w(f"| **total** | **{N_VER + N_MIS + N_NODOI + N_NOTFOUND}** | |")
w("")
w(f"Arithmetic check, so the table can be audited: {N_DOI} with a DOI "
  f"= {N_VER} verified + {N_MIS} mismatched + {N_NOTFOUND} not found; "
  f"{N_VER} + {N_MIS} + {N_NOTFOUND} + {N_NODOI} without a DOI = {len(entries)}.")
assert N_VER + N_MIS + N_NOTFOUND == N_DOI, (N_VER, N_MIS, N_NOTFOUND, N_DOI)
assert N_VER + N_MIS + N_NOTFOUND + N_NODOI == len(entries)
w("")
w("**None is yet VERIFIED against the source document** in the brief's strongest sense "
  "— that requires opening the work and checking the claim it is cited for, which "
  "happens claim by claim as the draft is written, not in bulk.")
w("")
w(f"Legitimate held copies located on this machine: {summary['entries_with_local_copy']} "
  f"candidate matches, of which {summary['entries_with_confident_copy']} are confident. "
  "Title-token matching against downloaded filenames is weak for agency reports whose "
  "filenames bear no relation to their titles, so this count is a floor, not a finding. "
  "The Drive sweep will raise it.")
w("")
w("## 4. Entries that need a decision")
w("")
w("### 4.1 Four year disagreements that are not errors")
w("")
w("CrossRef's `issued` date is the earliest registered date, which for a journal "
  "article is the online-first date. In four cases our year is the **printed issue** "
  "year and is the right one for a Harvard reference list:")
w("")
w("| Key | Our year | CrossRef print | CrossRef online | Venue |")
w("|---|---|---|---|---|")
for e in entries:
    cr = e.get("_crossref") or {}
    if cr.get("status") == "resolved" and (e.get("year") or "").strip() != cr.get("year", "") \
       and e["_verify"].startswith("METADATA VERIFIED"):
        w(f"| `{e['_keys'][0]}` | {clean(e.get('year'))} | {cr.get('year_print') or '-'} "
          f"| {cr.get('year_online') or '-'} | {clean(cr.get('container', ''))} |")
w("")
w("**No change needed.** This includes `ashton2015` — Ashton et al. in *The Journal of "
  "Navigation* — which is one of the paper's two anchor references. It is cited "
  "elsewhere in the literature as both 2014 and 2015; the printed issue is 2015 and "
  "that is what we will use. Worth stating once in the ledger so that nobody "
  "'corrects' it later.")
w("")
mis = [e for e in entries if e["_verify"].startswith("METADATA MISMATCH")]
mis_year = [e for e in mis if "year ours" in e["_verify"]]
mis_title = [e for e in mis if e not in mis_year]

w(f"### 4.2 {len(mis)} genuine mismatches against the registry")
w("")
if mis_year:
    w(f"**Year ({len(mis_year)}).** The registered title agrees, the year does not:")
    w("")
    for e in mis_year:
        cr = e.get("_crossref") or {}
        venue = clean(cr.get("container") or cr.get("publisher") or "")
        w(f"- **`{e['_keys'][0]}`** — {clean(e.get('author'))[:60]}, "
          f"*{clean(e.get('title'))[:70]}*. Ours: {clean(e.get('year')) or 'none'}; "
          f"{cr.get('agency', 'the registry')} records "
          f"{cr.get('year_print') or cr.get('year') or '-'}"
          + (f" in {venue}" if venue else "")
          + (f" {cr.get('volume')}" if cr.get("volume") else "")
          + (f", {cr.get('pages')}" if cr.get("pages") else "") + ".")
    w("")
    w("  **Recommendation:** take the year from the registry record of the version we "
      "actually cite, and keep this note so the choice stays visible. Pete's call on "
      "each. Note that a dataset's registered publication year is the year the *series* "
      "was first published, which is not the year of the product version used in a run "
      "— so for data products the run's own configuration is the better authority and "
      "the reference should name the version, not just the year.")
    w("")
if mis_title:
    w(f"**Title ({len(mis_title)}).** The DOI resolves, but to a differently titled "
      "record — in each case a data product cited under a working name rather than its "
      "registered title:")
    w("")
    for e in mis_title:
        cr = e.get("_crossref") or {}
        w(f"- **`{e['_keys'][0]}`** — ours: *{clean(e.get('title'))[:62]}*; "
          f"registered as *{clean(cr.get('title'))[:72]}* "
          f"({clean(cr.get('publisher'))}, {cr.get('year') or '-'}).")
    w("")
    w("  **Recommendation:** cite the registered title, and give the working name only "
      "if the paper needs it for continuity with the figures. A referee checking the "
      "DOI must land on the thing the reference names.")
w("")
w(f"### 4.3 The {N_NODOI} entries with no DOI")
w("")
w("These are mostly agency reports, where a DOI often does not exist. They are not "
  "suspect — but under JON's website/dataset format each needs a **URL and an access "
  "date**, and the access date is recorded for almost none of them. Entries missing "
  "both a DOI and a URL cannot be formatted in JON style at all:")
w("")
missing = [e for e in entries if not clean(e.get("doi")) and not clean(e.get("url"))]
w(f"**{len(missing)} entries have neither a DOI nor a URL:**")
w("")
for e in sorted(missing, key=lambda x: x["_keys"][0]):
    w(f"- `{e['_keys'][0]}` ({e['_type']}, {e['_grade']}) — {clean(e.get('title'))[:95]}")
w("")
w("Each needs a locator before submission. For agency reports the report number plus "
  "the issuing body is usually enough for a Harvard entry, and most of these have one; "
  "the gap is a retrievable URL for the reader.")
w("")
notfound = [e for e in entries if e["_verify"].startswith("UNVERIFIED, DOI NOT FOUND")]
if notfound:
    w(f"### 4.5 {len(notfound)} recorded DOIs that neither registry knows")
    w("")
    w("A DOI that 404s at **both** CrossRef and DataCite is either mistyped, or belongs "
      "to a third registration agency, or was never registered. Each must be opened by "
      "hand before submission; a dead DOI in a reference list is worse than none, "
      "because JON hyperlinks the reference end-list.")
    w("")
    for e in sorted(notfound, key=lambda x: x["_keys"][0]):
        w(f"- `{e['_keys'][0]}` — `{clean(e.get('doi'))}` — {clean(e.get('title'))[:80]}")
    w("")

w("### 4.4 Entries that cannot yet be formatted completely")
w("")
truncated = [e for e in entries if re.search(r"\band others\b|\bet al\b",
                                             e.get("author", ""), re.I)]
noyear = [e for e in entries if not clean(e.get("year"))]
w("JON requires full details \"even if the list of authors is extensive\" "
  "(`JON-RULES.md` §6), so an author list abbreviated in the module bibliography "
  "cannot go into the reference list as it stands.")
w("")
w(f"**{len(truncated)} entries have a truncated author list** (`and others` / `et al.` "
  "in the stored author field):")
w("")
for e in sorted(truncated, key=lambda x: x["_keys"][0]):
    w(f"- `{e['_keys'][0]}` — {clean(e.get('author'))[:80]} — "
      f"{clean(e.get('title'))[:70]}")
w("")
if noyear:
    w(f"**{len(noyear)} entries have no year**, and print as `(n.d.)`:")
    w("")
    for e in sorted(noyear, key=lambda x: x["_keys"][0]):
        w(f"- `{e['_keys'][0]}` — {clean(e.get('title'))[:90]}")
    w("")
    w("For the Boeing airport-planning document the year is on the document's own "
      "revision page; it needs reading off the copy we hold rather than guessing.")
    w("")
w("## 5. Candidate citations used in prose but absent from the library")
w("")
w("Author–date patterns appearing three or more times in project prose that match no "
  "entry, no entry key and no institution field in the library. Organisation names and "
  "product codes are mixed in with real missing sources; the point of the list is that "
  "each one is either a citation the library is missing or a phrase that should not "
  "look like a citation.")
w("")
w("| Appears as | Occurrences | My reading |")
w("|---|---|---|")
READING = {
 "OI 2018": "Ocean Infinity's 2018 search — a real citable source (its operations "
            "report / ATSB record), and the single most-used uncited string in the project",
 "Infinity 2018": "same as above, matched on the second word",
 "OI 2025": "Ocean Infinity's 2025 search resumption — citable, and current",
 "Infinity 2025": "same as above",
 "Vergoz 2021": "hydroacoustic source-localisation literature — a real missing entry",
 "Nielsen 2021": "hydroacoustics — a real missing entry",
 "Large 2019": "**Pete's own dissertation.** Must be in the library",
 "Nesterov 2018": "drift / windage literature — real missing entry",
 "Chapman 1988": "underwater acoustics — real missing entry",
 "Breivik 2008": "leeway / windage literature — real missing entry",
 "Breivik 2011": "leeway / windage literature — real missing entry",
 "Maximenko 2018": "surface-drift climatology — real missing entry",
 "Miron 2019": "transition-matrix drift modelling — real missing entry",
 "Heaney 1991": "long-range acoustic propagation — real missing entry",
 "LaCasce 2008": "statistics of Lagrangian dispersion — real missing entry",
 "Matsumoto 2016": "hydroacoustics — real missing entry",
 "Jansen 2016": "check which Jansen; likely drift or acoustics",
 "Dr\u00e9villon 2013": "Mercator/PSY ocean analysis system — real missing entry",
 "ETOPO 2022": "NOAA ETOPO 2022 bathymetry — a data product needing a dataset entry",
 "Record 2017": "probably 'the record' in prose, not a citation — check",
 "Atlas 2023": "likely a data-product name (an atlas), not an author",
 "HL 2019": "a product or run code, not a citation",
 "RA 2021": "a reanalysis product code, not a citation",
 "GA 2017": "Geoscience Australia 2017 — bathymetry survey data, citable",
 "JASDF 2019": "check: an organisation abbreviation in prose",
 "SUS 2003": "the SUS charge reference data — needs a proper source entry",
 "Generator 2026": "our own generated output, not a citation",
}
for name, cnt in summary["unmatched_inline_top"]:
    w(f"| {name} | {cnt} | {READING.get(name, 'not yet assessed')} |")
w("")
w("**Finding.** On this evidence the library is roughly 15 to 20 entries short of what "
  "the project's own prose already relies on, and the largest single gap is the Ocean "
  "Infinity searches, referred to several hundred times and cited nowhere. The searched-"
  "areas likelihood rests on them. Closing this is the next citation task.")
w("")
w("## 6. The library")
w("")
w("Printed pages are deliberately **not** a column here. JON's Harvard style admits an "
  "in-text page only for a direct quotation (`JON-RULES.md` §6), and pages in this "
  "project are a property of a *claim*, not of a reference. They live with the claim in "
  "the module prose ledgers and will be carried into the reference draft. A "
  "reference-level page column would invite exactly the detachment of claim from page "
  "that it appears to prevent.")
w("")
w("| Key | Reference (JON Harvard style) | Grade | Verification | Used by | Copy held |")
w("|---|---|---|---|---|---|")
for k, e in sorted(by_key.items(), key=lambda kv: kv[0].lower()):
    ver = e["_verify"].split(" (")[0]
    used = module_of(e)
    nfiles = len(e["_used_in"])
    used += f" ({nfiles} file{'s' if nfiles != 1 else ''})" if nfiles else " (no use traced)"
    copy = "yes" if e.get("_local_confident") else ("candidate" if e["_local_copy"] else "-")
    w(f"| `{k}` | {jon_ref(e)} | {e['_grade']} | {ver} | {used} | {copy} |")
w("")
w("## 6a. Davey et al. (2016) has chapter-level DOIs — and they resolve the page conflict")
w("")
w("Every chapter of the book is separately registered with its own DOI and its own "
  "printed page range. Retrieved from CrossRef and verified 12 October 2026:")
w("")
w("| Ch. | Title | Printed pages | DOI |")
w("|---|---|---|---|")
for n, title, pg, _au in DAVEY_CHAPTERS:
    w(f"| {n} | {title} | {pg} | `10.1007/978-981-10-0379-0_{n}` |")
w("")
w("**This is the way out of the conflict in §6.** A chapter citation is a *reference*, "
  "not an in-text page, so it is fully Harvard-compliant, and it is far more precise "
  "than citing a 109-page book. The particle filter implementation is chapter 8, "
  "pp. 55\u201361; the satellite communications measurement model is chapter 5, "
  "pp. 23\u201334; the manoeuvre dynamics our sampler modifies are chapter 7, "
  "pp. 47\u201354. Each can be cited as its own reference-list entry with a resolvable "
  "DOI and its printed pages, which is what the project's traceability rule actually "
  "wants.")
w("")
w("Recommended practice for the paper: cite `(Davey et al., 2016)` for the work as a "
  "whole and the chapter entry where a specific model element is meant. The printed "
  "page ranges above also give an independent check on the project's "
  "printed-page = PDF-page \u2212 13 rule for this book.")
w("")
w("## 6b. Legitimate copies held, by provenance")
w("")
w("| Source | Copy held | Provenance | Citable pagination |")
w("|---|---|---|---|")
w("| Davey et al. (2016) | publisher PDF | Pete's Google Drive; CC BY-NC 4.0 | printed "
  "pages, from the running headers |")
w("| Holland (2018) | author's accepted version | **green open access, arXiv:1702.02432v3, "
  "15 Jan 2018**, retrieved via Unpaywall 12 Oct 2026 | **NOT the printed pagination.** "
  "The copy is numbered 1\u201310; the printed article is *IEEE Aerospace and Electronic "
  "Systems Magazine* 33(2), 24\u201333. Locate quotations by section, not page, unless "
  "the published version is obtained |")
w("| Large (2019) | `~/Downloads/Dissertation.pdf`, 285 pp. | Pete's own work, published "
  "open access by him; he confirmed on 12 Oct 2026 that there are no restrictions | its "
  "own printed folios; note that the text layer has a broken character map, so quotations "
  "must be read from the rendered page |")
w("")
w("## 7. Open items")
w("")
w("1. Fold in the prose ledgers `results/*-references.md`, which carry printed pages, "
   "per-claim provenance and the module's own verification notes. The `.bib` files are "
   "the skeleton; the prose files are where the work is.")
w("2. Sweep Pete's Google Drive and `deskstar` for held copies and for sources cited "
   "nowhere in the repository.")
w("3. Close the gaps in §5, starting with Ocean Infinity 2018 and 2025, and Large (2019).")
w("4. Record an access date for every URL-only entry (§4.3).")
w("5. Confirm the heuristic grades on the 21 `misc` entries.")
w("6. Decide the dataset, software and thesis reference formats with the Editorial "
   "Office (`JON-RULES.md` §6), then regenerate.")
w("7. Add the engine itself as a citable software entry once a release or commit is "
   "nominated for the paper.")
w("")
w("---")
w("")
w(f"*Regenerate with `python build_citation_library.py && python write_citation_outputs.py`. "
  f"Last run {TODAY}.*")

(PAPER / "CITATIONS-LEDGER.md").write_text("\n".join(L) + "\n")
print("references.bib:", (PAPER/'references.bib').stat().st_size, "bytes,", len(by_key), "entries")
print("CITATIONS-LEDGER.md:", (PAPER/'CITATIONS-LEDGER.md').stat().st_size, "bytes")
print("no DOI and no URL:", len(missing))
print("\nsample formatted refs:")
for k in list(by_key)[:3]:
    print("  -", jon_ref(by_key[k])[:160])
