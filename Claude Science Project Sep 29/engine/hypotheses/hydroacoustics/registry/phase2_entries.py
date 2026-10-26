#!/usr/bin/env python3
"""Phase 2 of the hydroacoustics registry (26 Oct 2026): add the hydro work of 23-25 Oct and the items left for phase 2.

Writes entries-phase2.yaml (do not edit by hand; correct this script and run it again). build_registry.py reads it.
Rules (project registry README, sections 5 and 6; Pete 23-25 Oct 2026):
  * Register, do not move or redo. No recompute, no new audit. The status comes from existing records only:
      hand-off of the producing thread (its own entries and verifier result) > explicit statement in a record
      > name chain (-vN) > status line or banner in the item's own README or note (first 25 / 12 lines) > UNCHECKED.
  * Every status other than UNCHECKED gives the record: file and line, and the quote (read by this script, not typed).
  * Roots: WORK (claude-science-sep29 checkout), EX (exchange, hydroacoustics part), XDRIVE (external drive, not hashed).
Inputs: --work <'Claude Science Project Sep 29' folder on claude-science-sep29>, --backfill <registry/backfill_report.json>.
"""
import argparse, collections, gzip, json, re, subprocess, sys
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
EXCH = Path("/Users/pete/Downloads/mh370-exchange/hydroacoustics")
WN = "Claude Science Project Sep 29"
STAT_LINE = re.compile(r"(?i)^\s*(>?\s*)?(\*\*)?\s*status\s*(:|\*\*\s*:|:\s*\*\*)")
BANNER = re.compile(r"(?i)^\s*(>|\*\*).*\b(smoke|stand-?in|provisional|not evidence|do not quote|caveat|pilot|unconverged|not converged|draft|not for release)\b")
WS = re.compile("/" + "workspaces/[^\\s`'\")]*" + "|" + "/" + r"\.claude-" + "science/[^\\s`'\")]*")
THREAD = {"c764a583": "c764a583 (Aircraft Impact Acoustic Source Survey)", "c0b15646": "c0b15646 (Hydroacoustic Site Noise Characterization Review)",
          "9e0bf4fe": "9e0bf4fe (Hydroacoustic Data Inventory Review)"}


def map_readme(t):   # same mapping as registry/backfill_registry.py on claude-science-sep29
    t2 = t.lower()
    if re.search(r"\bsuperseded\b", t2): return "SUPERSEDED"
    if re.search(r"\bwithdrawn\b", t2): return "WITHDRAWN"
    if re.search(r"pending (a |pete|ruling|your)|await\w* (pete|a ruling|your)|for pete to|not adopted|proposal", t2): return "PENDING_RULING"
    if re.search(r"provisional|stand-?in|not for release|pipeline test|unconverged|not converged|smoke|exploratory|prelim|draft|caveat|conditional|wip\b|partial|incomplete|in progress|running|pilot|not yet|not evidence", t2): return "CURRENT_WITH_CAVEATS"
    if re.search(r"complete|final|accepted|adopted|delivered|current|done|pass\b|passed|verified|measured", t2): return "CURRENT"
    return None


def slug(s):
    return re.sub(r"[^a-z0-9_]+", "_", s.lower().replace("-", "_").replace(".", "_")).strip("_")


def clean(s):
    return WS.sub("<session workspace path>", s)


def line_quote(path, needle):
    for i, l in enumerate(Path(path).read_text(errors="replace").splitlines(), 1):
        if needle in l:
            return i, clean(l.strip()[:400])
    raise ValueError(f"{path}: {needle!r} not found")


def first_heading(p):
    try:
        for line in Path(p).read_text(errors="replace").splitlines()[:40]:
            if line.startswith("# "):
                return clean(line[2:].strip()[:200])
    except Exception:
        pass
    return None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--work", required=True); ap.add_argument("--backfill", required=True)
    a = ap.parse_args()
    work = Path(a.work).resolve(); res = work / "results"; top = work.parent
    tracked = [p for p in subprocess.run(["git", "ls-files", "-z"], cwd=top, capture_output=True, text=True).stdout.split("\0") if p]
    spec = yaml.safe_load(open(HERE / "entries.yaml"))
    have_work = {e["path"][5:].rstrip("/") for e in spec["entries"] if e["path"].startswith("WORK:")}
    have_ex = [e["path"][3:].rstrip("/") for e in spec["entries"] if e["path"].startswith("EX:")]
    hid = {e["path"][5:]: e["id"] for e in spec["entries"] if e["path"].startswith("WORK:results/")}
    bf = json.load(open(a.backfill))
    E, D, report = [], [], collections.defaultdict(list)
    rp = WN + "/results/"

    def add(e):
        e.setdefault("defects", []); e.setdefault("verified_this_run", False); e.setdefault("status", "UNCHECKED")
        e.setdefault("status_rank", "none"); e.setdefault("status_evidence", []); e.setdefault("superseded_by", None)
        E.append(e)

    def ev_file(root, rel, needle, rank):
        base = work if root == "WORK" else EXCH
        ln, q = line_quote(base / rel, needle)
        return {"rank": rank, "source": f"{root}:{rel}:{ln}", "quote": q}

    def readme_status(e, root, rel):
        base = work if root == "WORK" else EXCH
        L = (base / rel).read_text(errors="replace").splitlines()[:25]
        hit = next(((i, l) for i, l in enumerate(L, 1) if STAT_LINE.search(l)), None) or \
              next(((i, l) for i, l in enumerate(L[:12], 1) if BANNER.search(l)), None)
        if not hit:
            return
        st = map_readme(hit[1])
        if st is None:
            report["readme_status_unmapped"].append([e["id"], clean(hit[1].strip()[:200])]); return
        e.update(status=st, status_rank="readme", status_evidence=[{"rank": "readme", "source": f"{root}:{rel}:{hit[0]}", "quote": clean(hit[1].strip()[:400])}])

    # ---------- 1. hand-off of session c764a583 (entries and manifests in the hand-off folder) ----------
    hof = res / "hydroacoustics/source-survey-2026-10-23/registry-handoff"
    hy = yaml.safe_load(open(hof / "entries-c764a583.yaml"))
    hlines = (hof / "entries-c764a583.yaml").read_text().splitlines()
    for x in hy["entries"]:
        e = {k: v for k, v in x.items() if k not in ("manifest",)}
        mf = hof / x["manifest"]
        rows = [l.split("\t") for l in gzip.open(mf, "rt").read().splitlines()[1:]]
        e["file_list"] = [r[0] for r in rows]
        ln = next(i for i, l in enumerate(hlines, 1) if l.strip() == f"- id: {x['id']}")
        sl = next(i for i in range(ln, ln + 8) if hlines[i - 1].strip().startswith("status:"))
        e["status_rank"] = "handoff"
        e["status_evidence"] = [{"rank": "handoff", "source": f"WORK:results/hydroacoustics/source-survey-2026-10-23/registry-handoff/entries-c764a583.yaml:{sl}",
                                 "quote": hlines[sl - 1].strip()}]
        if x["id"].startswith("res.raw_ims"):
            e["status_evidence"].append(ev_file("WORK", "coordination/archive/HYDROACOUSTICS-2026-10-07-to-2026-10-26.md", "Independent verifier: 12 headline items", "verifier"))
        if x.get("defects") and any(not str(d).startswith("D") for d in x["defects"]):
            e["defects"] = ["D28"]
            e["status_note"] = "Hand-off defect text: " + "; ".join(str(d) for d in x["defects"])
        if not x["id"].startswith("res.raw_ims"):
            # RULE 4 (coordination/HYDROACOUSTICS.md, 26 Oct 2026; inbox archived the same day to coordination/archive/HYDROACOUSTICS-2026-10-07-to-2026-10-26.md): only an independent verifier sets CURRENT. These three
            # entries have the producer's hand-off only (independent verifier of 26 Oct 2026, hydro-verifier-failures-2026-10-26.csv).
            r4 = ev_file("WORK", "coordination/archive/HYDROACOUSTICS-2026-10-07-to-2026-10-26.md", "RULE 4. A new result starts as UNCHECKED", "rule")
            if e["status"] == "CURRENT":
                e["status"] = "CURRENT_WITH_CAVEATS"
                e["status_note"] = "Producer hand-off only; no independent verifier pass (RULE 4). The hand-off gives CURRENT; the registry gives CURRENT_WITH_CAVEATS."
            else:
                e["status_note"] = "Producer hand-off only; no independent verifier pass (RULE 4)."
            e["status_evidence"].append(r4)
        e["producing_thread"] = THREAD["c764a583"]
        e["handoff_manifest"] = f"WORK:results/hydroacoustics/source-survey-2026-10-23/registry-handoff/{x['manifest']}"
        add(e)
    ln, q = line_quote(work / "results/hydroacoustics/source-survey-2026-10-23/raw-data-2026-10-25/README.md", "**Route lengths in the Kadri replication.**")
    D.append({"id": "D28", "title": "Kadri replication: route lengths 1-4 % too long (erratum 2 of the wave-3 verifier)",
              "what": "water_route.py sums 8-neighbour grid steps without smoothing. The Sriwijaya 182 and AB Aviation 1103 offsets are too negative by about 26 s and 84 s. The conclusions do not change (README).",
              "evidence": [{"file": "WORK:results/hydroacoustics/source-survey-2026-10-23/raw-data-2026-10-25/README.md", "lines": [ln, ln]}],
              "fixed_this_run": "no (erratum in README; notes not edited)"})
    hl = [p[len(rp):] for p in tracked if p.startswith(rp + "hydroacoustics/source-survey-2026-10-23/registry-handoff/")]
    add({"id": "note.registry_handoff_c764a583", "kind": "note", "path": "WORK:results/hydroacoustics/source-survey-2026-10-23/registry-handoff",
         "note": f"Registry hand-off of session c764a583: entries-c764a583.yaml and {len(hl) - 1} manifests (record of what that session proposed).",
         "producing_thread": THREAD["c764a583"]})

    # ---------- 2. results/hydroacoustics/ top files ----------
    top_files = sorted(p[len(rp):] for p in tracked if p.startswith(rp + "hydroacoustics/") and p[len(rp + "hydroacoustics/"):].count("/") == 0)
    for f in top_files:
        n = f.split("/")[-1]
        e = {"id": "note.hydro_" + slug(n.rsplit(".", 1)[0]) if n.endswith((".md", ".txt")) else "res.hydro_" + slug(n), "kind": "note" if n.endswith((".md", ".txt")) else "product",
             "path": f"WORK:results/{f}", "note": first_heading(res / f) or n}
        if n == "INDEX.md":
            e["note"] = "Hydroacoustics index, generated from the hydro registry on hypothesis/hydroacoustics (make_index.py). Do not edit by hand."
            e["hash"] = False
            e["hash_note"] = "generated from this registry after each build (make_index.py), so a hash in the registry would always be one build old; not hashed"
        add(e)
    by = {x["path"]: x for x in E}
    bef, aft = by["WORK:results/hydroacoustics/profile-prompt-HYDROACOUSTIC_MODULE-before-2026-10-23.txt"], by["WORK:results/hydroacoustics/profile-prompt-HYDROACOUSTIC_MODULE-after-2026-10-23.txt"]
    bef.update(status="SUPERSEDED", status_rank="explicit", superseded_by=aft["id"],
               status_evidence=[ev_file("WORK", "coordination/archive/HYDROACOUSTICS-2026-10-07-to-2026-10-26.md", "The HYDROACOUSTIC_MODULE profile prompt was replaced", "explicit")])

    # ---------- 3. back-to-basics (session c0b15646) and the other results folders ----------
    folders = collections.defaultdict(list)
    for p in tracked:
        if p.startswith(rp):
            r = p[len(rp):].split("/")
            if len(r) > 1 and r[0].startswith("hydroacoustics") and r[0] != "hydroacoustics":
                folders[r[0]].append(p[len(rp):])
    SPLIT = {"hydroacoustics-back-to-basics-2026-10-23", "hydroacoustics-graphics-2026-10-22"}
    for n, files in sorted(folders.items()):
        if n in SPLIT:
            subs = collections.defaultdict(list)
            for f in files:
                subs[f.split("/")[1] if f.count("/") >= 2 else "_top"].append(f)
            for sname, sf in sorted(subs.items()):
                rid = f"res.{slug(n.replace('hydroacoustics-', ''))}.{slug(sname)}"
                path = f"WORK:results/{n}/{sname}"
                rd = sorted(f for f in sf if f.count("/") == 2 and re.match(r"(?i)(readme|note)", f.split("/")[-1]))
                e = {"id": rid, "kind": "product", "path": path, "note": (first_heading(res / rd[0]) if rd else None) or f"{n}/{sname} ({len(sf)} files)"}
                if n == "hydroacoustics-back-to-basics-2026-10-23":
                    e["producing_thread"] = THREAD["c0b15646"]
                if rd:
                    e["definition"] = {"file": f"WORK:results/{rd[0]}", "lines": [1, min(6, len((res / rd[0]).read_text(errors='replace').splitlines()))]}
                    readme_status(e, "WORK", f"results/{rd[0]}")
                add(e)
        else:
            rd = sorted(f for f in files if f.count("/") == 1 and f.split("/")[-1].lower().startswith("readme"))
            e = {"id": f"res.{slug(n.replace('hydroacoustics-', ''))}", "kind": "product", "path": f"WORK:results/{n}",
                 "note": (first_heading(res / rd[0]) if rd else None) or f"{n} ({len(files)} files)"}
            if rd:
                readme_status(e, "WORK", f"results/{rd[0]}")
            add(e)
    # explicit statement: noise-vs-levels-corrected replaces the 22 Oct charts 1-3 (deleted from the repo before this registry)
    ue = next(x for x in E if x["path"].endswith("hydroacoustics-graphics-2026-10-22/updated-examples"))
    nv = next(x for x in E if x["path"].endswith("noise-vs-levels-corrected"))
    q = ev_file("WORK", "results/hydroacoustics-back-to-basics-2026-10-23/noise-vs-levels-corrected/README.md", "Replaces the 22 Oct charts 1-3", "explicit")
    ue["status_note"] = (f"Charts 1-3 and their companions of this folder are replaced by {nv['id']} and are no longer in the repo ({q['source']}). "
                         "The remaining charts 4-10 have no status record. The README names the coupling value 2.1e-4 (registry defect D01 is about that value; not applied here: no record links them).")
    # ---------- 4. loose files at the top of results/ ----------
    loose = [i for i in bf["results_hydro_left_for_phase2"] if "/" not in i and (res / i).is_file() and f"results/{i}" not in have_work]
    for n in loose:
        e = {"id": "res.file." + slug(n), "kind": "note" if n.endswith(".md") else "product", "path": f"WORK:results/{n}", "note": first_heading(res / n) if n.endswith(".md") else n}
        stem = n.rsplit(".", 1)[0]
        cands = sorted((k for k in hid if stem.startswith(Path(k).stem) and Path(k).suffix == ".md"), key=len)
        if cands:
            e["companion_of"] = hid[cands[-1]]
        if n.endswith(".md"):
            readme_status(e, "WORK", f"results/{n}")
        add(e)
    # ---------- 5. coordination and thread files ----------
    for rel in bf["coordination_hydro_left_for_phase2"] + bf["threads_hydro_left_for_phase2"]:
        n = rel.split("/")[-1]
        e = {"id": ("note." if rel.endswith(".md") else "res.") + slug(rel.replace("/", "_").rsplit(".", 1)[0]), "kind": "note" if rel.endswith(".md") else "product",
             "path": f"WORK:{rel}", "note": first_heading(work / rel) or n}
        if n == "hydro-protected-paths-2026-10-25.csv":
            e["producing_thread"] = THREAD["9e0bf4fe"]
            e["note"] = "Hydro input files cited by hydro_data.sqlite with SHA-256 (keep out of any deletion manifest), plus two folders."
        add(e)
    # ---------- 6. exchange folder (hydroacoustics part): items with no entry ----------
    add({"id": "ex.handover_2026_10_23", "kind": "archive", "path": "EX:handover-2026-10-23",
         "note": "Hand-over package of the 23 Oct hydro clean-up (artifacts of 10 sessions, tool results, transcripts, memory rows, Pete's hydro messages, final error register). Registered in place as a read-only archive; do not move or edit."})
    pre_ln, pre_q = line_quote(EXCH / "potential-signals-PREVIEW-2026-10-23/README.txt", "PREVIEW ONLY")
    add({"id": "ex.potential_signals_preview_2026_10_23", "kind": "product", "path": "EX:potential-signals-PREVIEW-2026-10-23", "status": "SUPERSEDED",
         "status_rank": "explicit", "superseded_by": "ex.potential_signals_2026_10_23",
         "status_evidence": [{"rank": "explicit", "source": f"EX:potential-signals-PREVIEW-2026-10-23/README.txt:{pre_ln}", "quote": pre_q}],
         "note": "Preview tables for graphics code tests only. Not results."})
    gl = (HERE / "entries.yaml").read_text().splitlines()
    gi = next(i for i, l in enumerate(gl, 1) if "FINAL-v2, FINAL and PREVIEW in the same parent folder are SUPERSED" in l)
    for sub, tag in (("FINAL", "first_set"), ("FINAL-v2", "second_set"), ("PREVIEW", "preview")):   # ids without version tokens (rule 3)
        add({"id": f"ex.potential_signals_graphics_{tag}", "kind": "product", "path": f"EX:potential-signals-graphics-2026-10-23/{sub}", "status": "SUPERSEDED",
             "status_rank": "explicit", "superseded_by": "ex.potential_signals_graphics",
             "status_evidence": [{"rank": "explicit", "source": f"MOD:registry/entries.yaml:{gi}", "quote": clean(gl[gi - 1].strip()[:400])}],
             "note": f"Charts of the potential-signal tables, folder {sub}."})
    add({"id": "ex.potential_signals_graphics_top", "kind": "note", "path": "EX:potential-signals-graphics-2026-10-23", "file_list": ["README.md", "code/charts.py"],
         "note": "README (FINAL-v2 text) and code/charts.py at the top of potential-signals-graphics-2026-10-23."})
    add({"id": "ex.run_j_smoke_log", "kind": "scratch", "path": "EX:run-j-smoke.log", "note": "Log of the run J smoke test (17 Oct 2026)."})
    inv = json.load(gzip.open(work / "registry/data_homes/exchange_inventory_hydroacoustics.json.gz", "rt"))
    add({"id": "home.exchange_hydroacoustics", "kind": "data_home", "path": "EX:", "hash": False,
         "hash_note": (f"See the ex.* entries. Inventory {inv['built_utc']}: {inv['n_files']} files, {inv['bytes']} bytes; SHA-256 from SHA256SUMS {inv['n_sha_from_sums']}, "
                       f"computed {inv['n_hashed_now']}, not hashed {inv['n_not_hashed']} (registry/data_homes/exchange_inventory_hydroacoustics.json.gz on claude-science-sep29)."),
         "note": "Exchange folder, hydroacoustics part: run outputs of the hydroacoustic module."})
    # ---------- 7. external drive (archive-tools item lists; drive not mounted) ----------
    at = Path("/Users/pete/Downloads/archive-tools")
    seen = {}
    for script in ("archive-to-porsche.v3.sh", "archive-to-porsche.sh"):
        for i, l in enumerate((at / script).read_text().splitlines(), 1):
            m = re.match(r'\s*"(mh370-[^"]+)"', l)
            if m and "/hydroacoustics" in m.group(1):
                seen.setdefault(m.group(1), []).append(f"archive-tools/{script} line {i}")
    for rel, where in sorted(seen.items()):
        present = (Path("/Users/pete/Downloads") / rel).exists()
        add({"id": "xd." + slug(rel.split("/hydroacoustics/", 1)[1]) + ("_inputs" if rel.startswith("mh370-inputs") else ""), "kind": "archive", "path": f"XDRIVE:{rel}",
             "hash": False, "hash_note": "external drive not mounted in this session",
             "holder": "Porsche drive (available on request from Pete)",
             "note": (f"Listed for copy to the external drive in {'; '.join(where)}. Source in ~/Downloads now: {'present' if present else 'absent'}. "
                      "The VERIFIED-*.txt list is on the drive; it was not readable from this session, so the copy is not confirmed here.")})
    # ---------- 8. memory notes (rows moved out of memory; records of what memory said) ----------
    add({"id": "note.memnote_hydroacoustics", "kind": "note", "path": "MOD:registry/memory-notes",
         "note": ("Hydroacoustics memory rows moved to the registry (216 move-to-registry rows, 11 defer-hydro rows). RECORDS OF WHAT MEMORY SAID, "
                  "not verified facts; each row gives its verification status. Made by registry/import_hydro_memory_records.py on claude-science-sep29.")})
    ids = collections.Counter(x["id"] for x in E)
    dup = [i for i, c in ids.items() if c > 1] + [x["id"] for x in E if x["id"] in {e["id"] for e in spec["entries"]}]
    if dup:
        sys.exit(f"duplicate ids: {dup}")
    out = {"registry_version": "hydro-registry v1, phase 2 (2026-10-26)",
           "generated_by": "registry/phase2_entries.py (do not edit by hand)", "entries": E, "defects": D}
    yaml.safe_dump(out, open(HERE / "entries-phase2.yaml", "w"), sort_keys=False, allow_unicode=True, width=160)
    print(json.dumps({"entries": len(E), "defects": len(D), "status": collections.Counter(x["status"] for x in E),
                      "readme_status_unmapped": report["readme_status_unmapped"]}, indent=1, default=str))


if __name__ == "__main__":
    main()
