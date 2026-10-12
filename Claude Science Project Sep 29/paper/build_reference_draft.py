"""Build paper/REFERENCE-DRAFT.md and paper/reference-draft.tex.

The reference draft is a LIVING INTERNAL DOCUMENT, not the paper. It may carry fuller
mathematics than the paper will, and anything in it that is not for the paper is marked.

Every equation, label and number in the generated methodology and results sections is
copied from a project note under results/, via handoff/methods_raw.json, which is an
extraction of those notes. Nothing is retyped from memory and nothing is invented: if a
note does not give an equation, no equation appears.

Re-runnable:  python build_citation_library.py && python build_reference_draft.py
"""
import json, re, pathlib, collections, datetime

ROOT = pathlib.Path("repo2/Claude Science Project Sep 29")
PAPER = ROOT / "paper"; PAPER.mkdir(exist_ok=True)
TODAY = "12 October 2026"
raw = json.load(open("handoff/methods_raw.json"))
cit = json.load(open("handoff/citations.json"))

# --------------------------------------------------------------- parse extracts
def parse(text):
    """Block format -> list of element dicts. Tolerant: unknown lines are ignored."""
    els, cur, mode, buf = [], None, None, {}
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("ELEMENT:"):
            cur = {"element": s[8:].strip(), "taxonomy": "", "status": "", "davey": "",
                   "eqs": [], "results": [], "gaps": [], "sources": []}
            els.append(cur); mode = None; continue
        if cur is None:
            continue
        if s == "EQ":
            mode, buf = "eq", {}; continue
        if s == "ENDEQ":
            if buf.get("LATEX"): cur["eqs"].append(buf)
            mode, buf = None, {}; continue
        if s == "RESULT":
            mode, buf = "res", {}; continue
        if s == "ENDRESULT":
            if buf.get("CLAIM"): cur["results"].append(buf)
            mode, buf = None, {}; continue
        m = re.match(r"^([A-Z]+):\s*(.*)$", s)
        if not m:
            if mode and buf:                      # continuation of the previous field
                k = list(buf)[-1]; buf[k] = (buf[k] + " " + s).strip()
            continue
        k, v = m.group(1), m.group(2).strip()
        if mode in ("eq", "res"):
            buf[k] = v
        elif k == "TAXONOMY": cur["taxonomy"] = v
        elif k == "STATUS":   cur["status"] = v
        elif k == "DAVEY":    cur["davey"] = v
        elif k == "GAP":      cur["gaps"].append(v)
        elif k == "SOURCE":   cur["sources"].append(v)
    return els

DOC_TITLE = {
 "results/core-model-stages.md": "Core filter: staged model changes",
 "results/debris-drift-methods-draft.md": "Ocean surface drift of recovered debris",
 "results/hydroacoustics-methods-draft.md": "Hydroacoustics",
 "results/pleiades-methods-draft.md": "Pl\u00e9iades conditional hypothesis",
 "results/seabed-search-methods-draft.md": "Searched areas (disconfirming evidence)",
 "results/settling-methods-draft.md": "Impact to seafloor (settling)",
 "results/eof-impact-tau-method-oct11.md": "End of flight: impact dissipation duration",
 "results/davey-2016-reference.md": "Reproduction audit of the published model",
 "results/davey-ch11-reproduction.md": "Reproduction of the published refinement chapter",
 "results/composer-pass1-run-c.md": "Composer: first composed pass",
}
parsed, failed = {}, {}
for d, t in raw.items():
    if t.startswith("__ERROR__") or not t.strip():
        failed[d] = t[:200]; continue
    els = parse(t)
    if els: parsed[d] = els
    else: failed[d] = "no ELEMENT block recovered"

TAX_ORDER = ["REPRODUCTION", "UPDATE", "MODIFICATION", "EXTENSION", ""]
def tax_of(e):
    for t in TAX_ORDER[:-1]:
        if e["taxonomy"].upper().startswith(t): return t
    return "UNCLASSIFIED"
def status_of(e):
    for s in ("BUILT", "SPECIFIED", "INTENDED", "MIXED"):
        if e["status"].upper().startswith(s): return s
    return "UNSTATED"

# ----------------------------------------------- coverage register, read verbatim
arch = (ROOT / "ARCHITECTURE.md").read_text()
greg = []
for line in arch.splitlines():
    m = re.match(r"^\|\s*(G\d{1,2})\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|",
                 line)
    if m:
        greg.append(tuple(x.strip() for x in m.groups()))
open_items = []
m = re.search(r"\n## Still open\n(.*?)\n\n\n", arch, re.S)
if m:
    for om in re.finditer(r"^\d+\.\s+(.*?)(?=\n\d+\.|\Z)", m.group(1), re.S | re.M):
        open_items.append(re.sub(r"\s+", " ", om.group(1)).strip())

build_status = []
for line in arch.splitlines():
    m = re.match(r"^\|\s*(\d\s+[a-z ]+)\s*\|\s*([^|]*)\|\s*([^|]*)\|", line)
    if m and "interface" not in line:
        build_status.append(tuple(x.strip() for x in m.groups()))

# ------------------------- build status measured from the code, not from prose
def loc(*globs):
    n, files = 0, []
    for g in globs:
        for p in ROOT.glob(g):
            if p.is_file():
                try:
                    n += len(p.read_text(errors="replace").splitlines()); files.append(p)
                except Exception:
                    pass
    return n, len(files)

MEASURED = []   # (element, where, lines, files, verdict)
for name, globs in [
    ("Core filter", ("engine/crates/geo/src/*.rs", "engine/crates/satcom/src/*.rs",
                     "engine/crates/flight/src/*.rs", "engine/crates/mh370/src/*.rs")),
    ("End of flight", ("engine/hypotheses/end-of-flight/**/*.rs",)),
    ("Pl\u00e9iades", ("engine/hypotheses/pleiades/**/*.rs",)),
    ("Searched areas", ("engine/hypotheses/seabed-search/**/*.rs",)),
    ("Composer", ("engine/crates/compose/src/*.rs", "engine/crates/compose/examples/*.rs")),
    ("Shared ocean transport", ("engine/crates/ocean/src/*.rs",)),
    ("Hydroacoustics", ("results/hydroacoustics-audit/scripts/*.py",)),
    ("Antenna gain (parked)", ("engine/hypotheses/antenna-gain/**/*.rs",)),
    ("Arc kernel (placeholder)", ("engine/hypotheses/arc-kernel/**/*.rs",)),
]:
    n, f = loc(*globs)
    MEASURED.append((name, globs[0].rsplit("/", 1)[0], n, f))

compose_rejected = "compose" in (ROOT / "engine/crates/mh370/src/main.rs").read_text()
hyp_dirs = sorted(p.name for p in (ROOT / "engine/hypotheses").glob("*")
                  if (p / "hypothesis.toml").exists())
no_module = [m for m in ("debris-drift", "settling", "hydroacoustics") if m not in hyp_dirs]

# ---------------------------------------------------------------- prose sections
LIT = r"""
Every source named here is in `paper/CITATIONS-LEDGER.md` with its grade and its
verification status. Nothing is cited here that is not in that ledger.

### 1.1 The work this paper reproduces and extends

The direct antecedent is Davey, Gordon, Holland, Rutten and Williams (2016), the Defence
Science and Technology Group's Bayesian reconstruction of the flight, published open
access by Springer under CC BY-NC 4.0. It is a particle filter over aircraft state driven
by the Inmarsat burst timing and frequency offsets, with a prior formed from primary radar
and a manoeuvre model of random turns and speed changes. Its chapters carry separate
digital object identifiers and printed page ranges, so the paper can cite a specific
element precisely: the satellite communications measurement model is chapter 5, printed
pages 23 to 34; cruise dynamics chapter 6, 35 to 46; manoeuvre dynamics chapter 7, 47 to
54; the particle filter implementation chapter 8, 55 to 61; the validation experiments
chapter 9, 63 to 86; the application to the accident chapter 10, 87 to 100; and the
ongoing refinement chapter 11, 101 to 109.

Two features of that work set the agenda for this one. It assumes infinite fuel inside the
filter and applies fuel as an after-the-fact censor on trajectories. And it treats the two
transmissions at 00:19 unevenly: both burst timing offsets are used, neither burst
frequency offset is, and the anomalous second timing offset is used only after a log-on
correction.

The measurement models themselves come from Ashton, Shuster Bruce, Colledge and Dickinson
(2015) in this journal, which is the published account of the Inmarsat analysis and the
source of the satellite ephemeris and the offset definitions the filter uses.

The treatment of the final two transmissions rests on Holland (2018). That paper
establishes, from satellite data unit bench tests and four previous log-ons of the same
airframe, that this unit's frequency offset is initially too high at log-on and then
decays to a steady value over a few minutes; and it bounds the steady-state equivalent
offsets at 00:19 and the descent rates they imply. Its bench-test evidence is an
unpublished internal study of the flight path reconstruction group, inspectable only
through Holland's summary of it — a limitation this paper states rather than conceals.

### 1.2 Bayesian search and the comparable case

The methodological precedent for turning a posterior into a search plan is Stone, Keller,
Kratzke and Strumpfer (2014) on Air France 447, which is the standard reference for
combining dissimilar evidence — flight dynamics, acoustic beacons, drift of recovered
bodies and debris, and unsuccessful search coverage — into one probability map, and for
the proposition that the failure of a search is itself evidence. The treatment of searched
areas here follows that logic.

Model comparison follows Kass and Raftery (1995) for the interpretation of Bayes factors,
and the convergence and effective-sample-size diagnostics are reported against a
replicate-count-dependent split-half floor established within the project, because the
published work states no quantitative convergence criterion at all.

### 1.3 Drift of the recovered debris

The authoritative drift work for this accident is Griffin, Oke and Jones (2016, 2017), the
CSIRO reports that modelled the drift of recovered items with an ocean reanalysis and
measured the leeway of a genuine flaperon section. The treatment here is an update rather
than a new method: more recovered items, several ocean products rather than one, and
explicit marginalisation over windage and Stokes drift. The supporting literature is the
leeway and windage line — Breivik and colleagues, Sutherland and colleagues (2020) on
evaluating leeway coefficients against operational prediction systems, and Durgadoo and
colleagues (2021) on strategies for simulating marine debris drift. Ocean products used
are documented in the project's data manifest and cited as datasets.

### 1.4 Hydroacoustics

The possibility that the impact was recorded by the hydroacoustic stations of the
International Monitoring System has been examined by Duncan, Gavrilov and McCauley (2014)
for this accident, and the physics of impact-generated acoustic and acoustic-gravity waves
by Kadri (2019, 2024). Metz, Obana and Fukao (2023) is the clearest demonstration that a
remote hydroacoustic detection of an aircraft crash is achievable in principle, and Duncan
and Dall'Osto (2023) treat the dependence of long-range detection on propagation
conditions and impact parameters. Propagation modelling follows the standard references —
Jensen, Kuperman, Porter and Schmidt (2011) for computational ocean acoustics, Collins
(1993) for the split-step Pad\'e parabolic equation, Porter (1992) for normal modes, and
Francois and Garrison (1982) for absorption. Calibration sources are the explosive
source-level work of Gaspin and Shuler (1971) and the Indian Ocean calibration experiments
of Blackman and colleagues (2004).

This paper's hydroacoustic contribution is predictive, not evidential, and the Discussion
states the calibration gaps that make it so.

### 1.5 Remote sensing of debris

The official record of the satellite imagery analysis is Minchin, Mueller, Lewis, Byrne
and Tran (2017), Geoscience Australia Record 2017/013, which reports the analysis of the
Pl\'eiades 1A imagery. The conditional hypothesis in this paper is built on that record.

### 1.6 The official record

The Australian Transport Safety Bureau's series under investigation AE-2014-054 defines
the underwater search areas and reports the operational search, and the Malaysian safety
investigation report of 2018 is the factual record of the flight and of the recovered
debris. These are cited as the official sources for the data the estimator consumes and
for the searched areas it conditions on.

### 1.7 What the literature does not settle

Three things this paper must therefore argue rather than cite. First, whether the
reconstruction is sensitive to the fuel model, which the published filter did not carry
inside the likelihood. Second, whether the final two transmissions should be scored at
all, and under which cause, where the literature offers named hypotheses but no
resolution. Third, whether a hydroacoustic non-detection carries information, which
depends on a transmission-loss calibration that does not yet exist.
"""

HOWTO = r"""
**This document is not the paper.** It is the internal reference from which the paper is
written. It may carry fuller mathematics than the paper will, and anything in it that is
not intended for the paper is marked **not for the paper**.

**What the labels mean.** Every element is classified on two axes, following the agreed
taxonomy:

- against the published work — **REPRODUCTION** (Davey et al. as published), **UPDATE**
  (same element, better data or product), **MODIFICATION** (same element, changed
  assumption or method), **EXTENSION** (an element the published work does not have);
- against reality — **BUILT** (in code and run), **SPECIFIED** (designed, not run),
  **INTENDED** (discussed only).

**Where the content comes from.** The classification, the equations, the result claims and
the caveat labels in sections 2 and 3 are extracted from the project notes under
`results/` and are reproduced as those notes state them. Caveat labels are **verbatim**.
The coverage register in section 4 and the open items in section 5 are copied from
`ARCHITECTURE.md`. The build status in section 2.1 is measured from the code in this
checkout. No equation appears unless a note gives it; no number is retyped from memory.

**Reading the result claims.** A claim carries its own labels and its source artifact. A
claim with a label such as "not converged" or "PROVISIONAL" is reported here as a finding
at that strength and not at any greater strength. Negative results are kept.
"""

# ------------------------------------------------------------------- emit markdown
M = []
w = M.append
w("# Reference draft — MH370 Bayesian reconstruction")
w("")
w("**Internal reference document. Not the paper. Not for circulation outside the project.**")
w("")
w(f"Owner: paper drafting and citations module. Generated {TODAY} by "
  "`build_reference_draft.py`. Target journal: *The Journal of Navigation*; its verified "
  "rules are in `paper/JON-RULES.md`.")
w("")
w("## 0. How to read this document")
w(HOWTO)
w("## 1. Literature summary")
w(LIT)
w("## 2. Methodology, end to end")
w("")
w("The chain runs from the 18:01:49 radar prior, through the core particle filter on the "
  "Inmarsat handshakes, to the end-of-flight stage and impact, then to the impact-level "
  "modules and the composer. The order below follows that chain. The classification of "
  "each element against the published work is given first, because it determines how much "
  "the paper must say: a reproduction is cited, an extension is derived.")
w("")
w("### 2.1 Build status, measured from the code in this checkout")
w("")
w("| Element | Where | Lines of code | Files |")
w("|---|---|---|---|")
for name, where, n, f in MEASURED:
    w(f"| {name} | `{where}` | {n:,} | {f} |")
w("")
w(f"Hypothesis directories carrying a `hypothesis.toml`: {', '.join('`'+h+'`' for h in hyp_dirs)}.")
w("")
if no_module:
    w("**No engine hypothesis module exists for " +
      ", ".join("`"+m+"`" for m in no_module) +
      ".** Their methods are written up as drafts under `results/` and their analysis runs "
      "as Python under `results/`, so they are SPECIFIED as engine modules while being "
      "partly BUILT as analysis. The paper must not describe them as integrated modules.")
    w("")
w("**A discrepancy that must be resolved before any status claim is published.** "
  "`ARCHITECTURE.md` carries a table headed \"Build status, honestly\" which states:")
w("")
w("| stage | interface | model |")
w("|---|---|---|")
for a, b, c in build_status:
    w(f"| {a} | {b} | {c} |")
w("")
w("That table is **materially out of date** for stages 2 to 4, and the paper would be "
  "wrong to quote it. Measured against the code today: the end-of-flight module is "
  f"{dict((m[0], m[2]) for m in MEASURED)['End of flight']:,} lines, not a placeholder; "
  "two impact-level modules exist as hypothesis crates (Pléiades and searched areas); and "
  "the composer exists as `engine/crates/compose` with worked `pass0` and `pass1` "
  "examples and two composed result notes under `results/`. "
  "The table's specific evidence remains true — `crates/mh370/src/main.rs` still rejects a "
  "`[[compose]]` section — but that is a statement about the runner's configuration path, "
  "not about whether a composer exists. Both facts need stating together: **the composer "
  "is built as a separate crate and has been run; it is not wired into the main runner's "
  "`[[compose]]` configuration.**")
w("")

by_tax = collections.OrderedDict((t, []) for t in ["REPRODUCTION", "UPDATE",
                                                   "MODIFICATION", "EXTENSION",
                                                   "UNCLASSIFIED"])
for d, els in parsed.items():
    for e in els:
        by_tax[tax_of(e)].append((d, e))

TAX_INTRO = {
 "REPRODUCTION": ("Davey et al. as published. **The paper gives a short summary and "
                  "chapter citations here, not a re-derivation.** The fuller mathematics "
                  "below is *not for the paper*."),
 "UPDATE": ("The same model element with newer or better data or products. The paper "
            "describes what changed about the data, and cites the published method."),
 "MODIFICATION": ("A published element whose assumptions or method changed. The paper "
                  "states the assumption that changed, why, and what it costs."),
 "EXTENSION": ("An element the published work does not have. **This is where the paper's "
               "words should go.** Each needs its purpose, its governing equations, its "
               "status and its open coverage gaps."),
 "UNCLASSIFIED": ("Not classified by its own note. Needs a decision before drafting."),
}
sec = 1
for tax, items in by_tax.items():
    if not items:
        continue
    sec += 1
    w(f"### 2.{sec} {tax.capitalize()} ({len(items)} element"
      f"{'s' if len(items) != 1 else ''})")
    w("")
    w(TAX_INTRO[tax])
    w("")
    for d, e in items:
        w(f"#### {e['element']}")
        w("")
        w(f"*Source note:* `{d}` — {DOC_TITLE.get(d, '')}  ")
        w(f"*Status:* **{status_of(e)}** — {e['status'].split('--', 1)[-1].strip()}  ")
        w(f"*Classification:* {e['taxonomy']}")
        if e["davey"] and e["davey"] not in ("-", ""):
            w("")
            w(f"*Relation to the published work:* {e['davey']}")
        if e["eqs"]:
            w("")
            w("Governing equations, as the note gives them:")
            w("")
            for q in e["eqs"]:
                w(f"- {q.get('PURPOSE', '')}")
                w("")
                w("  ```latex")
                w("  " + q["LATEX"])
                w("  ```")
                if q.get("SYMBOLS") and q["SYMBOLS"] != "-":
                    w(f"  Symbols: {q['SYMBOLS']}")
                if q.get("IMPL") and q["IMPL"] != "-":
                    w(f"  Implemented in: `{q['IMPL']}`")
                w("")
        if e["gaps"]:
            w("")
            w("Open coverage gaps named by the note:")
            w("")
            for g in e["gaps"]:
                w(f"- {g}")
        if e["sources"]:
            w("")
            w("Sources the note cites: " + "; ".join(e["sources"]) + ".")
        w("")

w("## 3. Results and findings")
w("")
w("Every claim below carries the caveat labels its note attaches, **verbatim**, and the "
  "artifact it came from. A claim with no artifact recorded is marked so: it is traceable "
  "to its note but not yet to a run directory, and must be before it is published.")
w("")
nres = 0
for d, els in parsed.items():
    rs = [r for e in els for r in e["results"]]
    if not rs:
        continue
    w(f"### 3.{list(parsed).index(d) + 1} {DOC_TITLE.get(d, d)}")
    w("")
    w(f"Source note: `{d}`")
    w("")
    for r in rs:
        nres += 1
        w(f"**R{nres}.** {r['CLAIM']}")
        w("")
        lab = r.get("LABELS", "").strip()
        w(f"- *Labels, verbatim:* {lab if lab and lab != '-' else '**NONE RECORDED — check the note before publishing this claim**'}")
        art = r.get("ARTIFACT", "").strip()
        w(f"- *Artifact:* {('`' + art + '`') if art and art != '-' else '**not recorded in the note**'}")
        w("")

w("## 4. Coverage register, copied from ARCHITECTURE.md")
w("")
w("Pete's standing rule: any result carries its coverage statement — the feasible set, the "
  "model's reach, the proposal's coverage, and every open gap named in the result's label. "
  "The register is reproduced here unchanged so that the draft and the architecture cannot "
  "drift apart. Status values are as recorded there.")
w("")
w("| # | Stage | Gap | Kind | Effect | Status |")
w("|---|---|---|---|---|---|")
for row in greg:
    w("| " + " | ".join(row) + " |")
w("")
st = collections.Counter("RESOLVED" if r[5].upper().startswith("RESOLVED")
                         else ("declared" if "declared" in r[5].lower() else "open")
                         for r in greg)
w(f"Of {len(greg)} registered gaps: {st.get('open', 0)} open, "
  f"{st.get('declared', 0)} declared or declared-conditional, {st.get('RESOLVED', 0)} resolved.")
w("")
w("## 5. Open items")
w("")
w("### 5.1 From ARCHITECTURE.md, copied unchanged")
w("")
for i, o in enumerate(open_items, 1):
    w(f"{i}. {o}")
w("")
w("### 5.2 Raised by this draft")
w("")
w("1. **The build-status table in `ARCHITECTURE.md` is out of date** (section 2.1). No "
  "status claim should be published from it until it is corrected. Posted as a "
  "recommendation in `coordination/PAPER.md`.")
w("2. **Result claims without a recorded artifact.** Several claims in section 3 are "
  "traceable to a note but not to a run directory. The project's own rule is that numbers "
  "come from the artifact; a claim that cannot name one cannot go in the paper.")
w("3. **One methods note could not be summarised.** `results/eof-impact-tau-method-oct11.md` "
  "— the impact dissipation duration method — was refused by a content filter during "
  "automated extraction. It was left out rather than worked around, so the dissipation "
  "duration τ is **absent from section 2** even though the architecture lists it as a "
  "required `ImpactView` field. It must be written into the draft by hand.")
w("4. **No element is classified as a pure reproduction except the audit notes.** If the "
  "paper is to begin with the baseline reproduction, as agreed, the reproduction needs its "
  "own methodology subsection drawn from `results/davey-2016-reference.md` and "
  "`config/davey2016.toml`, not only from the audit of contradictions.")
w("5. **Hydroacoustics, settling and ocean drift have no engine module** (section 2.1). "
  "Their status in the paper is SPECIFIED as integrated modules, whatever their analysis "
  "has produced.")
w("")
w("## 6. References")
w("")
w("Generated from `paper/CITATIONS-LEDGER.md` in the journal's Harvard style. Only entries "
  "whose use in the project could be traced to a file are listed here; the full library is "
  "in the ledger.")
w("")
# reuse the ledger's own formatter so the two files cannot disagree
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("wco", "write_citation_outputs.py")
# the writer runs at import; instead re-implement the two calls we need by exec-ing it
# in a throwaway namespace and lifting jon_ref out.
_ns = {}
_src = open("write_citation_outputs.py").read()
_src = _src.split("# ----------------------------------------------------------------- bib output")[0]
exec(compile(_src, "write_citation_outputs.py", "exec"), _ns)
jon_ref, clean_ = _ns["jon_ref"], _ns["clean"]
used = sorted((e for e in cit["entries"] if e["_used_in"]),
              key=lambda e: clean_(e.get("author") or e.get("institution") or "").lower())
for e in used:
    w(f"{jon_ref(e)}")
    w("")
w(f"*{len(used)} of {len(cit['entries'])} library entries are listed; "
  f"{len(cit['entries']) - len(used)} could not be traced to a use in the repository and "
  "are held in the ledger pending a decision.*")
w("")
w("## 7. What is not in this draft")
w("")
w("1. **The section and word budget for the paper**, and the ranked list of results that "
  "can carry one paper. These wait on the survey of recent papers in the journal, which is "
  "running.")
w("2. **The figure and table list.** Same dependency.")
w("3. **The audit of where Holland's work enters the method**, requested by architecture.")
w("4. **The proposed full draft of the paper.** It follows this document and is a separate "
  "deliverable, labelled PROPOSED on every page.")
w("5. **Style notes.** `paper/STYLE-NOTES.md` is not yet written; the dissertation Pete "
  "supplied on 12 October 2026 is the source for it, and its printed page is its PDF page "
  "minus 14.")
w("6. **The impact dissipation duration method**, for the reason in section 5.2 item 3.")
w("")
w("---")
w("")
w(f"*Generated {TODAY}. Regenerate with "
  "`python build_citation_library.py && python build_reference_draft.py`. "
  "Every regeneration should state what changed and why, in `coordination/PAPER.md`.*")

(PAPER / "REFERENCE-DRAFT.md").write_text("\n".join(M) + "\n")

# ----------------------------------------------------------------- emit LaTeX
SNAKE = re.compile(r"(?<=[A-Za-z]{2})_(?=[A-Za-z]{2})")
# An unbraced subscript of three or more letters is a code identifier, not a subscript:
# `x_final` would typeset as x_f followed by the word 'inal'. `x_{max}` and `s_t` are left
# alone because they are braced or genuinely single-character.
WORDSUB = re.compile(r"(?<=[A-Za-z])_(?=[A-Za-z]{3,})")

def math_safe(s):
    """Make a note's equation compile in math mode.

    Notes sometimes record a code identifier (`mach_rate_per_s`) where an equation is
    expected. In math mode its underscores become subscripts and a second one is a
    'double subscript' error, so an underscore BETWEEN two letters on each side is
    treated as part of an identifier and escaped. A genuine subscript (`x_1`, `s_t`)
    has a single character on one side and is left alone.
    """
    s = s.strip().strip("$")
    s = SNAKE.sub(r"\\_", s)
    s = WORDSUB.sub(r"\\_", s)
    s = re.sub(r"(?<!\\)%", r"\\%", s)
    return s

def wrap_plain(s, width=86):
    """Hard-wrap for verbatim blocks, which do not wrap themselves."""
    out, line = [], ""
    for word in str(s).split():
        if len(line) + len(word) + 1 > width:
            out.append(line); line = word
        else:
            line = (line + " " + word).strip()
    if line:
        out.append(line)
    return "\n".join(out)

T = []
t = T.append
t(r"% Reference draft, mathematics companion -- MH370 Bayesian reconstruction")
t(r"% INTERNAL. Not the paper. Generated by build_reference_draft.py -- do not hand-edit.")
t(r"% Every equation is copied from the project note named above it. Where a note gives no")
t(r"% equation, none appears here.")
t(r"\documentclass[11pt,a4paper]{article}")
t(r"\usepackage[utf8]{inputenc}\usepackage{amsmath,amssymb,geometry,fancyhdr}")
t(r"\geometry{margin=2.54cm}")
t(r"\pagestyle{fancy}\fancyhf{}\fancyhead[L]{Reference draft -- internal, not the paper}")
t(r"\fancyhead[R]{\thepage}")
t(r"\title{MH370 Bayesian reconstruction:\\ governing equations of the reference draft}")
t(r"\author{Internal reference --- paper drafting and citations module}")
t(r"\date{" + TODAY + r"}")
t(r"\begin{document}\maketitle")
t(r"\noindent\textbf{Internal document.} This is the mathematics companion to")
t(r"\texttt{paper/REFERENCE-DRAFT.md}. Equations are reproduced as the project notes give")
t(r"them, each with the file that implements it. Nothing here is a derivation by the")
t(r"drafting module, and nothing is included that a note does not state.")
t(r"\medskip")
neq = 0
for tax in ["REPRODUCTION", "UPDATE", "MODIFICATION", "EXTENSION", "UNCLASSIFIED"]:
    items = [(d, e) for d, e in by_tax[tax] if e["eqs"]]
    if not items:
        continue
    t(r"\section{" + tax.capitalize() + r"}")
    for d, e in items:
        t(r"\subsection{" + e["element"].replace("&", r"\&").replace("_", r"\_") + r"}")
        t(r"\noindent\textit{Status:} " + status_of(e) +
          r". \textit{Source note:} \texttt{" + d.replace("_", r"\_") + r"}.")
        t(r"\medskip")
        for q in e["eqs"]:
            neq += 1
            t(r"\begin{equation}")
            t(math_safe(q["LATEX"]))
            t(r"\end{equation}")
            # Symbol glossaries and paths come from prose notes and mix text with LaTeX
            # commands, so they are set verbatim: that cannot fail to compile and it shows
            # exactly what the note said, which is the point of an internal reference.
            if q.get("SYMBOLS") and q["SYMBOLS"] != "-":
                t(r"\noindent\textbf{Symbols.}")
                t(r"\begin{verbatim}")
                t(wrap_plain(q["SYMBOLS"]))
                t(r"\end{verbatim}")
            if q.get("IMPL") and q["IMPL"] != "-":
                t(r"\noindent\textbf{Implemented in.}")
                t(r"\begin{verbatim}")
                t(wrap_plain(q["IMPL"]))
                t(r"\end{verbatim}")
            t(r"\medskip")
t(r"\end{document}")
(PAPER / "reference-draft.tex").write_text("\n".join(T) + "\n")

print("REFERENCE-DRAFT.md:", (PAPER / "REFERENCE-DRAFT.md").stat().st_size, "bytes")
print("reference-draft.tex:", (PAPER / "reference-draft.tex").stat().st_size, "bytes,", neq, "equations")
print("elements:", sum(len(v) for v in by_tax.values()),
      "| by taxonomy:", {k: len(v) for k, v in by_tax.items() if v})
print("results carried:", nres, "| references listed:", len(used),
      "| G-register rows:", len(greg))
print("notes that failed extraction:", list(failed))


