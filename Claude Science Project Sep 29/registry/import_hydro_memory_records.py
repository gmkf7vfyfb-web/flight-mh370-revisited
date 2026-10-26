#!/usr/bin/env python3
"""Phase 2 (26 Oct 2026): store the hydroacoustics memory rows as registry notes and citation-ledger rows.

Same rules and same row format as import_memory_records.py (phase 1), which skipped these rows:
  * 216 rows with action move-to-registry and target on hypothesis/hydroacoustics -> memory-notes/hydroacoustics.jsonl in the
    hydro registry (branch hypothesis/hydroacoustics, engine/hypotheses/hydroacoustics/registry/memory-notes/).
  * 11 rows with action defer-hydro (written after the export) -> memory-notes/deferred-hydro.jsonl. Their text is not in the
    export; it comes from --deferred (the memory rows as read on 26 Oct 2026, read-only). They were not content-verified.
  * 45 rows with action move-to-citation-ledger and ledger results/hydroacoustics-references.md -> a generated section in that
    file, with the status from the external-facts verification CSV and the verifier fixes of phase 1 (VERIFIER_FIXES).
THESE ROWS ARE RECORDS OF WHAT MEMORY SAID. They are not verified facts. Restricted-source text is withheld (public repository);
session-workspace paths are replaced.
A row links to a registry entry only when the memory track gave one, or when the row text names the path of exactly one
hydro entry (last path part, 12 characters or more): link "name match (registry track, 26 Oct 2026)". Otherwise the row links
to the topic note entry note.memnote_hydroacoustics.
Usage: python3 import_hydro_memory_records.py --export <jsonl> --changes <csv> --facts <csv> --deferred <json> --hydro-registry <dir>
       [--export-vid ...] [--changes-vid ...] [--facts-vid ...]
"""
import argparse, collections, csv, hashlib, json, re, sys
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_memory_records as P1  # noqa: E402

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
LEDGER = "Claude Science Project Sep 29/results/hydroacoustics-references.md"
# Independent verifier of 26 Oct 2026 (hydro-verifier-failures-2026-10-26.csv, check 6): facts found that the memory track did not find.
HYDRO_VERIFIER_FIXES = {
    "mem_e89bb8698858": {"status": "VERIFIED",
                         "append_source": "CMST 2014-30 PDF p. 21 table: arrival 1.98-2.00 h after 00:00 UTC, bearing 92.5-93.5 deg, 'Small earthquake in the Java Trench'. CMST gives the time as a range; the exact time 01:58:55 is not printed.",
                         "finding": "MINOR fixed 26 Oct 2026: item 1 (CMST) VERIFIED at PDF p. 21 (time is a range in CMST); item 2 was VERIFIED; status PARTIAL -> VERIFIED."},
    "mem_bac90d8699b2": {"status": "VERIFIED",
                         "append_source": "Arons relation Eq. 2 (Ppeak = 52.4e6 (R/W^1/3)^-1.13): arXiv 2604.12723 PDF p. 10. Leslie 1964, JASA 36:1138-1144 (Crossref 10.1121/1.1919174).",
                         "finding": "MINOR fixed 26 Oct 2026: items 3 (Arons Eq. 2, arXiv 2604.12723 PDF p. 10) and 4 (Leslie 1964, Crossref 10.1121/1.1919174) found; items 1-2 were VERIFIED; status PARTIAL -> VERIFIED."},
}
TOPIC_NOTE = "note.memnote_hydroacoustics"


def main():
    ap = argparse.ArgumentParser()
    for k in ("export", "changes", "facts", "deferred", "hydro-registry"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--export-vid", default="ba131e4c-350c-4db5-8b56-a61b3f2772f9")
    ap.add_argument("--changes-vid", default="49868988"); ap.add_argument("--facts-vid", default="fdfbc300")
    a = ap.parse_args()
    hreg = Path(a.hydro_registry)
    raw = open(a.export, "rb").read()
    exp = {json.loads(l)["id"]: json.loads(l) for l in raw.decode().splitlines() if l.strip()}
    ch = list(csv.DictReader(open(a.changes)))
    facts = {r["mem_id"]: r for r in csv.DictReader(open(a.facts))}
    deferred = {d["id"]: d for d in json.load(open(a.deferred))}
    ents = yaml.safe_load(open(hreg / "entries.yaml"))["entries"] + yaml.safe_load(open(hreg / "entries-phase2.yaml"))["entries"]
    names = collections.defaultdict(set)
    for e in ents:
        last = e["path"].split(":", 1)[1].rstrip("/").split("/")[-1]
        if len(last) >= 12:
            names[last].add(e["id"])
    pats = {n: re.compile(r"(?<![\w.-])" + re.escape(n) + r"(?![\w-])") for n in names}
    stats = collections.Counter()

    def link(text):
        hits = {i for n, pt in pats.items() if pt.search(text) for i in names[n]}
        return sorted(hits)[0] if len(hits) == 1 else None

    def row(r, body, src_note):
        mid = r["mem_id"]
        text, flags = P1.clean(mid, body, a.export_vid)
        if src_note and "withheld_restricted" in flags:
            text = f"[text withheld from the repository: it names a restricted source (results/restricted-sources-ledger.md). Full text: project memory row {mid} (not in the export).]"
        for f in flags:
            stats["registry_" + f] += 1
        ent = r.get("registry_entry") or link(body)
        return {"mem_id": mid, "registry_entry": ent or TOPIC_NOTE,
                "link": "existing entry (memory track)" if r.get("registry_entry") else ("name match (registry track, 26 Oct 2026)" if ent else "topic note entry (no entry matched)"),
                "topic": r.get("topic") or "hydroacoustics", "module": "hydroacoustics", "written_utc": r["written_utc"], "memory_evidence_tag": r["orig_evidence"],
                "marker": r.get("marker") or "none", "original_text": text, "text_flags": flags,
                "verification_status": r["verification_status"], "verified_by": P1.cell(r["verified_by"]), "verification_evidence": P1.cell(r["evidence"]),
                "nature": "record of what memory said; not a verified fact", **({"text_source": src_note} if src_note else {})}

    nd = hreg / "memory-notes"; nd.mkdir(exist_ok=True)
    reg_rows = [row(r, exp[r["mem_id"]]["body"], None) for r in ch if r["action"] == "move-to-registry" and r["target_path"].startswith("hypothesis/hydroacoustics")]
    dfr_rows = []
    for r in ch:
        if r["action"] == "defer-hydro":
            d = deferred[r["mem_id"]]
            x = row(r, d["body"], "project memory row read on 26 Oct 2026 (read-only); written after the 25 Oct export, so not in it")
            x["action"] = "defer-hydro (memory track: left until the hydro phase 2 merge)"
            dfr_rows.append(x)
    out = {}
    for name, rows in (("hydroacoustics", reg_rows), ("deferred-hydro", dfr_rows)):
        rows.sort(key=lambda x: (x["written_utc"], x["mem_id"]))
        with open(nd / f"{name}.jsonl", "w", encoding="utf-8") as fh:
            for x in rows:
                fh.write(json.dumps(x, ensure_ascii=False) + "\n")
        out[name] = {"module": "hydroacoustics", "file": f"memory-notes/{name}.jsonl", "rows": len(rows), "topic_note_entry": TOPIC_NOTE,
                     "rows_linked_to_topic_note": sum(1 for x in rows if x["registry_entry"] == TOPIC_NOTE),
                     "rows_linked_by_name_match": sum(1 for x in rows if x["link"].startswith("name match")),
                     "status_counts": dict(collections.Counter(x["verification_status"] for x in rows)),
                     "text_flags": dict(collections.Counter(f for x in rows for f in x["text_flags"]))}
    links = collections.defaultdict(list)
    for x in reg_rows + dfr_rows:
        links[x["registry_entry"]].append(x["mem_id"])
    # ---------- citation ledger rows ----------
    led = []
    for r in ch:
        if r["action"] != "move-to-citation-ledger" or "hydroacoustics-references" not in r["ledger_target"]:
            continue
        mid = r["mem_id"]; f = facts.get(mid, {}); fx = {**P1.VERIFIER_FIXES.get(mid, {}), **HYDRO_VERIFIER_FIXES.get(mid, {})}
        text, flags = P1.clean(mid, exp[mid]["body"], a.export_vid)
        if fx.get("corrected_text"):
            text = "[SUPERSEDED WORDING - the independent verifier found this text wrong; use the corrected text column] " + text
        status = fx.get("status") or f.get("d_status") or r["verification_status"]
        corr = fx["corrected_text"] if "corrected_text" in fx else (f.get("corrected_text") or r["new_text"])
        corr = P1.clean(mid, corr, a.export_vid)[0] if corr else ""
        src = f.get("source", "")
        if fx.get("append_source"):
            src = (src + " " if src else "") + fx["append_source"]
        led.append({"mem_id": mid, "written": r["written_utc"], "text": text, "status": status, "source": src,
                    "method": f.get("method") or r["verified_by"], "evidence": f.get("evidence") or r["evidence"], "corrected": corr, "verifier": fx.get("finding", "")})
        stats["ledger_rows_written"] += 1
        stats["ledger_" + "_".join(flags or ["no_flags"])] += 1
    led.sort(key=lambda x: (x["written"], x["mem_id"]))
    sec = [P1.START.replace("import_memory_records.py", "import_hydro_memory_records.py"), "", "## External facts moved from memory (25 October 2026; written 26 October 2026)", "",
           "These rows are records of what project memory said about external sources. They are not verified facts unless the",
           "status column says VERIFIED or CORRECTED, and even then the check was the memory track's check of the held source.",
           "Status values: VERIFIED (claim found in the source), CORRECTED (claim corrected against the source; use the corrected",
           "text), PARTIAL (part of the claim found), UNVERIFIABLE (no held copy, or the claim was not found). The last column gives",
           "the finding of the independent verifier of 25 October 2026 where there is one. Text that names a restricted source is",
           "withheld here; the memory export row holds it.", "",
           "| mem_id | written (UTC) | memory text | status | source | method and evidence | corrected text | verifier |", "|---|---|---|---|---|---|---|---|"]
    for x in led:
        sec.append("| " + " | ".join(P1.cell(v)[:900] for v in (f"`{x['mem_id']}`", x["written"], x["text"], x["status"], x["source"],
                                                                (x["method"] + "; " + x["evidence"]).strip("; "), x["corrected"], x["verifier"])) + " |")
    sec += ["", P1.END]
    p = WORK.parent / LEDGER
    t = p.read_text()
    st = sec[0]
    if st in t:
        t = t[:t.index(st)] + "\n".join(sec) + t[t.index(P1.END) + len(P1.END):]
    else:
        t = t.rstrip("\n") + "\n\n" + "\n".join(sec) + "\n"
    p.write_text(t)
    index = {"what": "Hydroacoustics memory rows moved to the registry (phase 2, 26 Oct 2026). Records of what memory said; not verified facts.",
             "inputs": {"export_artifact_version": a.export_vid, "export_sha256": hashlib.sha256(raw).hexdigest(),
                        "changes_artifact_version_prefix": a.changes_vid, "changes_sha256": hashlib.sha256(open(a.changes, "rb").read()).hexdigest(),
                        "facts_artifact_version_prefix": a.facts_vid, "facts_sha256": hashlib.sha256(open(a.facts, "rb").read()).hexdigest()},
             "topics": out, "links": {k: sorted(v) for k, v in sorted(links.items())},
             "citation_ledger": {LEDGER: len(led), "status_counts": dict(collections.Counter(x["status"] for x in led))}, "stats": dict(stats)}
    json.dump(index, open(nd / "index.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: index[k] for k in ("topics", "citation_ledger", "stats")}, indent=1))


if __name__ == "__main__":
    main()
