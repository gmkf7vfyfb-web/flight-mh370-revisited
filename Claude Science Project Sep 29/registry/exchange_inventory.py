"""Inventory of the exchange folder for the project registry.
Rules (registry task, 25 Oct 2026):
  * stat every file (path, bytes, mtime);
  * read every SHA256SUMS* file and take the checksum of each file it lists;
  * compute SHA-256 only for a file < 1 GB that has no checksum in a SHA256SUMS file;
  * never hash a file >= 1 GB; count and list those files as 'not hashed';
  * skip the hydroacoustics folder (phase 2).
Output: JSON with one record per file.
Usage: python exchange_inventory.py --root /Users/pete/Downloads/mh370-exchange --out inv.json [--skip hydroacoustics]
"""
import argparse, hashlib, json, os, sys, time
from pathlib import Path
LIMIT = 1 << 30

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--skip", nargs="*", default=["hydroacoustics"]); a = ap.parse_args()
    root = Path(a.root); files = []; sums = {}
    for dp, dn, fn in os.walk(root):
        rel = Path(dp).relative_to(root)
        if rel.parts and rel.parts[0] in a.skip:
            dn[:] = []; continue
        for f in fn:
            p = Path(dp) / f
            try:
                st = p.stat()
            except OSError as ex:
                files.append({"rel": str(p.relative_to(root)), "error": str(ex)}); continue
            files.append({"rel": str(p.relative_to(root)), "bytes": st.st_size, "mtime": int(st.st_mtime)})
            if f.startswith("SHA256SUMS"):
                for line in p.read_text(errors="replace").splitlines():
                    parts = line.strip().split(None, 1)
                    if len(parts) == 2 and len(parts[0]) == 64:
                        name = parts[1].lstrip("*").strip()
                        if name.startswith("./"): name = name[2:]
                        tgt = (Path(dp) / name)
                        try:
                            k = str(tgt.resolve().relative_to(root.resolve()))
                        except ValueError:
                            k = str(tgt)
                        sums.setdefault(k, (parts[0], str(p.relative_to(root))))
    t0 = time.time(); hashed = 0; hb = 0
    for r in files:
        if "bytes" not in r: continue
        if r["rel"] in sums:
            r["sha256"], r["sha_source"] = sums[r["rel"]][0], "SHA256SUMS:" + sums[r["rel"]][1]
        elif r["bytes"] < LIMIT:
            r["sha256"], r["sha_source"] = sha256(root / r["rel"]), "computed 2026-10-25"
            hashed += 1; hb += r["bytes"]
        else:
            r["sha256"], r["sha_source"] = None, "not hashed: >= 1 GB and no SHA256SUMS entry"
    listed_missing = sorted(k for k in sums if not (root / k).exists())
    out = {"root": str(root), "skipped_top_folders": a.skip, "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "n_files": len(files), "bytes": sum(r.get("bytes", 0) for r in files), "n_sha_from_sums": sum(1 for r in files if str(r.get("sha_source","")).startswith("SHA256SUMS")),
           "n_hashed_now": hashed, "bytes_hashed_now": hb, "n_not_hashed": sum(1 for r in files if "bytes" in r and r["sha256"] is None),
           "bytes_not_hashed": sum(r["bytes"] for r in files if "bytes" in r and r["sha256"] is None),
           "sums_entries_without_file": listed_missing, "files": files, "hash_seconds": round(time.time() - t0)}
    json.dump(out, open(a.out, "w"))
    print({k: v for k, v in out.items() if k not in ("files", "sums_entries_without_file")}, "sums without file:", len(listed_missing))

if __name__ == "__main__":
    main()
