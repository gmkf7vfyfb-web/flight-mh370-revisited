"""Write results/hydroacoustics/INDEX.md (claude-science-sep29) from REGISTRY.json. Never edit INDEX.md by hand.
Usage: python make_index.py <path to INDEX.md> [--stale stale_and_wording.tsv]
"""
import argparse, collections, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Hits in CURRENT notes reviewed by hand on 23 Oct 2026 (note id:line -> result). Add a row when a new hit is reviewed.
REVIEWED = {
    "note.digitised_sources:76": "reviewed: restates Brown 2026's Arons value as Brown's, and says the F-35A spectrum must come from Metz; no change",
    "note.audit_architecture:125": "reviewed: audit finding F6 about Brown's 2.1e-4 (Arons law); correct as written; no change",
    "note.pleiades_test_preregistration:81": "reviewed: pre-registration of 10 Oct records the table used then; historical; no change",
}


def cell(s):
    return str(s if s is not None else "").replace("|", "/").replace("\n", " ")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--stale")
    a = ap.parse_args()
    r = json.load(open(HERE / "REGISTRY.json"))
    E, C, D = r["entries"], r["constants"], r["defects"]
    cnt = collections.Counter(e["status"] for e in E)
    L = ["# Hydroacoustics: index of data, products, notes and defects (generated from the registry)", "",
         f"*Generated from `engine/hypotheses/hydroacoustics/registry/REGISTRY.json` on `hypothesis/hydroacoustics` "
         f"({r['registry_version']}; built {r['built_utc']}; module {r['git']['module_branch'][:12]}; work branch "
         f"{r['git']['work_branch'][:12]}; sha256 manifests: {'yes' if r['hashing'] else 'no'}). Do not edit by hand: change "
         f"`entries.yaml`, rebuild, regenerate.*", "",
         "**How to use.** Find the item below. Read its status and defects. Read its definition (quoted in REGISTRY.json from the "
         "cited lines). Use only CURRENT or CURRENT_WITH_CAVEATS items for results, and state the listed defects beside every "
         "number. Pete's rulings: `decisions.md`. Proposals that are not yet rules: `proposals.md`.", "",
         "**Status counts:** " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())), "",
         "## Status values", "", "| status | meaning |", "|---|---|"]
    L += [f"| {k} | {cell(v)} |" for k, v in r["status_values"].items()]
    for kind, title in [("input", "Inputs"), ("product", "Products"), ("note", "Results notes (claude-science-sep29)"), ("code", "Code")]:
        L += ["", f"## {title}", "", "| id | status | defects | path | files | GB | definition source |", "|---|---|---|---|---|---|---|"]
        for e in [x for x in E if x["kind"] == kind]:
            d = e.get("definition") or {}
            src = f"{d.get('file')} L{d.get('lines')}" if d.get("file") else d.get("note", "")
            gb = f"{e['bytes']/1e9:.3f}" if e.get("bytes") else ""
            sup = f" -> {e['superseded_by']}" if e.get("superseded_by") else ""
            L.append(f"| {e['id']} | {e['status']}{sup} | {', '.join(e.get('defects', []))} | `{cell(e['path'])}` | {e.get('n_files') or ''} | {gb} | {cell(src)} |")
    L += ["", "## Defects", "", "| id | defect | what | fixed in this run | affects |", "|---|---|---|---|---|"]
    L += [f"| {d['id']} | {cell(d['title'])} | {cell(d.get('what'))} | {cell(d.get('fixed_this_run'))} | {', '.join(d['affects'])} |" for d in D]
    L += ["", "## Constants", "", "| id | value | units | status | note | source |", "|---|---|---|---|---|---|"]
    for c in C:
        s = c["source"]
        L.append(f"| {c['id']} | {cell(c['value'])} | {cell(c['units'])} | {c['status']} | {cell(c.get('note'))} | {cell(s.get('file'))} L{s.get('lines')} |")
    if a.stale and Path(a.stale).exists():
        rows = [x.split("\t") for x in Path(a.stale).read_text().splitlines() if x.startswith(("STALE\tnote.", "WORDING\tnote."))]
        L += ["", "## Lines in the notes that still use a retired value or ruled-out wording", "",
              "Found by `check_registry.py --stale --wording` after the status banners were added. Notes with a status other than "
              "CURRENT carry a one-line banner at the top that states the correction. Notes with status CURRENT carry no banner; "
              "each of their hits is marked below with the result of a review in this run. Lines that quote the old value in order "
              "to correct it are not listed.", "",
              "| check | note | status | line | text (first 160 characters) | handling |", "|---|---|---|---|---|---|"]
        for x in rows:
            p, _, ln = x[3].rpartition(":")
            key = f"{x[1]}:{ln}"
            if x[2] != "CURRENT":
                how = "banner at top of note"
            else:
                how = REVIEWED.get(key, "NOT REVIEWED in this run")
            L.append(f"| {x[0]} | {x[1]} | {x[2]} | {Path(p).name}:{ln} | {cell(x[4])} | {cell(how)} |")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(L) + "\n")
    print("wrote", a.out, len(L), "lines")


if __name__ == "__main__":
    main()
