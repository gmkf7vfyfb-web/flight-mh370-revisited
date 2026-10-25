#!/usr/bin/env python3
"""Project check for the rules for new work (clean-up proposal of 23 Oct 2026, section 5.6). Standard library only.

Checks
  C1  Each NEW result folder results/<module>/<run id>/ has manifest.json that agrees with manifest.schema.json.
      Its outputs exist with the stated bytes and SHA-256, and its inputs are registry ids that exist.
      A NEW loose file at the top of results/ or directly in results/<module>/ is a FAIL.
      A NEW file in an old (baseline) result folder that has no manifest is a WARN (old folders are closed; use a new run folder).
  C2  No NEW path, and no NEW text in a committed file, contains a session workspace path (the platform deletes those folders).
  C3  No NEW file or folder name uses a version suffix (-v2, _v3, -FINAL, -rev2 ...). The registry holds the version.
  C4  Registries: ids are unique, each superseded_by target exists, each status is a permitted value, no root points to a
      session workspace. Violations recorded in baseline/known_violations.json (the tree at the baseline commit) are listed as KNOWN, not FAIL.

"NEW" means: not in baseline/tracked_paths.txt.gz (all tracked paths at the baseline commit). Thus the check does not fail
on the existing tree. Existing violations go to a report (--report-existing), they are not fixed.

Usage
  python3 check_project.py                       check the working tree (tracked + untracked, not ignored files)
  python3 check_project.py --commit <sha>        check the tree of one commit
  python3 check_project.py --pre-push <remote> <url>   (git pre-push hook; reads ref lines on stdin)
  python3 check_project.py --report-existing <out.md>  list every violation in the baseline tree (C1-C4), exit 0
  python3 check_project.py --make-baseline       write baseline/ from HEAD (only at a registry rebuild; commit the result)
Exit status 1 if there is at least one FAIL.
"""
import gzip, hashlib, json, os, re, subprocess, sys
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
PROJECT_DIR = "Claude Science Project Sep 29"
RESULTS = PROJECT_DIR + "/results/"
BASE = HERE / "baseline"
STATUS = {"CURRENT", "CURRENT_WITH_CAVEATS", "KNOWN_DEFECT", "SUPERSEDED", "WITHDRAWN", "PENDING_RULING", "UNCHECKED"}
# written in two parts so that this file does not match its own pattern
WS_PAT = re.compile("/" + "workspaces/" + "|" + "/" + r"\.claude-" + "science/")
VERSION_PAT = re.compile(r"(?i)[-_ .](v[0-9]+|final|rev[0-9]+)(?=$|[-_ .()])")
RESULTS_TOP_OK = {"INDEX.md", "README.md"}
TEXT_EXT = {".md", ".txt", ".csv", ".tsv", ".json", ".yaml", ".yml", ".py", ".rs", ".toml", ".sh", ".r", ".R", ".ipynb",
            ".html", ".tex", ".bib", ".cfg", ".ini", ".log", ".jl", ".m", ".js", ".ts", ""}
MAX_SCAN = 20_000_000


def git(*a, cwd=None, binary=False, check=True):
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.environ.get("GIT_CONFIG_GLOBAL", "/dev/null")}
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, env=env)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(a)}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout if binary else r.stdout.decode(errors="replace")


TOP = Path(git("rev-parse", "--show-toplevel", cwd=HERE).strip())


# ---------- views of a tree: working tree or one commit ----------
class WorkTree:
    name = "working tree"
    def paths(self):
        out = git("ls-files", "-z", "-c", "-o", "--exclude-standard", cwd=TOP)
        return sorted({p for p in out.split("\0") if p and (TOP / p).is_file()})
    def read(self, p):
        return (TOP / p).read_bytes()
    def size(self, p):
        return (TOP / p).stat().st_size


class CommitTree:
    """Tree of one commit. Reads blobs through one 'git cat-file --batch' process."""
    def __init__(self, sha):
        self.sha = sha; self.name = f"commit {sha[:12]}"; self._p = None; self._sizes = None
    def paths(self):
        out = git("ls-tree", "-r", "-z", "-l", self.sha, cwd=TOP)
        self._sizes = {}
        for rec in out.split("\0"):
            if not rec:
                continue
            meta, path = rec.split("\t", 1)
            parts = meta.split()
            if parts[1] == "blob":
                self._sizes[path] = int(parts[3]) if parts[3] != "-" else 0
        return sorted(self._sizes)
    def _proc(self):
        if self._p is None:
            env = {**os.environ, "GIT_CONFIG_GLOBAL": os.environ.get("GIT_CONFIG_GLOBAL", "/dev/null")}
            self._p = subprocess.Popen(["git", "cat-file", "--batch"], cwd=TOP, stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
        return self._p
    def read(self, p):
        q = self._proc()
        q.stdin.write(f"{self.sha}:{p}\n".encode()); q.stdin.flush()
        head = q.stdout.readline().split()
        if len(head) < 3 or head[1] == b"missing":
            raise FileNotFoundError(p)
        n = int(head[2]); data = q.stdout.read(n); q.stdout.read(1)
        return data
    def size(self, p):
        if self._sizes is None:
            self.paths()
        return self._sizes[p]


# ---------- baseline ----------
def load_baseline():
    f = BASE / "tracked_paths.txt.gz"
    if not f.exists():
        sys.exit(f"STOP: {f} is missing. Run --make-baseline at a registry build, or restore the file.")
    paths = set(gzip.open(f, "rt", encoding="utf-8").read().split("\n")) - {""}
    kv = BASE / "known_violations.json"
    known = set(json.load(open(kv))["keys"]) if kv.exists() else set()
    return paths, known


def dirs_of(paths):
    d = set()
    for p in paths:
        parts = p.split("/")
        for i in range(1, len(parts)):
            d.add("/".join(parts[:i]))
    return d


# ---------- small JSON Schema validator (subset used by manifest.schema.json) ----------
TYPES = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float), "boolean": bool, "null": type(None)}


def _type_ok(v, t):
    ts = t if isinstance(t, list) else [t]
    for x in ts:
        if x == "integer" and isinstance(v, bool):
            continue
        if isinstance(v, TYPES[x]):
            return True
    return False


def validate(v, s, root, where="$"):
    errs = []
    if "$ref" in s:
        ref = s["$ref"].lstrip("#/").split("/")
        node = root
        for k in ref:
            node = node[k]
        return validate(v, node, root, where)
    if "type" in s and not _type_ok(v, s["type"]):
        return [f"{where}: type must be {s['type']}"]
    if "const" in s and v != s["const"]:
        errs.append(f"{where}: must be {s['const']!r}")
    if "enum" in s and v not in s["enum"]:
        errs.append(f"{where}: must be one of {s['enum']}")
    if isinstance(v, str):
        if "pattern" in s and not re.search(s["pattern"], v):
            errs.append(f"{where}: does not match {s['pattern']}")
        if len(v) < s.get("minLength", 0) or len(v) > s.get("maxLength", 1 << 30):
            errs.append(f"{where}: length {len(v)} outside limits")
    if isinstance(v, (int, float)) and not isinstance(v, bool) and "minimum" in s and v < s["minimum"]:
        errs.append(f"{where}: below minimum {s['minimum']}")
    if isinstance(v, list):
        if len(v) < s.get("minItems", 0):
            errs.append(f"{where}: needs at least {s['minItems']} items")
        if "items" in s:
            for i, x in enumerate(v):
                errs += validate(x, s["items"], root, f"{where}[{i}]")
    if isinstance(v, dict):
        for k in s.get("required", []):
            if k not in v:
                errs.append(f"{where}: missing required field {k!r}")
        props = s.get("properties", {})
        for k, x in v.items():
            if k in props:
                errs += validate(x, props[k], root, f"{where}.{k}")
            elif s.get("additionalProperties") is False:
                errs.append(f"{where}: field {k!r} not permitted")
    if "not" in s and not validate(v, s["not"], root, where):
        errs.append(f"{where}: matches a forbidden form")
    if "oneOf" in s:
        n = sum(1 for x in s["oneOf"] if not validate(v, x, root, where))
        if n != 1:
            errs.append(f"{where}: must match exactly one permitted form (matches {n})")
    for sub in s.get("allOf", []):
        if "if" in sub:
            if not validate(v, sub["if"], root, where):
                errs += validate(v, sub.get("then", {}), root, where)
        else:
            errs += validate(v, sub, root, where)
    return errs


def schema_errors(obj):
    schema = json.load(open(HERE / "manifest.schema.json"))
    try:
        import jsonschema  # optional; same result expected
        v = jsonschema.Draft202012Validator(schema)
        return [f"$.{'.'.join(map(str, e.path))}: {e.message}" for e in v.iter_errors(obj)]
    except ImportError:
        return validate(obj, schema, schema)


# ---------- registries ----------
def registry_files(paths):
    return sorted(p for p in paths if p.startswith(PROJECT_DIR + "/") and p.endswith("/REGISTRY.json")
                  and "/Hydroacoustic Handover/" not in p)


def load_registries(view, paths):
    regs = {}
    for p in registry_files(paths):
        try:
            regs[p] = json.loads(view.read(p))
        except Exception as ex:
            regs[p] = {"_error": str(ex)}
    return regs


def registry_ids(regs):
    ids = {}
    for p, r in regs.items():
        for e in r.get("entries", []):
            ids.setdefault(e.get("id"), []).append(p)
    return ids


def check_registries(regs):
    """C4. Returns list of (key, message). The merged project registry repeats module ids; uniqueness is checked
    inside each registry file and across the module registries, not against the merged copy."""
    out = []
    merged = PROJECT_DIR + "/registry/REGISTRY.json"
    all_ids = set()
    for p, r in regs.items():
        if "_error" in r:
            out.append((f"C4:{p}:json", f"{p}: cannot read JSON: {r['_error']}")); continue
        seen = set()
        for e in r.get("entries", []):
            i = e.get("id")
            all_ids.add(i)
            if i in seen:
                out.append((f"C4:{p}:{i}:dup", f"{p}: id {i} occurs more than once"))
            seen.add(i)
            st = e.get("status")
            if st not in STATUS:
                out.append((f"C4:{p}:{i}:status", f"{p}: {i} has status {st!r}, not a permitted value"))
        for k, v in (r.get("roots") or {}).items():
            if isinstance(v, str) and WS_PAT.search(v):
                out.append((f"C4:{p}:root:{k}", f"{p}: root {k} points to a session workspace"))
    owner = {}
    for p, r in regs.items():
        if p == merged or "_error" in r:
            continue
        for e in r.get("entries", []):
            i = e.get("id")
            if i in owner and owner[i] != p:
                out.append((f"C4:{p}:{i}:dup-across", f"id {i} is in {owner[i]} and in {p}"))
            owner.setdefault(i, p)
    for p, r in regs.items():
        for e in r.get("entries", []) if "_error" not in r else []:
            t = e.get("superseded_by")
            for x in (t if isinstance(t, list) else [t] if t else []):
                if x not in all_ids:
                    out.append((f"C4:{p}:{e.get('id')}:superseded_by", f"{p}: {e.get('id')} superseded_by {x} which is not a registry id"))
    return out


# ---------- file checks ----------
def is_text(p, data):
    return PurePosixPath(p).suffix in TEXT_EXT and b"\0" not in data[:8192]


def scan_ws(p, data):
    out = []
    for n, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), 1):
        if WS_PAT.search(line):
            out.append((n, line.strip()[:140]))
    return out


MANIFEST_DIR = re.compile(r"^" + re.escape(PROJECT_DIR) + r"/registry/modules/[^/]+/manifests/")


def version_names(path, new_dirs):
    """C3 on the file name and on each NEW folder in the path. Registry manifest files are exempt: their names copy
    registry ids, which copy the names of old items."""
    if MANIFEST_DIR.match(path):
        return []
    bad = []
    parts = path.split("/")
    for i, comp in enumerate(parts):
        is_file = i == len(parts) - 1
        full = "/".join(parts[:i + 1])
        if not is_file and full not in new_dirs:
            continue
        stem = comp.rsplit(".", 1)[0] if is_file and "." in comp[1:] else comp
        if VERSION_PAT.search(stem):
            bad.append(full)
    return bad


def check_result_folder(view, run_dir, files_in_dir, modules, reg_ids):
    """C1 for one new run folder. Returns list of messages."""
    errs = []
    mpath = run_dir + "/manifest.json"
    if mpath not in files_in_dir:
        return [f"{run_dir}/: new result folder has no manifest.json"]
    try:
        m = json.loads(view.read(mpath))
    except Exception as ex:
        return [f"{mpath}: not valid JSON: {ex}"]
    errs += [f"{mpath}: {e}" for e in schema_errors(m)]
    module, run_id = run_dir.split("/")[-2], run_dir.split("/")[-1]
    if m.get("run_id") != run_id:
        errs.append(f"{mpath}: run_id {m.get('run_id')!r} differs from folder name {run_id!r}")
    if m.get("module") != module:
        errs.append(f"{mpath}: module {m.get('module')!r} differs from parent folder {module!r}")
    listed = set()
    for o in m.get("outputs", []) if isinstance(m.get("outputs"), list) else []:
        op = o.get("path", "") if isinstance(o, dict) else ""
        if re.match(r"^[A-Z]+:", op):
            continue  # large file in a registry root (exchange folder); checked by the registry build, not here
        fp = run_dir + "/" + op
        listed.add(fp)
        if fp not in files_in_dir:
            errs.append(f"{mpath}: output {op} is not in the folder"); continue
        data = view.read(fp)
        if len(data) != o.get("bytes"):
            errs.append(f"{mpath}: output {op} has {len(data)} bytes, manifest says {o.get('bytes')}")
        elif hashlib.sha256(data).hexdigest() != o.get("sha256"):
            errs.append(f"{mpath}: output {op} SHA-256 differs from the manifest")
    for f in sorted(files_in_dir):
        if f not in listed and f != mpath and PurePosixPath(f).name not in ("README.md",):
            errs.append(f"{f}: file is in the result folder but not in manifest outputs")
    for i in m.get("inputs", []) if isinstance(m.get("inputs"), list) else []:
        rid = i.get("registry_id") if isinstance(i, dict) else None
        if rid and rid not in reg_ids:
            errs.append(f"{mpath}: input {rid} is not a registry id")
    cfg = m.get("configuration")
    if isinstance(cfg, dict) and "file" in cfg:
        cp = run_dir + "/" + cfg["file"]
        if cp not in files_in_dir:
            errs.append(f"{mpath}: configuration file {cfg['file']} is not in the folder")
        elif hashlib.sha256(view.read(cp)).hexdigest() != cfg.get("sha256"):
            errs.append(f"{mpath}: configuration file SHA-256 differs")
    return errs


def load_modules():
    return set(json.load(open(HERE / "modules.json"))["modules"])


def run_checks(view, added_lines=None):
    base, known = load_baseline()
    modules = load_modules()
    paths = view.paths()
    pset = set(paths)
    new = [p for p in paths if p not in base]
    base_dirs = dirs_of(base)
    new_dirs = dirs_of(new) - base_dirs
    regs = load_registries(view, paths)
    reg_ids = set(registry_ids(regs))
    fails, warns, knowns = [], [], []
    # C1
    run_dirs = {}
    for p in new:
        if not p.startswith(RESULTS):
            continue
        rel = p[len(RESULTS):].split("/")
        if len(rel) == 1:
            if rel[0] not in RESULTS_TOP_OK:
                fails.append(f"C1 {p}: new loose file at the top of results/. Put it in results/<module>/<run id>/ with manifest.json")
            continue
        top = RESULTS + rel[0]
        if top in new_dirs or (rel[0] in modules and len(rel) >= 3 and RESULTS + "/".join(rel[:2]) in new_dirs):
            if rel[0] not in modules:
                fails.append(f"C1 {p}: new folder results/{rel[0]}/ is not a module name (see modules.json). Use results/<module>/<run id>/")
                continue
            if len(rel) == 2:
                fails.append(f"C1 {p}: new file directly in results/{rel[0]}/. Put it in a run folder results/{rel[0]}/<run id>/")
                continue
            run_dirs.setdefault(RESULTS + "/".join(rel[:2]), [])
        else:
            # file inside an old folder, or a new sub-folder inside an old folder
            folder = RESULTS + "/".join(rel[:2]) if rel[0] in modules and len(rel) >= 3 else top
            if folder + "/manifest.json" in pset:
                warns.append(f"C1 {p}: new file in old result folder {folder}/ that has a manifest; update its outputs list")
            else:
                warns.append(f"C1 {p}: new file in old result folder {folder}/ (no manifest). Old folders are closed; use results/<module>/<run id>/")
    for d in sorted(run_dirs):
        inside = [p for p in paths if p.startswith(d + "/")]
        for e in check_result_folder(view, d, set(inside), modules, reg_ids):
            fails.append("C1 " + e)
    # C2 and C3
    for p in new:
        if WS_PAT.search(p):
            fails.append(f"C2 {p}: path contains a session workspace path")
        for b in version_names(p, new_dirs):
            fails.append(f"C3 {b}: name uses a version suffix (-v2, -FINAL ...). Give a new run id and set supersedes/superseded_by")
        try:
            if view.size(p) > MAX_SCAN:
                continue
            data = view.read(p)
        except Exception:
            continue
        if is_text(p, data):
            for n, line in scan_ws(p, data):
                fails.append(f"C2 {p}:{n}: session workspace path in text: {line}")
    for p, lines in (added_lines or {}).items():
        if p in base:
            for n, line in lines:
                if WS_PAT.search(line):
                    fails.append(f"C2 {p}:{n}: added line has a session workspace path: {line.strip()[:140]}")
    # C4
    for key, msg in check_registries(regs):
        (knowns if key in known else fails).append(f"C4 {msg}")
    return {"view": view.name, "n_paths": len(paths), "n_new": len(new), "fails": sorted(set(fails)), "warns": sorted(set(warns)),
            "known": sorted(set(knowns))}


def print_result(r):
    print(f"check_project: {r['view']}: {r['n_paths']} paths, {r['n_new']} new since baseline")
    for x in r["warns"]:
        print("WARN ", x)
    for x in r["known"]:
        print("KNOWN", x)
    for x in r["fails"]:
        print("FAIL ", x)
    print(f"check_project: {len(r['fails'])} FAIL, {len(r['warns'])} WARN, {len(r['known'])} KNOWN (existing, in baseline)")


def added_lines_in_range(a, b):
    out = {}
    try:
        diff = git("diff", "-U0", "--no-color", "--diff-filter=M", f"{a}..{b}", cwd=TOP)
    except RuntimeError:
        return None
    cur, n = None, 0
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            cur = line[6:]
        elif line.startswith("@@"):
            m = re.search(r"\+(\d+)", line); n = int(m.group(1)) if m else 0
        elif line.startswith("+") and not line.startswith("+++") and cur:
            out.setdefault(cur, []).append((n, line[1:])); n += 1
    return out


def pre_push():
    zero = "0" * 40
    worst = 0
    for line in sys.stdin.read().splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        lref, lsha, rref, rsha = parts
        if lsha == zero:
            continue  # delete
        have_remote = rsha != zero and subprocess.run(["git", "cat-file", "-e", rsha], cwd=TOP).returncode == 0
        added = added_lines_in_range(rsha, lsha) if have_remote else None
        if added is None:
            print(f"check_project: no local copy of the remote head for {rref}; added lines in old files are not scanned (new files are)")
        r = run_checks(CommitTree(lsha), added)
        print_result(r)
        worst |= bool(r["fails"])
    if worst:
        print("check_project: push refused. Correct the FAIL items, or ask Pete for a ruling. Do not use --no-verify.")
    return 1 if worst else 0


# ---------- report and baseline ----------
def existing_violations(view):
    """All violations in a tree, as if every path were new (for the report). C1 lists result folders with no valid manifest."""
    paths = view.paths()
    pset = set(paths)
    modules = load_modules()
    rows = []
    folders = sorted({RESULTS + p[len(RESULTS):].split("/")[0] for p in paths if p.startswith(RESULTS) and "/" in p[len(RESULTS):]})
    for f in folders:
        if f + "/manifest.json" not in pset:
            rows.append(("C1", f + "/", "result folder has no manifest.json"))
    for p in paths:
        if p.startswith(RESULTS) and "/" not in p[len(RESULTS):] and PurePosixPath(p).name not in RESULTS_TOP_OK:
            rows.append(("C1", p, "loose file at the top of results/"))
    all_dirs = dirs_of(paths)
    for p in paths:
        for b in version_names(p, all_dirs):
            rows.append(("C3", b, "version suffix in name"))
        if WS_PAT.search(p):
            rows.append(("C2", p, "path contains a session workspace path"))
        try:
            if view.size(p) > MAX_SCAN:
                continue
            data = view.read(p)
        except Exception:
            continue
        if is_text(p, data):
            hits = scan_ws(p, data)
            if hits:
                rows.append(("C2", p, f"{len(hits)} lines with a session workspace path (first at line {hits[0][0]})"))
    regs = load_registries(view, paths)
    c4 = check_registries(regs)
    for key, msg in c4:
        rows.append(("C4", key, msg))
    return rows, [k for k, _ in c4], {"folders": len(folders)}


def main():
    a = sys.argv[1:]
    if a[:1] == ["--pre-push"]:
        sys.exit(pre_push())
    if a[:1] == ["--make-baseline"]:
        BASE.mkdir(exist_ok=True)
        head = git("rev-parse", "HEAD", cwd=TOP).strip()
        view = CommitTree(head)
        paths = view.paths()
        own = [str((BASE / n).relative_to(TOP)) for n in ("tracked_paths.txt.gz", "known_violations.json")]
        paths = sorted(set(paths) | set(own))
        with gzip.open(BASE / "tracked_paths.txt.gz", "wt", encoding="utf-8") as fh:
            fh.write("\n".join(paths) + "\n")
        rows, keys, _ = existing_violations(view)
        json.dump({"baseline_commit": head, "n_paths": len(paths), "keys": sorted(set(keys))}, open(BASE / "known_violations.json", "w"), indent=1)
        print(f"baseline written: {len(paths)} paths at {head[:12]}, {len(set(keys))} known registry violations")
        return
    if a[:1] == ["--report-existing"]:
        view = CommitTree(git("rev-parse", "HEAD", cwd=TOP).strip())
        rows, _, info = existing_violations(view)
        out = Path(a[1]) if len(a) > 1 else Path("existing_violations.tsv")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write("check\tpath_or_key\tfinding\n")
            for r in rows:
                fh.write("\t".join(r) + "\n")
        from collections import Counter
        print(f"existing violations in {view.name}: {dict(Counter(r[0] for r in rows))}; written to {out}")
        return
    view = CommitTree(a[a.index("--commit") + 1]) if "--commit" in a else WorkTree()
    r = run_checks(view)
    print_result(r)
    sys.exit(1 if r["fails"] else 0)


if __name__ == "__main__":
    main()
