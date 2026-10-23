"""Build the hydroacoustic data registry (REGISTRY.json and REGISTRY.yaml) from entries.yaml.

Written 23 Oct 2026 (hydro clean-up run, proposal v6). Rules:
  * entries.yaml is curated by hand. It names each item, its location, the file and line range that DEFINES it,
    its status and the defect ids that apply. It never contains typed-in quotes or typed-in hashes.
  * This script resolves every path, lists every file with size and sha256 (manifests/<id>.tsv.gz),
    and extracts the definition text from the cited lines. A missing file, an empty line range, or a constant
    whose value text does not appear in its cited lines is an ERROR, and the build fails.
Usage:
  python build_registry.py --mod <module dir> --work <'Claude Science Project Sep 29' dir on claude-science-sep29>
                           [--roots roots.yaml] [--no-hash]
"""
import argparse, gzip, hashlib, json, os, subprocess, sys, time
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent


def sha256(p, bufsize=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(bufsize), b""):
            h.update(b)
    return h.hexdigest()


def git_head(d):
    """HEAD at build time plus a dirty flag. The registry is committed AFTER it is built, so the commit that contains it is the
    next one on that branch; content hashes, not this field, tie the manifests to files."""
    env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null"}
    try:
        h = subprocess.run(["git", "-C", str(d), "log", "-1", "--format=%H %cI"], capture_output=True, text=True, env=env).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(d), "status", "--porcelain", "--untracked-files=no", "--", "."], capture_output=True, text=True, env=env).stdout.strip()
        return f"{h} (head at build time; uncommitted changes in scope: {'yes' if dirty else 'no'})"
    except Exception:
        return ""


def resolve(roots, spec):
    root, _, rel = spec.partition(":")
    if root not in roots:
        raise KeyError(f"unknown root {root!r} in {spec!r}")
    return Path(roots[root]) / rel


def quote(path, lines):
    txt = Path(path).read_text(errors="replace").splitlines()
    a, b = lines
    if a < 1 or b > len(txt) or a > b:
        raise ValueError(f"line range {lines} outside {path} ({len(txt)} lines)")
    q = "\n".join(txt[a - 1:b])          # exact lines, no stripping (verifier finding 23 Oct)
    if not q.strip():
        raise ValueError(f"empty quote at {path}:{a}-{b}")
    return q


def manifest(path, do_hash):
    p = Path(path)
    skip = ("__pycache__", ".pytest_cache")
    files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file() and not any(s in x.parts for s in skip))
    rows, total = [], 0
    for f in files:
        s = f.stat().st_size
        total += s
        rows.append((str(f.relative_to(p.parent if p.is_file() else p)), s, sha256(f) if do_hash else ""))
    return rows, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--roots", default=str(HERE / "roots.yaml"))
    ap.add_argument("--no-hash", action="store_true")
    a = ap.parse_args()
    roots = yaml.safe_load(open(a.roots))
    roots["MOD"], roots["WORK"] = str(Path(a.mod).resolve()), str(Path(a.work).resolve())
    spec = yaml.safe_load(open(HERE / "entries.yaml"))
    errors, out_entries = [], []
    (HERE / "manifests").mkdir(exist_ok=True)
    defect_ids = {d["id"] for d in spec["defects"]}
    t0 = time.time()
    for e in spec["entries"]:
        r = dict(e)
        try:
            p = resolve(roots, e["path"])
            if not p.exists():
                raise FileNotFoundError(str(p))
            if e.get("hash", True):
                rows, total = manifest(p, not a.no_hash)
                mf = HERE / "manifests" / f"{e['id']}.tsv.gz"
                with gzip.open(mf, "wt") as fh:
                    fh.write("relpath\tbytes\tsha256\n")
                    for row in rows:
                        fh.write("\t".join(map(str, row)) + "\n")
                body = "\n".join("\t".join(map(str, x)) for x in rows).encode()
                r.update(n_files=len(rows), bytes=total, manifest=f"manifests/{e['id']}.tsv.gz",
                         manifest_sha256=hashlib.sha256(body).hexdigest())
            else:
                r.update(n_files=None, bytes=None, manifest=None, manifest_sha256=None,
                         hash_note=e.get("hash_note", "not hashed (see hash_note)"))
            if "definition" in e:
                d = e["definition"]
                r["definition"] = {"file": d["file"], "lines": d["lines"], "quote": quote(resolve(roots, d["file"]), d["lines"])}
            else:
                r["definition"] = {"file": None, "lines": None, "quote": None, "note": "NO DEFINITION LOCATED"}
            bad = [x for x in e.get("defects", []) if x not in defect_ids]
            if bad:
                raise ValueError(f"unknown defect ids {bad}")
        except Exception as ex:
            errors.append(f"{e['id']}: {type(ex).__name__}: {ex}")
        out_entries.append(r)
        print(f"{e['id']:48s} {r.get('n_files')} files {r.get('bytes')} B  {time.time()-t0:.0f}s", flush=True)
    out_consts = []
    for c in spec["constants"]:
        r = dict(c)
        if c["source"].get("file") is None:
            r["source"] = {**c["source"], "quote": None, "note": "external source; no file in the registry roots"}
            out_consts.append(r)
            continue
        try:
            q = quote(resolve(roots, c["source"]["file"]), c["source"]["lines"])
            for needle in c["source"].get("must_contain", []):
                if needle not in q:
                    raise ValueError(f"value text {needle!r} not in cited lines")
            r["source"] = {**c["source"], "quote": q}
        except KeyError as ex:
            if c["source"].get("file") is None:
                r["source"] = {**c["source"], "quote": None}
            else:
                errors.append(f"constant {c['id']}: {ex}")
        except Exception as ex:
            errors.append(f"constant {c['id']}: {type(ex).__name__}: {ex}")
        out_consts.append(r)
    out_defects = []
    for d in spec["defects"]:
        r = dict(d)
        ev = []
        for x in d.get("evidence", []):
            if "file" in x:
                try:
                    ev.append({**x, "quote": quote(resolve(roots, x["file"]), x["lines"])})
                except Exception as ex:
                    errors.append(f"defect {d['id']} evidence {x['file']}: {type(ex).__name__}: {ex}")
                    ev.append(x)
            else:
                ev.append(x)
        r["evidence"] = ev
        r["affects"] = sorted(e["id"] for e in spec["entries"] if d["id"] in e.get("defects", []))
        out_defects.append(r)
    reg = {
        "registry_version": spec["registry_version"],
        "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hashing": not a.no_hash,
        "git": {"module_branch": git_head(a.mod), "work_branch": git_head(a.work)},
        "roots": {k: v for k, v in roots.items()},
        "status_values": spec["status_values"],
        "entries": out_entries, "constants": out_consts, "defects": out_defects,
        "build_errors": errors,
    }
    json.dump(reg, open(HERE / "REGISTRY.json", "w"), indent=1, ensure_ascii=False)
    yaml.safe_dump(reg, open(HERE / "REGISTRY.yaml", "w"), sort_keys=False, allow_unicode=True, width=140)
    print(f"\n{len(out_entries)} entries, {len(out_consts)} constants, {len(out_defects)} defects, {len(errors)} errors")
    for x in errors:
        print("ERROR", x)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
