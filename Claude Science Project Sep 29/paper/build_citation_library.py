"""Build the MH370 paper master citation library.

Gathers every citation the project uses, deduplicates it, grades it, finds which
module uses it, checks each DOI against CrossRef, and locates a held copy.
Outputs: handoff/citations.json  (consumed by the ledger/bib writer)

Re-runnable. Nothing is invented: every field is either copied from a project
file, returned by CrossRef, or left empty.
"""
import json, os, re, pathlib, unicodedata, collections, time

ROOT = pathlib.Path("repo2/Claude Science Project Sep 29")
OUT = pathlib.Path("handoff"); OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------- bib parsing
# Entries may be one-per-line with the closing brace at end of line, or spread
# over many lines. Scan by brace depth rather than by regex so both parse.
HEAD = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.S)

def iter_entries(txt):
    for m in HEAD.finditer(txt):
        depth, i, n = 1, m.end(), len(txt)
        while i < n and depth:
            c = txt[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            i += 1
        yield m.group(1), m.group(2), txt[m.end(): i - 1]

class _E:
    findall = staticmethod(lambda txt: list(iter_entries(txt)))
ENTRY = _E()

def split_fields(body):
    """Field-by-field scan that respects nested braces and quoted values."""
    out, i, n = {}, 0, len(body)
    while i < n:
        m = re.compile(r"([A-Za-z\-_]+)\s*=\s*").search(body, i)
        if not m:
            break
        key = m.group(1).lower()
        j = m.end()
        while j < n and body[j] in " \t\n":
            j += 1
        if j >= n:
            break
        if body[j] == "{":
            depth, k = 0, j
            while k < n:
                if body[k] == "{":
                    depth += 1
                elif body[k] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            val, i = body[j + 1:k], k + 1
        elif body[j] == '"':
            k = body.find('"', j + 1)
            val, i = body[j + 1:k], k + 1
        else:
            k = j
            while k < n and body[k] not in ",\n":
                k += 1
            val, i = body[j:k], k
        out[key] = re.sub(r"\s+", " ", val).strip()
    return out

def norm_title(s):
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(s.split())

def norm_doi(s):
    s = (s or "").strip().lower()
    s = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", s)
    return s.rstrip(" .")

def first_surname(authors):
    a = (authors or "").split(" and ")[0].strip()
    if "," in a:
        return a.split(",")[0].strip()
    return a.split()[-1] if a.split() else ""

# ---------------------------------------------------------------- collect
bibs = sorted(ROOT.glob("results/*.bib")) + sorted(ROOT.glob("results/**/*.bib"))
# Paper-level additions, owned by this module (never results/, which the modules own).
# references.bib is the generated output and must not be read back in.
bibs += [p for p in ROOT.glob("paper/*.bib") if p.name != "references.bib"]
bibs = sorted(set(bibs))
raw = []
for f in bibs:
    txt = f.read_text(errors="replace")
    for etype, key, body in ENTRY.findall(txt):
        fl = split_fields(body)
        fl["_type"] = etype.lower()
        fl["_key"] = key
        fl["_file"] = str(f.relative_to(ROOT))
        raw.append(fl)

# ---------------------------------------------------------------- dedupe
merged = {}
order = []
def ident(e):
    d = norm_doi(e.get("doi", ""))
    if d:
        return ("doi", d)
    return ("ayt", first_surname(e.get("author", "")).lower(),
            (e.get("year") or "").strip(), norm_title(e.get("title", ""))[:70])

for e in raw:
    k = ident(e)
    if k not in merged:
        merged[k] = dict(e)
        merged[k]["_files"] = [e["_file"]]
        merged[k]["_keys"] = [e["_key"]]
        order.append(k)
    else:
        m = merged[k]
        if e["_file"] not in m["_files"]:
            m["_files"].append(e["_file"])
        if e["_key"] not in m["_keys"]:
            m["_keys"].append(e["_key"])
        for fk, fv in e.items():
            if fk.startswith("_"):
                continue
            if not m.get(fk) and fv:
                m[fk] = fv

entries = [merged[k] for k in order]

# ---------------------------------------------------------------- grading
AGENCY = ("atsb", "australian transport safety", "safety investigation", "icao",
          "inmarsat", "dsto", "dstg", "defence science", "ctbto", "noaa",
          "boeing", "ncei", "gebco", "copernicus", "mercator", "nasa", "esa",
          "royal society", "iso ", "ieee standard", "bureau of meteorology",
          "ministry of transport", "cnes", "airbus",
          "csiro", "commonwealth scientific", "cmst", "curtin", "geoscience",
          "lawrence livermore", "sandia", "naval", "woods hole", "scripps",
          "jet propulsion", "met office", "ecmwf", "hycom", "ifremer",
          "national oceanograph", "lamont", "springer", "cambridge university",
          "elsevier", "wiley", "taylor", "iho", "wmo", "usgs")
UNOFFICIAL = ("blogspot", "wordpress", "370location", "duncansteel", "radiantphysics",
              "reddit", "forum", "medium.com", "youtube", "tmfassociates",
              "aviationweek", "theguardian", "bbc.co")
PREPRINT = ("arxiv", "preprint", "biorxiv", "essoar", "ssrn", "researchgate",
            "egusphere", "authorea")

def grade(e):
    t, pub = e["_type"], " ".join(
        str(e.get(k, "")) for k in ("publisher", "institution", "organization",
                                    "journal", "booktitle", "howpublished",
                                    "url", "series", "note", "school")).lower()
    if any(w in pub for w in UNOFFICIAL):
        return "unofficial", "source is a blog, forum or independent analyst site"
    if any(w in pub for w in PREPRINT) or t in ("phdthesis", "mastersthesis"):
        return "grey", "preprint, thesis or non-refereed deposit"
    if t in ("techreport", "manual", "report"):
        return "official" if any(w in pub for w in AGENCY) else "grey", \
               "agency or standards body report" if any(w in pub for w in AGENCY) else "report, not refereed"
    if t in ("book", "inbook", "incollection", "booklet"):
        return "official", "published book or chapter"
    if t in ("article",):
        return "peer-reviewed", "journal article"
    if t in ("inproceedings", "conference", "proceedings"):
        return "peer-reviewed", "conference proceedings"
    if t == "misc":
        if any(w in pub for w in AGENCY):
            return "official", "agency, publisher or data-provider product"
        return "grey", "miscellaneous entry; grade needs manual confirmation"
    return "grey", "entry type not recognised; grade needs manual confirmation"

for e in entries:
    g, why = grade(e)
    e["_grade"], e["_grade_basis"] = g, why

# ---------------------------------------------------- where the project uses it
SCAN_GLOBS = ["results/**/*.md", "ARCHITECTURE.md", "README.md", "RUNBOOK.md",
              "threads/master-prompts/*.md", "coordination/*.md",
              "engine/**/*.rs", "engine/**/*.toml", "engine/**/*.py"]
scan_files = []
for g in SCAN_GLOBS:
    scan_files += [p for p in ROOT.glob(g) if p.is_file()]
scan_files = sorted(set(scan_files))

texts = {}
for p in scan_files:
    try:
        texts[p] = p.read_text(errors="replace")
    except Exception:
        pass

CITE_RE = re.compile(
    r"\(?\b([A-Z][A-Za-z\u00c0-\u024f'\-]+)"
    r"(?:\s+(?:et\s+al\.?|and\s+[A-Z][A-Za-z'\-]+|&\s+[A-Z][A-Za-z'\-]+))?"
    r",?\s*\(?((?:19|20)\d{2})[a-z]?\)?")

usage = collections.defaultdict(set)
inline_counts = collections.Counter()
for p, txt in texts.items():
    rel = str(p.relative_to(ROOT))
    for m in CITE_RE.finditer(txt):
        inline_counts[(m.group(1), m.group(2))] += 1
    low = txt.lower()
    for e in entries:
        sn = first_surname(e.get("author", "")).lower()
        yr = (e.get("year") or "").strip()
        if len(sn) > 3 and yr and sn in low:
            # require surname and year within 120 chars of one another
            for mm in re.finditer(re.escape(sn), low):
                w = low[max(0, mm.start() - 60): mm.start() + 120]
                if yr in w:
                    usage[tuple(e["_keys"])].add(rel)
                    break
    # also match by DOI string
    for e in entries:
        d = norm_doi(e.get("doi", ""))
        if d and d in low:
            usage[tuple(e["_keys"])].add(rel)

for e in entries:
    e["_used_in"] = sorted(usage.get(tuple(e["_keys"]), []))

# ------------------------------------------------- unmatched inline citations
known = set()          # (surname-or-org, year)
known_tokens = set()   # any name token appearing in a bib key or author/org field
for e in entries:
    yr = (e.get("year") or "").strip()
    sn = first_surname(e.get("author", ""))
    if sn:
        known.add((sn.lower(), yr))
    org = " ".join(str(e.get(k, "")) for k in
                   ("author", "institution", "organization", "publisher", "school",
                    "number", "series", "title"))
    for tok in re.findall(r"[A-Za-z]{3,}", org):
        known_tokens.add(tok.lower())
        known.add((tok.lower(), yr))
    for k in e["_keys"]:
        for tok in re.findall(r"[A-Za-z]{3,}", k):
            known_tokens.add(tok.lower())
            known.add((tok.lower(), yr))

MONTHS = {"jan", "january", "feb", "february", "mar", "march", "apr", "april",
          "may", "jun", "june", "jul", "july", "aug", "august", "sep", "sept",
          "september", "oct", "october", "nov", "november", "dec", "december"}
STOP = MONTHS | {
    "figure", "table", "section", "appendix", "arc", "run", "case", "the",
    "this", "note", "page", "since", "between", "from", "stage", "mach", "utc",
    "fl", "overnight", "version", "commit", "branch", "seed", "config", "stage",
    "step", "epoch", "window", "item", "panel", "lane", "set", "list", "row",
    "day", "week", "year", "date", "updated", "revised", "added", "see", "and"}
unmatched = sorted(
    ((f"{a} {y}", c) for (a, y), c in inline_counts.items()
     if (a.lower(), y) not in known
     and a.lower() not in STOP
     and a.lower() not in known_tokens
     and not a.endswith("-")
     and c >= 3),
    key=lambda kv: -kv[1])

# ------------------------------------------------------- held copies on disk
COPY_DIRS = [pathlib.Path("/Users/pete/Downloads"),
             pathlib.Path("/Users/pete/Downloads/mh370-exchange")]
local = []
for d in COPY_DIRS:
    if d.exists():
        for p in d.rglob("*"):
            if p.suffix.lower() in (".pdf", ".docx", ".doc") and p.is_file():
                local.append(p)
local_tok = [(p, set(norm_title(p.stem).split())) for p in local]

for e in entries:
    tt = set(norm_title(e.get("title", "")).split())
    tt = {w for w in tt if len(w) > 3}
    best, score = None, 0.0
    if len(tt) >= 3:
        for p, pt in local_tok:
            if not pt:
                continue
            ov = len(tt & pt) / len(tt)
            if ov > score:
                best, score = p, ov
    e["_local_copy"] = str(best) if score >= 0.45 else ""
    e["_local_match"] = round(score, 2) if best else 0.0
    e["_local_confident"] = bool(best and score >= 0.7)

# ------------------------------------------------- CrossRef DOI verification
# Cached: re-runs do not re-hit the API. Verifies that the DOI resolves and that
# the registered title and year agree with ours. Nothing is overwritten; the
# CrossRef values are recorded alongside for comparison.
import urllib.request, urllib.error
CACHE = OUT / "crossref-cache.json"
cache = json.load(open(CACHE)) if CACHE.exists() else {}

try:
    import builtins
    _host = getattr(builtins, "host", None) or globals().get("host")
    MAILTO = _host.get_user_email() if _host else None
except Exception:
    MAILTO = None
UA = "MH370-paper-citation-audit/1.0" + (f" (mailto:{MAILTO})" if MAILTO else "")

def datacite(doi):
    """CrossRef indexes only CrossRef-registered DOIs. Datasets, data products and
    arXiv deposits are registered with DataCite, and 404 at CrossRef without being
    broken. Ask the right registry before calling a DOI unverified."""
    url = "https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe="")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                   "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=25) as r:
            a = json.load(r)["data"]["attributes"]
        return {"status": "resolved", "agency": "DataCite",
                "title": (a.get("titles") or [{}])[0].get("title", ""),
                "year": str(a.get("publicationYear") or ""),
                "year_print": "", "year_online": "",
                "volume": "", "issue": "", "pages": "",
                "container": "", "publisher": a.get("publisher", ""),
                "type": (a.get("types") or {}).get("resourceTypeGeneral", ""),
                "n_authors": len(a.get("creators", []) or [])}
    except urllib.error.HTTPError as ex:
        return {"status": f"http {ex.code}", "agency": "DataCite"}
    except Exception as ex:
        return {"status": f"error: {type(ex).__name__}", "agency": "DataCite"}

def crossref(doi):
    if doi in cache:
        return cache[doi]
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    if MAILTO:
        url += "?mailto=" + urllib.parse.quote(MAILTO)
    rec = {"status": "error"}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            msg = json.load(r)["message"]
        def _yr(k):
            dp = (msg.get(k, {}) or {}).get("date-parts") or [[None]]
            return str(dp[0][0] or "")
        rec = {
            "status": "resolved",
            "title": (msg.get("title") or [""])[0],
            "year": str((msg.get("issued", {}).get("date-parts") or [[""]])[0][0] or ""),
            "year_print": _yr("published-print"),
            "year_online": _yr("published-online"),
            "volume": msg.get("volume", ""),
            "issue": msg.get("issue", ""),
            "pages": msg.get("page", ""),
            "type": msg.get("type", ""),
            "container": (msg.get("container-title") or [""])[0],
            "publisher": msg.get("publisher", ""),
            "n_authors": len(msg.get("author", []) or []),
        }
        rec["agency"] = "CrossRef"
    except urllib.error.HTTPError as ex:
        rec = datacite(doi) if ex.code == 404 else {"status": f"http {ex.code}",
                                                    "agency": "CrossRef"}
    except Exception as ex:
        rec = {"status": f"error: {type(ex).__name__}", "agency": "CrossRef"}
    cache[doi] = rec
    time.sleep(0.12)
    return rec

for e in entries:
    d = norm_doi(e.get("doi", ""))
    if not d:
        e["_verify"] = "UNVERIFIED, NO DOI (nothing to check automatically)"
        e["_crossref"] = {}
        continue
    cr = crossref(d)
    e["_crossref"] = cr
    ag = cr.get("agency", "registry")
    if cr.get("status") != "resolved":
        e["_verify"] = ("UNVERIFIED, DOI NOT FOUND (absent from both CrossRef and "
                        f"DataCite: {cr.get('status')})")
        continue
    t_ours, t_cr = norm_title(e.get("title", "")), norm_title(cr.get("title", ""))
    ours_toks = set(t_ours.split())
    cr_toks = set(t_cr.split())
    overlap = len(ours_toks & cr_toks) / max(len(ours_toks), 1)
    y_ok = (e.get("year") or "").strip() == cr.get("year", "")
    if overlap >= 0.7 and y_ok:
        e["_verify"] = f"METADATA VERIFIED ({ag}: title and year agree)"
    elif overlap >= 0.7:
        ours_y = (e.get("year") or "").strip()
        if ours_y and ours_y == cr.get("year_print"):
            e["_verify"] = (f"METADATA VERIFIED ({ag}: title agrees; our year is the "
                            f"printed-issue year {cr['year_print']}, the registry's "
                            f"earliest-issued year is the online-first year "
                            f"{cr.get('year_online') or cr.get('year')})")
        else:
            e["_verify"] = (f"METADATA MISMATCH ({ag}: title agrees; year ours {ours_y}, "
                            f"registry issued {cr.get('year')}, print "
                            f"{cr.get('year_print') or '-'}, online "
                            f"{cr.get('year_online') or '-'})")
    else:
        e["_verify"] = (f"METADATA MISMATCH ({ag}: registered title is "
                        f"{cr.get('title','')[:80]!r})")

json.dump(cache, open(CACHE, "w"), indent=1)

summary = {
    "bib_files": [str(f.relative_to(ROOT)) for f in bibs],
    "raw_entries": len(raw),
    "deduplicated": len(entries),
    "with_doi": sum(1 for e in entries if norm_doi(e.get("doi", ""))),
    "by_grade": dict(collections.Counter(e["_grade"] for e in entries)),
    "by_type": dict(collections.Counter(e["_type"] for e in entries)),
    "scanned_files": len(scan_files),
    "entries_with_usage": sum(1 for e in entries if e["_used_in"]),
    "by_verification": dict(collections.Counter(
        e["_verify"].split(" (")[0] for e in entries)),
    "mismatches": [f"{e['_keys'][0]}: {e['_verify']}" for e in entries
                   if e["_verify"].startswith("METADATA MISMATCH")],
    "entries_with_local_copy": sum(1 for e in entries if e["_local_copy"]),
    "entries_with_confident_copy": sum(1 for e in entries if e.get("_local_confident")),
    "local_candidates_indexed": len(local),
    "unmatched_inline_top": unmatched[:40],
}
json.dump({"summary": summary, "entries": entries},
          open(OUT / "citations.json", "w"), indent=1)
print(json.dumps(summary, indent=1)[:3000])
