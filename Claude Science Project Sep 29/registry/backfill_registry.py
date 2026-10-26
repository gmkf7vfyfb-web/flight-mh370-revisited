#!/usr/bin/env python3
"""Backfill the module registries (all modules except hydroacoustics) from records that already exist. 25 Oct 2026.

Rules (clean-up proposal of 23 Oct 2026, sections 5.1-5.3; approved):
  * Register, do not move or redo. No recompute. No new audit. Status comes from existing records only, in this order:
      ruling (Pete) > explicit statement (superseded / withdrawn / defect) > chain (newer version, same name stem)
      > readme (status line or banner in the item's own README or note) > UNCHECKED.
  * Hand-read records are in status_records.yaml (item, status, evidence file:line or memory id). The script extracts the quotes.
  * Module assignment: name rule, then the subject of the commit that first added the item, then the overrides below.
Output: modules/<module>/entries.yaml (generated; do not edit by hand) and backfill_report.json.
Usage:
  python3 backfill_registry.py --memories <memory export .json> [--repo <repo top>]
The exchange inventory and the branch record are read from data_homes/ (written by exchange_inventory.py and record_branches.py).
"""
import argparse, collections, gzip, json, os, re, subprocess, sys
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
WORKN = "Claude Science Project Sep 29"
PREFIX = {"core": "core", "end-of-flight": "eof", "drift": "drift", "settling": "settling", "searched-areas": "searched",
          "pleiades": "pleiades", "composer": "composer", "paper": "paper", "project": "project"}
MODULES = list(PREFIX)
WS = re.compile("/" + "workspaces/[^\\s`'\")]*" + "|" + "/" + r"\.claude-" + "science/[^\\s`'\")]*")

# ---------- module rules ----------
RULES = [
    (r"^hydroacoustics", "hydroacoustics"),
    (r"^(eof-|endurance_)", "end-of-flight"),
    (r"^(composer-|e2e-calibration-|decision-2026)", "composer"),
    (r"^(settling-)", "settling"),
    (r"^(seabed-search|searched-areas-|seabed-field-coverage)", "searched-areas"),
    (r"^pleiades", "pleiades"),
    (r"^(drift-|debris-drift|kadri-haixun)", "drift"),
    (r"^(run-[a-j]|run-j|next-run-|stage[123]|bfo|bto|bias_drift|core_|davey|declination|fuel-|fnl_|mach250|n571|r600|reject_|request21|route|sampler-smoke|satellite-coverage|sita-|speed-envelope|step-check|tempered_|track_wide|turn-|vr_only|waypoints-|item10|islands-check|c7-options|families-289|evidence-sweep|overnight-reports|flyby|hybrid-arm)", "core"),
]
LOOSE_RULES = RULES + [
    (r"^(end-of-flight|eof|endurance|boeing|glide|dive|impact)", "end-of-flight"),
    (r"^(composer|compose|views)", "composer"),
    (r"^(searched|seabed|search-)", "searched-areas"),
    (r"^(ocean-transport|ocean-drift|drift|debris|flaperon|beaching)", "drift"),
    (r"^(settl|wreck)", "settling"),
    (r"^(core|fuel|bfo|bto|satcom|route|path|filter|davey|inmarsat|mach|track|radar|n571|waypoint|sampler|1825|0019|0011|arc|log-?on)", "core"),
    (r"^(paper|jon|journal|manuscript|referee|figure)", "paper"),
    (r"^(restricted-sources|INDEX|README|clean|housekeep|audit|status|overnight|project|handover|memory)", "project"),
]
SUBJ = [(r"(?i)^(core|run[- ]?j|core combination)", "core"), (r"(?i)^(eof|end[- ]of[- ]flight)", "end-of-flight"), (r"(?i)^composer", "composer"),
        (r"(?i)^settling", "settling"), (r"(?i)^(searched|seabed)", "searched-areas"), (r"(?i)^pleiades", "pleiades"),
        (r"(?i)^(drift|debris|ocean)", "drift"), (r"(?i)^hydro", "hydroacoustics")]
LOOSE_OVERRIDE = {  # read by hand from the commit subject, 25 Oct 2026
    "breakup-field-candidate.md": "settling", "ocean-fields-east-120-160E.md": "drift", "ocean-product-recommendation.md": "drift",
    "ocean-references.bib": "drift", "ocean-references.md": "drift",
    "burst-0019-plausibility-architecture-fig1.png": "end-of-flight", "burst-0019-plausibility-architecture-fig2.png": "end-of-flight",
    "burst-0019-plausibility-architecture-fig3.png": "end-of-flight", "burst-0019-plausibility-architecture.md": "end-of-flight",
    "planned-descent-run-plan.md": "end-of-flight", "fig-planned-descent-map.png": "end-of-flight",
    "fig-impact-loudness-maps.png": "end-of-flight", "fig-gain-37s-vs-26s.png": "end-of-flight",
    "source-access-ledger-2026-10-22.csv": "project", "source-access-ledger-2026-10-22.md": "project"}
COORD = {"COMPOSER.md": "composer", "CORE_STAGES.md": "core", "END_OF_FLIGHT.md": "end-of-flight", "OCEAN_DRIFT.md": "drift",
         "OCEAN_TRANSPORT.md": "drift", "OCEAN_SETTLING.md": "settling", "PAPER.md": "paper", "PLEIADES.md": "pleiades",
         "SEARCHED_AREAS.md": "searched-areas", "README.md": "project", "architecture.md": "project", "OVERNIGHT-2026-10-10.md": "project"}
THREAD_RULES = [(r"hydroacoustic", "hydroacoustics"), (r"composer|e2e-calibration", "composer"), (r"end-of-flight|eof-|gain-observable|mode-allocation", "end-of-flight"),
                (r"ocean-drift|ocean-transport|drift", "drift"), (r"settling", "settling"), (r"searched-areas", "searched-areas"),
                (r"pleiades", "pleiades"), (r"paper", "paper"), (r"filter-audit|fuel|core-|item10|item5|ruling-composition|work-order|overnight", "core"),
                (r"shared-contract|inbox-watch", "project")]
CRATE = {"ocean": "drift", "compose": "composer"}
HYP = {"end-of-flight": "end-of-flight", "pleiades": "pleiades", "seabed-search": "searched-areas"}
EX_MOD = {"archive": "project", "composer": "composer", "core": "core", "debris-drift": "drift", "ocean-transport": "drift",
          "end-of-flight": "end-of-flight", "pleiades": "pleiades", "searched-areas": "searched-areas", "settling": "settling"}
BRANCH_MOD = {"core-request21": "core", "core-tau-h": "core", "core/ocean-transport": "drift", "hypothesis/debris-drift": "drift",
              "hypothesis/end-of-flight": "end-of-flight", "hypothesis/pleiades": "pleiades", "hypothesis/seabed-search": "searched-areas",
              "hypothesis/settling": "settling", "architecture/module-briefs-oct06": "project", "sept-29-chatgpt-advances": "project", "main": "project"}
MOVED = ["outputs", "output", "downloads", "handoff", "library_full_audit"]
ARCHIVE_DIR = "Archive Sep 29 loose files"
KEEP_IN_PLACE = ["library_full_audit/MH370"]   # restricted holding (ledger, Pete 9 Oct: "stays where it is")
AVIONICS = [("avionics_training", r"^tmp/avionics_training_"), ("avionics_try", r"^tmp/avionics_try_"),
            ("slideshare_avionics", r"^tmp/slideshare_avionics"), ("scribd_satcom", r"^tmp/scribd_satcom\.html$"),
            ("paperzz_airlink", r"^tmp/paperzz_airlink\.html$"), ("slideshare_airlink", r"^tmp/slideshare_airlink\.html$"),
            ("avionics_min", r"^tmp/avionics_min-1\.png$")]
XHOLDER = "Porsche drive (available on request from Pete)"
RESTRICTED_NOTE = ("RESTRICTED: internal use only. Record every use in results/restricted-sources-ledger.md. "
                   "Not for publication before review (Pete, 9-10 Oct 2026).")
DATA_HOMES = [("drift", "mh370-ocean-data", "Ocean model and observation data (GLORYS12, ERA5, GlobCurrent, OSCAR, WAVERYS, GDP, BRAN2016, GEBCO, GSHHG, WOA23, AusSeabed, products)."),
              ("settling", "mh370-settling-work", "Settling work folder."), ("settling", "mh370-settling-work-j", "Settling work folder for run J."),
              ("project", "mh370-large-files", "Large files folder."), ("project", "mh370-unpack", "Unpacked material folder."),
              ("project", "archive-tools", "Scripts that copy exchange folders to the external drive and check the copy (archive-to-porsche).")]
EXTERNAL_DRIVE = {"0bzoiifnlx2auwetvsjbvs2jwx0e", "0b6gvsowo81httgjdvklrx3bca1e", "0b7yqpah4jin5amtwuurlzv9jnk0"}  # verifier 25 Oct: third-party links
STATUS_WORDS = re.compile(r"(?i)\b(supersed\w*|withdrawn|withdraw|retracted|do not use|obsolete|replaced by|is wrong|was wrong|known defect|deprecated)\b")
STAT_LINE = re.compile(r"(?i)^\s*(>?\s*)?(\*\*)?\s*status\s*(:|\*\*\s*:|:\s*\*\*)")
BANNER = re.compile(r"(?i)^\s*(>|\*\*).*\b(smoke|stand-?in|provisional|not evidence|do not quote|caveat|pilot|unconverged|not converged|draft|not for release)\b")


def slug(s):
    return re.sub(r"[^a-z0-9_-]+", "-", s.lower().replace(".", "_")).strip("-")


def git(top, *a):
    env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null"}
    return subprocess.run(["git", *a], cwd=top, capture_output=True, text=True, env=env).stdout


def first_heading(p):
    try:
        for line in Path(p).read_text(errors="replace").splitlines()[:40]:
            if line.startswith("# "):
                return line[2:].strip()[:200]
    except Exception:
        pass
    return None


def map_readme(t):
    t2 = t.lower()
    if re.search(r"\bsuperseded\b", t2): return "SUPERSEDED"
    if re.search(r"\bwithdrawn\b", t2): return "WITHDRAWN"
    if re.search(r"pending (a |pete|ruling|your)|await\w* (pete|a ruling|your)|for pete to|not adopted|proposal", t2): return "PENDING_RULING"
    if re.search(r"provisional|stand-?in|not for release|pipeline test|unconverged|not converged|smoke|exploratory|prelim|draft|caveat|conditional|wip\b|partial|incomplete|in progress|running|pilot|not yet|not evidence", t2): return "CURRENT_WITH_CAVEATS"
    if re.search(r"complete|final|accepted|adopted|delivered|current|done|pass\b|passed|verified|measured", t2): return "CURRENT"
    return None


def clean(s):
    return WS.sub("<session workspace path>", s) if isinstance(s, str) else s


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--memories", required=True); ap.add_argument("--repo")
    a = ap.parse_args()
    top = Path(a.repo or git(HERE, "rev-parse", "--show-toplevel").strip()).resolve()
    work = top / WORKN; res = work / "results"
    tracked = [p for p in git(top, "ls-files", "-z").split("\0") if p]
    mem = {m["id"]: m for m in json.load(open(a.memories))}
    inv = json.load(gzip.open(HERE / "data_homes" / "exchange_inventory.json.gz", "rt"))
    branches = json.load(open(HERE / "data_homes" / "branches.json"))
    srec = yaml.safe_load(open(HERE / "status_records.yaml"))["records"]
    report = collections.defaultdict(list)

    # git first add / last change per path, one pass
    log = git(top, "log", "--format=@@%H|%cI|%s", "--name-only")
    first, last, cur = {}, {}, None
    for line in log.splitlines():
        if line.startswith("@@"):
            cur = line[2:].split("|", 2)
        elif line.strip():
            last.setdefault(line, cur); first[line] = cur

    def gitinfo(paths):
        f = [first[p] for p in paths if p in first]; l = [last[p] for p in paths if p in last]
        if not f:
            return {"note": "no commit found in the local history"}
        f0 = min(f, key=lambda x: x[1]); l0 = max(l, key=lambda x: x[1])
        return {"first_added": {"commit": f0[0], "date": f0[1], "subject": clean(f0[2][:200])},
                "last_changed": {"commit": l0[0], "date": l0[1]}}

    E = []   # all entries

    def add(e):
        e.setdefault("defects", []); e.setdefault("superseded_by", None); e.setdefault("inputs", [])
        e.setdefault("producing_thread", None); e.setdefault("verified_this_run", False)
        e.setdefault("status", "UNCHECKED"); e.setdefault("status_rank", "none"); e.setdefault("status_evidence", [])
        E.append(e)

    # ---------- 1. results/ ----------
    rp = WORKN + "/results/"
    rfiles = [p[len(rp):] for p in tracked if p.startswith(rp)]
    loose = sorted(p for p in rfiles if "/" not in p and p != "INDEX.md")   # INDEX.md is generated by make_index.py
    folders = collections.defaultdict(list)
    for p in rfiles:
        if "/" in p:
            folders[p.split("/")[0]].append(p)

    def subj_mod(s):
        for pat, m in SUBJ:
            if re.search(pat, s or ""): return m
        return None

    item_mod, item_basis = {}, {}
    for n in sorted(folders):
        subs = collections.Counter(first[rp + p][2] for p in folders[n] if rp + p in first)
        s = subs.most_common(1)[0][0] if subs else ""
        m = next((mm for pat, mm in RULES if re.search(pat, n)), None)
        item_mod[n] = m or subj_mod(s); item_basis[n] = "name rule" if m else "commit subject"
    for f in loose:
        s = first.get(rp + f, ("", "", ""))[2]
        m = next((mm for pat, mm in LOOSE_RULES if re.search(pat, f, re.I)), None)
        if f in LOOSE_OVERRIDE:
            item_mod[f], item_basis[f] = LOOSE_OVERRIDE[f], "override from commit subject (read by hand)"
        elif m:
            item_mod[f], item_basis[f] = m, "name rule"
        elif subj_mod(s):
            item_mod[f], item_basis[f] = subj_mod(s), "commit subject"
        else:
            item_mod[f], item_basis[f] = "core", "default core: commit subject is a core estimation-chain subject"
    hydro_items = sorted(i for i in item_mod if item_mod[i] == "hydroacoustics")
    report["results_hydro_left_for_phase2"] = hydro_items
    name2id = {}
    for n in sorted(item_mod):
        mod = item_mod[n]
        if mod == "hydroacoustics":
            continue
        isdir = n in folders
        rid = f"{PREFIX[mod]}.res.{slug(n)}"
        name2id[n] = rid
        files = [rp + p for p in folders[n]] if isdir else [rp + n]
        readme = None
        if isdir:
            rs = sorted(p for p in folders[n] if p.count("/") == 1 and p.split("/")[-1].lower().startswith("readme"))
            readme = rs[0] if rs else None
        elif n.endswith(".md"):
            readme = n
        desc = first_heading(res / readme) if readme else None
        gi = gitinfo(files)
        e = {"id": rid, "kind": "product" if (isdir or not n.endswith(".md")) else "note", "module": mod,
             "path": f"WORK:results/{n}", "note": clean(desc or gi.get("first_added", {}).get("subject") or n),
             "assignment_basis": item_basis[n], "git": gi, "_name": n, "_readme": readme}
        rj = [p for p in folders.get(n, []) if p.endswith("/run.json")]
        if rj:
            try:
                d = json.load(open(res / rj[0]))
                e["run_json"] = {"file": f"WORK:results/{rj[0]}", "keys": sorted(d)[:40],
                                 "commit": next((str(d[k]) for k in ("commit", "git_commit", "git", "engine_commit") if k in d), None)}
            except Exception as ex:
                e["run_json"] = {"file": f"WORK:results/{rj[0]}", "error": str(ex)[:120]}
        add(e)

    # ---------- 2. engine/, coordination/, threads/, paper/, top files ----------
    ep = WORKN + "/engine/"
    eng = collections.defaultdict(list)
    for p in tracked:
        if p.startswith(ep):
            r = p[len(ep):].split("/")
            if r[0] in ("crates", "hypotheses") and len(r) > 2:
                key = "/".join(r[:2])
            elif r[0] in ("crates", "hypotheses"):
                key = r[0] + "/_top-files"
            elif r[0] == "data" and len(r) > 1:
                key = "data/" + r[1]
            elif len(r) == 1:
                key = "_top-files"
            else:
                key = r[0]
            eng[key].append(p)
    for key, files in sorted(eng.items()):
        parts = key.split("/")
        if parts[0] == "crates" and len(parts) > 1:
            mod = CRATE.get(parts[1], "core")
        elif parts[0] == "hypotheses" and len(parts) > 1:
            if parts[1] == "hydroacoustics":
                continue
            mod = HYP.get(parts[1], "core")
        else:
            mod = "core"
        kind = "input" if parts[0] in ("data", "geo") else "code"
        is_group = key.endswith("_top-files")
        path = f"WORK:engine/{key}" if not is_group else f"WORK:engine/{'/'.join(parts[:-1]) + '/' if len(parts) > 1 else ''}"
        e = {"id": f"{PREFIX[mod]}.{'in' if kind == 'input' else 'code'}.engine-{slug(key)}", "kind": kind, "module": mod,
             "path": path, "file_list": [p[len(WORKN) + 1:] for p in files] if is_group else None,
             "note": f"Engine {'data' if kind == 'input' else 'code'} on the working branch: engine/{key} ({len(files)} files). Code source of record is git.",
             "assignment_basis": "engine folder map", "git": gitinfo(files)}
        add(e)
    for p in tracked:
        if not p.startswith(WORKN + "/"):
            continue
        rel = p[len(WORKN) + 1:]
        if rel.startswith("coordination/"):
            name = rel.split("/", 1)[1]
            mod = COORD.get(name)
            if mod is None:
                if "hydro" in name.lower(): report["coordination_hydro_left_for_phase2"].append(rel); continue
                mod = "project"
        elif rel.startswith("threads/"):
            name = rel.split("/", 1)[1]
            mod = next((m for pat, m in THREAD_RULES if re.search(pat, name)), "project")
            if mod == "hydroacoustics": report["threads_hydro_left_for_phase2"].append(rel); continue
        elif rel.startswith("paper/"):
            mod = "paper"
        elif "/" not in rel:
            mod = "project"
        else:
            continue
        kind = "code" if rel.endswith((".py", ".sh", ".mjs")) else ("note" if rel.endswith((".md", ".txt", ".tex", ".bib")) else "product")
        e = {"id": f"{PREFIX[mod]}.{'code' if kind == 'code' else 'note'}.{slug(rel.replace('/', '-'))}", "kind": kind, "module": mod,
             "path": f"WORK:{rel}", "note": clean(first_heading(top / p) or gitinfo([p]).get("first_added", {}).get("subject") or rel),
             "assignment_basis": "folder and file name map", "git": gitinfo([p]), "_name": rel}
        add(e)
    if WORKN + "/results/INDEX.md" in tracked:
        add({"id": "project.note.results-index", "kind": "note", "module": "project", "path": "WORK:results/INDEX.md",
             "note": "Results index. Generated by registry/make_index.py from REGISTRY.json; do not edit by hand.",
             "assignment_basis": "generated registry output", "git": gitinfo([WORKN + "/results/INDEX.md"])})
    hh = [p for p in tracked if p.startswith(WORKN + "/Hydroacoustic Handover/")]
    add({"id": "project.archive.hydroacoustic-handover", "kind": "archive", "module": "project", "path": "WORK:Hydroacoustic Handover",
         "note": f"Hydroacoustic Handover folder ({len(hh)} files). Registered in place as a read-only archive (proposal 5.3.3). Notes refer to its paths; do not move.",
         "assignment_basis": "proposal 5.3.3", "git": gitinfo(hh)})

    # ---------- 3. repository root ----------
    rootitems = collections.defaultdict(list)
    for p in tracked:
        if p.startswith(WORKN + "/"):
            continue
        r = p.split("/")
        rootitems[r[0] if len(r) > 1 else "_root-files"].append(p)
    for k, files in sorted(rootitems.items()):
        if k == "tmp":
            continue
        if k == ARCHIVE_DIR:
            subs = collections.defaultdict(list)
            for p in files:
                subs[p.split("/")[1]].append(p)
            for s, fs in sorted(subs.items()):
                if s in ("MANIFEST.tsv", "MANIFEST.md"):
                    continue
                add({"id": f"project.archive.loose-{slug(s)}", "kind": "archive", "module": "project", "path": f"REPO:{ARCHIVE_DIR}/{s}",
                     "note": f"Root folder {s}/ moved here with git mv on 25 Oct 2026 ({len(fs)} files). Path before and after: {ARCHIVE_DIR}/MANIFEST.tsv.",
                     "assignment_basis": "root loose folder", "git": gitinfo(fs)})
            add({"id": "project.note.archive-sep29-manifest", "kind": "note", "module": "project", "path": f"REPO:{ARCHIVE_DIR}/MANIFEST.tsv",
                 "note": "Path before, path after, bytes and SHA-256 of each file moved into the archive folder.", "assignment_basis": "root loose folder"})
            continue
        if k == "library_full_audit":   # what stays in place
            wb = [p for p in files if p.endswith("9M-MRO Fuel Model V5.X.xlsm")]
            m371 = [p for p in files if p not in wb]
            # Ulich's fuel workbook (FPPM-confidential cells): restricted holding (ledger, Pete 9-10 Oct 2026)
            add({"id": "project.in.library-full-audit-mh370", "kind": "input", "module": "project", "path": "REPO:library_full_audit/MH370",
                 "file_list": wb, "status": "CURRENT_WITH_CAVEATS", "status_rank": "ruling", "restricted": True,
                 "note": "Ulich's fuel workbook (FPPM-confidential cells). Kept in place, not moved. " + RESTRICTED_NOTE,
                 "uses_recorded_in": "WORK:results/restricted-sources-ledger.md",
                 "_evidence": [{"file": "WORK:results/restricted-sources-ledger.md", "must_contain": "library_full_audit/MH370/9M-MRO Fuel Model V5.X.xlsm` | Ulich"},
                               {"file": "WORK:results/restricted-sources-ledger.md", "must_contain": "stays where it is"},
                               {"memory": "mem_77ee3e310c8e", "must_contain": "Internal use is authorised in full"}],
                 "assignment_basis": "restricted-sources ledger", "git": gitinfo(wb)})
            # MH371 ACARS and EHM reports: not confidential (Pete, 26 Oct 2026); status unchanged; files stay in place
            add({"id": "project.in.library-full-audit-mh371", "kind": "input", "module": "project", "path": "REPO:library_full_audit/MH370",
                 "file_list": m371, "status": "CURRENT_WITH_CAVEATS", "status_rank": "ruling",
                 "note": ("MH371 ACARS and EHM reports (9M-MRO, 7 Mar 2014); the EHM export also holds the MH370 climb report. Kept in place, not moved. "
                          "Not confidential (Pete, 26 Oct 2026); provenance not verified."),
                 "status_note": "Split from project.in.library-full-audit-mh370 on 26 Oct 2026, when Pete ruled the MH371 items not confidential. Status unchanged.",
                 "_evidence": [{"file": "WORK:results/restricted-sources-ledger.md", "must_contain": "Pete ruled on 26 October 2026 that the MH371 items are NOT confidential"},
                               {"file": "WORK:results/restricted-sources-ledger.md", "must_contain": "stays where it is"}],
                 "assignment_basis": "restricted-sources ledger (reclassified section)", "git": gitinfo(m371)})
            continue
        if k in MOVED:
            report["moved_folder_still_at_root"].append(k)
        note = {"ISO Sept 28 Status": "FROZEN snapshot of 28 Sep 2026 (Pete's rule). Never edit.",
                "Archive ISO Pre Sept 28": "Archive of work before 28 Sep 2026 (contains codebases/v01-share-withdrawn).",
                "_root-files": "Loose files at the repository root."}.get(k, f"Root folder {k}/.")
        add({"id": f"project.archive.root-{slug(k)}", "kind": "archive", "module": "project", "path": f"REPO:{k if k != '_root-files' else ''}",
             "file_list": files if k == "_root-files" else None, "note": f"{note} ({len(files)} files)", "assignment_basis": "repository root",
             "git": gitinfo(files)})

    # ---------- 4. tmp/ ----------
    tmpf = sorted(p for p in tracked if p.startswith("tmp/"))
    used = set()
    for name, pat in AVIONICS:
        fs = [p for p in tmpf if re.search(pat, p)]
        used |= set(fs)
        if not fs:
            report["avionics_pattern_without_files"].append(name); continue
        needle = {"avionics_training": "tmp/avionics_training_", "avionics_try": "tmp/avionics_try_", "slideshare_avionics": "tmp/slideshare_avionics/",
                  "scribd_satcom": "tmp/scribd_satcom.html", "paperzz_airlink": "tmp/paperzz_airlink.html",
                  "slideshare_airlink": "tmp/slideshare_airlink.html", "avionics_min": "tmp/avionics_min-1.png"}[name]
        add({"id": f"project.in.tmp-{slug(name)}", "kind": "input", "module": "project", "path": "REPO:tmp/", "file_list": fs,
             "status": "CURRENT_WITH_CAVEATS", "status_rank": "ruling", "restricted": True,
             "note": f"tmp/ avionics material: {name} ({len(fs)} files). Provenance not verified. " + RESTRICTED_NOTE,
             "_evidence": [{"memory": "mem_bb853bca3bb6", "must_contain": "record every use in results/restricted-sources-ledger.md"},
                           {"memory": "mem_77ee3e310c8e", "must_contain": "Internal use is authorised in full"},
                           {"file": "WORK:results/restricted-sources-ledger.md", "must_contain": needle}],
             "uses_recorded_in": "WORK:results/restricted-sources-ledger.md", "assignment_basis": "Pete's ruling 9-10 Oct 2026", "git": gitinfo(fs)})
    rest = [p for p in tmpf if p not in used]
    add({"id": "project.scratch.tmp", "kind": "scratch", "module": "project", "path": "REPO:tmp/", "file_list": rest,
         "note": f"tmp/ scratch files ({len(rest)} files): HGA images, fuel-table inspection dumps, PDFs. Not a source of record.",
         "assignment_basis": "tmp/ less the restricted avionics files", "git": gitinfo(rest)})

    # ---------- 5. exchange folder (stat + SHA256SUMS + hashes < 1 GB from exchange_inventory.py) ----------
    exg = collections.defaultdict(list)
    for r in inv["files"]:
        parts = r["rel"].split("/")
        exg[(parts[0], parts[1] if len(parts) > 2 else "_top-files")].append(r)
    mvx = json.load(open(HERE / "data_homes" / "moved_to_xdrive.json"))["moves"] if (HERE / "data_homes" / "moved_to_xdrive.json").exists() else {}
    for (top_, sub), rows in sorted(exg.items()):
        if f"{top_}/{sub}" in mvx:   # moved to the external drive (only copy): entry made in section 6
            continue
        mod = EX_MOD.get(top_)
        if mod is None:
            report["exchange_unmapped"].append(top_); continue
        nb = sum(1 for r in rows if r.get("sha256") is None)
        add({"id": f"{PREFIX[mod]}.ex.{slug(top_)}-{slug(sub)}", "kind": "product" if top_ != "archive" else "archive", "module": mod,
             "path": f"EX:{top_}/{sub if sub != '_top-files' else ''}", "exchange_prefix": f"{top_}/{sub}" if sub != "_top-files" else top_ + "/", "exchange_top_files_only": sub == "_top-files",
             "note": f"Exchange folder {top_}/{sub}: {len(rows)} files, {sum(r.get('bytes', 0) for r in rows) / 1e9:.2f} GB; "
                     f"SHA-256 from SHA256SUMS {sum(1 for r in rows if str(r.get('sha_source', '')).startswith('SHA256SUMS'))}, "
                     f"computed {sum(1 for r in rows if str(r.get('sha_source', '')).startswith('computed'))}, not hashed {nb}.",
             "assignment_basis": "exchange folder name"})
    absent = collections.Counter("/".join(k.split("/")[:2]) for k in inv.get("sums_entries_without_file", []))
    for e in E:
        if e["path"].startswith("EX:"):
            k = e["path"][3:].rstrip("/")
            if absent.get(k):
                e["note"] += f" {absent[k]} files listed in a SHA256SUMS file here are not in the folder now."

    # ---------- 6. external drive (archive-to-porsche scripts) ----------
    at = Path("/Users/pete/Downloads/archive-tools")
    for script in ("archive-to-porsche.v3.sh", "archive-to-porsche.sh"):
        sp = at / script
        if not sp.exists():
            report["archive_script_missing"].append(script); continue
        lines = sp.read_text().splitlines()
        dest = next((re.search(r'DEST:-([^}]*)\}', l).group(1) for l in lines if "DEST=" in l and "DEST:-" in l), None)
        for i, l in enumerate(lines, 1):
            m = re.match(r'\s*"(mh370-[^"]+)"', l)
            if not m:
                continue
            rel = m.group(1)
            if "/hydroacoustics" in rel:
                report["xdrive_hydro_left_for_phase2"].append(rel); continue
            parts = rel.split("/")
            mod = EX_MOD.get(parts[1], "project") if parts[0] == "mh370-exchange" else "project"
            present = (Path("/Users/pete/Downloads") / rel).exists()
            add({"id": f"{PREFIX[mod]}.xd.{slug('-'.join(parts[1:]))}", "kind": "archive", "module": mod, "path": f"XDRIVE:{rel}",
                 "note": (f"Listed for copy to the external drive in archive-tools/{script} line {i} (destination {dest}). "
                          f"Source folder in ~/Downloads now: {'present' if present else 'absent'}. The VERIFIED-*.txt list is on the drive; "
                          f"it was not readable from this session, so the copy is not confirmed here."),
                 "assignment_basis": "archive script item list", "hash": False, "hash_note": "external drive not mounted in this session",
                 "holder": XHOLDER})
    for pre, m in sorted(mvx.items()):   # exchange folders moved to the external drive; per-file SHA-256 from the record
        ev = m["status_evidence"]
        add({"id": m["entry_id"], "kind": "archive", "module": "project", "path": f"XDRIVE:{m['xdrive_path']}", "holder": m["holder"],
             "note": m["note"] + ". " + m["deleted_note"] + f" Moved from the exchange folder ({pre}) on {m['date']}.",
             "status": m["status"], "status_rank": "verified", "status_evidence": [{"rank": "verified", "source": ev["source"], "quote": ev["quote"]}],
             "file_rows": m["file_rows"], "hash": "rows", "hash_note": "SHA-256 per file: " + m["sha256_source"],
             "platform_artifacts_deleted": m["platform_artifacts_deleted"], "assignment_basis": "data_homes/moved_to_xdrive.json"})

    # ---------- 7. Drive file ids ----------
    DPAT = re.compile(r"(?:drive\.google\.com/(?:file/d/|open\?id=|drive/folders/)|[Dd]rive (?:file )?id[:\s`]*)([A-Za-z0-9_-]{20,})")
    seen = {}
    for p in tracked:
        if not p.endswith((".md", ".txt", ".yaml", ".json", ".csv", ".bib")) or "hydroacoustic" in p.lower() or p.startswith(("ISO Sept 28", "Archive ISO", "Sept 27")):
            continue
        try:
            t = (top / p).read_text(errors="replace").splitlines()
        except Exception:
            continue
        if p.startswith(WORKN + "/registry/"):
            continue   # generated registry files are not a source of Drive ids
        for i, l in enumerate(t, 1):
            if l.startswith("| `mem_"):
                continue   # generated citation-ledger rows (memory text) are not a source of Drive ids
            for m in DPAT.finditer(l):
                seen.setdefault(m.group(1), (p, i))
    for did, (p, i) in sorted(seen.items()):
        mod = "core" if "/results/evidence-sweep" in p else "project"
        root = "WORK:" + p[len(WORKN) + 1:] if p.startswith(WORKN) else "REPO:" + p
        ext = slug(did) in EXTERNAL_DRIVE
        add({"id": f"{PREFIX[mod]}.drive.{slug(did)}", "kind": "input", "module": mod, "path": f"DRIVE:{did}",
             "drive_link": "third-party" if ext else "project",
             "note": (f"Third-party Google Drive link given in {root} line {i}. Not a project-Drive file; the project Drive gives no metadata for it "
                      f"(independent check, 25 Oct 2026). Not opened." if ext else f"Google Drive file id given in {root} line {i}."),
             "drive_id_source": {"file": root, "line": i},
             "assignment_basis": "file that gives the Drive id", "hash": False, "hash_note": "Drive file; not downloaded in this run"})

    # ---------- 8. other data homes in ~/Downloads ----------
    for mod, rel, desc in DATA_HOMES:
        add({"id": f"{PREFIX[mod]}.home.{slug(rel)}", "kind": "data_home", "module": mod, "path": f"DL:{rel}", "note": desc,
             "assignment_basis": "data home", "hash": "stat", "hash_note": "file list and sizes only; SHA-256 taken from SHA256SUMS files where present"})
    add({"id": "project.home.exchange-folder", "kind": "data_home", "module": "project", "path": "EX:",
         "note": f"Exchange folder: run outputs of all modules. {inv['n_files']} files, {inv['bytes'] / 1e9:.1f} GB without hydroacoustics. Hydroacoustics part is registered in phase 2.",
         "assignment_basis": "data home", "hash": False, "hash_note": "see the ex.* entries"})
    add({"id": "project.home.external-drive", "kind": "data_home", "module": "project", "path": "XDRIVE:", "holder": XHOLDER,
         "note": "External drive 'Porsche 1TB Backup', folder mh370-archive (DEST in archive-tools scripts). Single copy; Time Machine does not include it.",
         "assignment_basis": "data home", "hash": False, "hash_note": "drive not mounted in this session"})

    # ---------- 9. code on module branches (by branch and commit; no merge) ----------
    for b, v in sorted(branches.items()):
        mod = BRANCH_MOD.get(b) or ("composer" if b.startswith("core/composer") else "project")
        vw = v.get("vs_work", {})
        add({"id": f"{PREFIX[mod]}.code.branch-{slug(b.replace('/', '-'))}", "kind": "code", "module": mod, "path": f"GIT:{b}@{v['sha']}",
             "git": {"branch": b, "commit": v["sha"], "date": v["date"], "subject": clean(v["subject"]), "tree": v["tree_sha"],
                     "n_files": v["n_files"], "bytes": v["bytes"], "commits_not_in_working_branch": vw.get("branch_commits_not_in_work"),
                     "compared_with_working_head": vw.get("work_head")},
             "note": f"Code on branch {b} at {v['sha'][:12]} ({v['date'][:10]}). {vw.get('branch_commits_not_in_work')} commits are not in the working branch. Not merged (Pete's rule)."
                     + (f" Marked {v['status']} in data_homes/branches.json: {v.get('note', '')}" if v.get("status") else ""),
             "assignment_basis": "branch name", "hash": False, "hash_note": "git objects are content-addressed; tree sha recorded"})

    # ---------- 10. memory notes (rows moved out of memory; records of what memory said) ----------
    mi = HERE / "memory-notes" / "index.json"
    if mi.exists():
        idx = json.load(open(mi))
        for t, v in sorted(idx["topics"].items()):
            add({"id": v["topic_note_entry"], "kind": "note", "module": v["module"], "path": f"WORK:registry/{v['file']}",
                 "note": (f"Memory rows on topic '{t}' moved to the registry on 25 Oct 2026 ({v['rows']} rows; {v['rows_linked_to_topic_note']} have no other entry). "
                          "Records of what memory said, not verified facts; each row has its verification status."),
                 "assignment_basis": "memory track topic", "memory_notes": {"file": f"WORK:registry/{v['file']}", "n_rows": v["rows"]}})
        ids_now = {e["id"]: e for e in E}
        for rid, mids in idx["links"].items():
            e = ids_now.get(rid)
            if e is None:
                report["memory_note_links_to_missing_entry"].append([rid, len(mids)]); continue
            if ".memnote." not in rid:
                e["memory_notes"] = {"n_rows": len(mids), "mem_ids": mids, "where": "WORK:registry/memory-notes/<topic>.jsonl",
                                     "nature": "records of what memory said; not verified facts"}

    # ---------- status ----------
    by_name = {e.get("_name"): e for e in E if e.get("_name")}
    by_id = {e["id"]: e for e in E}
    applied = set()

    def mem_quote(mid, needle):
        b = mem.get(mid, {}).get("body")
        if b is None:
            raise KeyError(f"memory row {mid} not in the export")
        for s in re.split(r"(?<=[.;!?])\s+|\n+", b):
            if needle in s:
                return clean(s.strip()[:400]), mem[mid].get("evidence")
        raise ValueError(f"text {needle!r} not in memory row {mid}")

    def file_quote(spec, line, needle):
        root, _, rel = spec.partition(":")
        p = (work if root == "WORK" else top) / rel
        L = p.read_text(errors="replace").splitlines()
        if line:
            if needle not in L[line - 1]:
                raise ValueError(f"{spec}:{line} does not contain {needle!r}")
            return clean(L[line - 1].strip()[:400]), line
        for i, l in enumerate(L, 1):
            if needle in l:
                return clean(l.strip()[:400]), i
        raise ValueError(f"{spec} does not contain {needle!r}")

    def evidence(specs, rank):
        out = []
        for s in specs:
            if "memory" in s:
                q, ev = mem_quote(s["memory"], s["must_contain"])
                out.append({"rank": rank, "source": f"memory:{s['memory']}", "memory_evidence_tag": ev, "quote": q})
            else:
                q, ln = file_quote(s["file"], s.get("line"), s["must_contain"])
                out.append({"rank": rank, "source": f"{s['file']}:{ln}", "quote": q})
        return out

    errors = []
    for e in E:   # ruling-rank evidence set in the entry itself
        if "_evidence" in e:
            try:
                e["status_evidence"] = evidence(e.pop("_evidence"), e["status_rank"])
            except Exception as ex:
                errors.append(f"{e['id']}: {ex}")
    order = {"ruling": 0, "explicit": 1, "chain": 2, "readme": 3}
    for r in sorted(srec, key=lambda r: order[r["rank"]]):
        e = by_name.get(r["item"]) or by_id.get(r["item"])
        if e is None:
            errors.append(f"status record for unknown item {r['item']}"); continue
        if e["id"] in applied:
            continue
        try:
            ev = evidence(r.get("evidence", []), r["rank"]) if r.get("evidence") else []
        except Exception as ex:
            errors.append(f"{e['id']}: {ex}"); continue
        if r["rank"] == "readme" and not ev:
            ev = [{"rank": "readme", "source": f"WORK:results/{e['_readme']}" if e.get("_readme") else e["path"], "quote": None,
                   "read_by_hand": r.get("readme_override")}]
        e.update(status=r["status"], status_rank=r["rank"], status_evidence=ev, defects=r.get("defects", []))
        if r.get("superseded_by"):
            t = by_name.get(r["superseded_by"]) or by_id.get(r["superseded_by"])
            if t is None:
                errors.append(f"{e['id']}: superseded_by {r['superseded_by']} not found")
            else:
                e["superseded_by"] = t["id"]
        if r.get("note"):
            e["status_note"] = r["note"]
        applied.add(e["id"])
    # chain rule: same module, same name stem without a -vN token; the highest N supersedes the others. X-DRAFT -> X.
    def stem_v(n):
        s = n.rsplit(".", 1)[0] if "." in n.split("/")[-1] else n
        m = re.search(r"(?i)[-_]v(\d+)(?=$|[-_])", s)
        return re.sub(r"(?i)[-_]v\d+(?=$|[-_])", "", s), int(m.group(1)) if m else 1, (n.rsplit(".", 1)[1] if "." in n.split("/")[-1] else "DIR")
    groups = collections.defaultdict(list)
    for e in E:
        n = e.get("_name")
        if n:
            st, v, ext = stem_v(n)
            groups[(e["module"], st, ext)].append((v, e))
            if re.search(r"-DRAFT(\.|$)", n):
                t = by_name.get(n.replace("-DRAFT", ""))
                if t and e["id"] not in applied:
                    e.update(status="SUPERSEDED", status_rank="chain", superseded_by=t["id"],
                             status_evidence=[{"rank": "chain", "source": "name chain", "quote": None, "rule": f"{n} -> {t['_name']} (DRAFT and final of the same name)"}])
                    applied.add(e["id"])
    for k, g in groups.items():
        if len(g) < 2:
            continue
        g.sort(key=lambda x: x[0]); newest = g[-1][1]
        if g[-1][0] == g[-2][0]:
            report["chain_ambiguous"].append([x[1]["id"] for x in g]); continue
        for v, e in g[:-1]:
            if e["id"] in applied:
                continue
            e.update(status="SUPERSEDED", status_rank="chain", superseded_by=newest["id"],
                     status_evidence=[{"rank": "chain", "source": "name chain", "quote": None, "rule": f"{e['_name']} -> {newest['_name']} (same stem, higher version number)"}])
            applied.add(e["id"])
    # date chains: reported, not applied (a later date can be a continuation; see eof-run-j-supplement-oct19/oct20)
    dg = collections.defaultdict(list)
    for e in E:
        n = e.get("_name")
        if n and n in item_mod:
            s = re.sub(r"(?i)[-_](oct\d{2}|2026-\d{2}-\d{2}(-(am|pm))?)(?=$|[-_.])", "", n)
            if s != n:
                dg[(e["module"], s)].append(e["id"])
    report["date_chains_not_applied"] = [v for v in dg.values() if len(v) > 1]
    # readme status lines and banners
    for e in E:
        if e["id"] in applied or not e.get("_readme"):
            continue
        p = res / e["_readme"]
        L = p.read_text(errors="replace").splitlines()[:25]
        hit = next(((i, l) for i, l in enumerate(L, 1) if STAT_LINE.search(l)), None) or \
              next(((i, l) for i, l in enumerate(L[:12], 1) if BANNER.search(l)), None)
        if hit:
            st = map_readme(hit[1])
            if st is None:
                report["readme_status_unmapped"].append([e["id"], clean(hit[1].strip()[:200])]); continue
            e.update(status=st, status_rank="readme",
                     status_evidence=[{"rank": "readme", "source": f"WORK:results/{e['_readme']}:{hit[0]}", "quote": clean(hit[1].strip()[:400])}])
            applied.add(e["id"])
    # statements found in memory / files that name an item but are not applied (for Pete's review)
    names = {e["_name"]: e["id"] for e in E if e.get("_name") and len(e["_name"].rsplit(".", 1)[0]) >= 8}
    pats = {n: re.compile(r"(?<![\w-])" + re.escape(n.rsplit(".", 1)[0] if "." in n.split("/")[-1] else n) + r"(?![\w-])") for n in names}
    for m in mem.values():
        b = m["body"]
        if not STATUS_WORDS.search(b):
            continue
        for s in re.split(r"(?<=[.;!?])\s+|\n+", b):
            if STATUS_WORDS.search(s):
                for n, pt in pats.items():
                    if pt.search(s) and names[n] not in applied:
                        report["statements_not_applied"].append([names[n], f"memory:{m['id']}", clean(s.strip()[:300])])
    # memory status statements about exchange folders
    for e in E:
        if e["path"].startswith("EX:") and not e.get("exchange_top_files_only") and e["path"].rstrip("/").count("/") >= 1:
            k = e["path"][3:].rstrip("/")
            pt = re.compile(r"(?<![\w-])" + re.escape(k) + r"(?![\w-])")
            for m in mem.values():
                if pt.search(m["body"]) and STATUS_WORDS.search(m["body"]):
                    for s in re.split(r"(?<=[.;!?])\s+|\n+", m["body"]):
                        if pt.search(s) and STATUS_WORDS.search(s):
                            report["statements_not_applied"].append([e["id"], f"memory:{m['id']}", clean(s.strip()[:300])])
    # ---------- write ----------
    ids = collections.Counter(e["id"] for e in E)
    for i, c in ids.items():
        if c > 1:
            errors.append(f"duplicate id {i}")
    for e in E:
        for k in [k for k in e if k.startswith("_")]:
            e.pop(k)
    per = collections.defaultdict(list)
    for e in E:
        per[e["module"]].append(e)
    for mod in MODULES:
        d = HERE / "modules" / mod
        d.mkdir(parents=True, exist_ok=True)
        rows = sorted(per.get(mod, []), key=lambda x: x["id"])
        yaml.safe_dump({"registry_version": f"{mod} registry v1 (2026-10-25)", "module": mod,
                        "generated_by": "registry/backfill_registry.py (do not edit by hand; correct status_records.yaml and rebuild)",
                        "entries": rows}, open(d / "entries.yaml", "w"), sort_keys=False, allow_unicode=True, width=160)
    report["errors"] = errors
    report["counts"] = {m: len(per.get(m, [])) for m in MODULES}
    report["results_items"] = {"folders_total": len(folders), "loose_total": len(loose), "hydro_items": len(hydro_items),
                               "registered_results_items": len(name2id)}
    json.dump(report, open(HERE / "backfill_report.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({"counts": report["counts"], "results": report["results_items"], "errors": errors[:20],
                      "statements_not_applied": len(report["statements_not_applied"])}, indent=1))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
