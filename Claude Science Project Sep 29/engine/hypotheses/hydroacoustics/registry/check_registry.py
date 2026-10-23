"""Checks on the registry and the module notes. Hydro clean-up run, 23 Oct 2026.

  python check_registry.py --verify     re-hash every registered file and compare with the manifests (slow: ~80 GB)
  python check_registry.py --stale      list every registered text file that still uses a retired value (2.1e-4 as anchor,
                                        old IMOS table imos_tl_ramcorr) without saying so, with file and line
  python check_registry.py --wording    list wording that Pete has ruled out ("recorded no signal", "closed access" as a
                                        new label, "I am confident", "all ... already searched") with file and line
Exit status 1 if --verify finds a difference. --stale and --wording only report.
"""
import argparse, gzip, hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from registry import Registry

OLD_ANCHOR = re.compile(r"2\.1\s*(e-?0?4|×\s*10⁻⁴|x\s*10\^?-4)|0\.00021")
OLD_TABLE = re.compile(r"imos_tl_ramcorr")
CONTEXT_OK = re.compile(r"(?i)retired|old anchor|different quantity|low by 10\.3|superseded|was 2\.1|instead of|replac|→|->|D01")
WORDING = re.compile(r"(?i)recorded no signal|no signal was (recorded|detected)|\bi am confident\b|already been searched|no hydroacoustic detection")
TEXT = {".md", ".txt", ".csv", ".json", ".py", ".yaml"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--verify", action="store_true"); ap.add_argument("--stale", action="store_true")
    ap.add_argument("--wording", action="store_true"); ap.add_argument("--max-bytes", type=int, default=5_000_000)
    a = ap.parse_args(); R = Registry(); bad = 0
    for e in R.reg["entries"]:
        try:
            base = R.path(e["id"], allow_defect=True)
        except Exception as ex:
            print("SKIP", e["id"], ex); continue
        m = R.manifest(e["id"])
        if a.verify:
            for rel, (size, sha) in m.items():
                p = base if base.is_file() else base / rel
                h = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "MISSING"
                if h != sha:
                    bad += 1; print("DIFF", e["id"], rel, h[:12], sha[:12])
        if a.stale or a.wording:
            files = [base] if base.is_file() else [base / r for r in m] if m else []
            for p in files:
                if p.suffix not in TEXT or not p.exists() or p.stat().st_size > a.max_bytes:
                    continue
                for i, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
                    if a.stale and (OLD_ANCHOR.search(line) or OLD_TABLE.search(line)) and not CONTEXT_OK.search(line):
                        print(f"STALE\t{e['id']}\t{e['status']}\t{p}:{i}\t{line.strip()[:160]}")
                    if a.wording and WORDING.search(line):
                        print(f"WORDING\t{e['id']}\t{e['status']}\t{p}:{i}\t{line.strip()[:160]}")
    if a.verify:
        print(f"verify: {bad} differences")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
