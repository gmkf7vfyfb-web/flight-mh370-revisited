#!/usr/bin/env python3
"""Build "Archive ISO Pre Sept 28": the older MH370 iso threads and the old codebase copies.

GitHub gets: each thread's metadata, scrubbed conversation log, prompt history and final output;
a selection of its stored files (small reports, summaries, figures, scripts); the old codebases'
small files (source, configs, docs, small outputs), de-duplicated by content; and indexes with
SHA-256 for every file, saying where each one went. Google Drive gets the complete thread stores
(except the Astra thread's bulk particle outputs, which Pete asked to leave off) and the complete
old-codebase archives. Lists for the Drive upload are written outside the published folder.
"""
import csv, hashlib, json, os, re, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

X = Path("/jackbox/home/MH370-export")
OUT = X / "Archive ISO Pre Sept 28"
DRIVE_LISTS = X / "gdrive-archive"
STORE = Path("/jackbox/home/.iso/thread-storage")
CODEBASES = {
    "v01-share": Path("/jackbox/home/MH370-v01-share"),
    "v01-share-withdrawn": Path("/jackbox/home/MH370-v01-share-withdrawn-one-turn-20260907"),
    "release-v0.1": Path("/jackbox/home/MH370-withdrawn-one-turn-release-v0.1-20260907"),
}
# Archive files that already contain a whole codebase copy: Drive only. The zip duplicates the tar.zst.
CODEBASE_DRIVE_ONLY = {"MH370-v01-broad-reproducibility.tar.zst", "MH370-v01-broad-reports.zip", "MH370-v01-complete.tar.zst"}
CODEBASE_SKIP = {"MH370-v01-complete.zip"}

TEXT = {".json", ".csv", ".txt", ".toml", ".md", ".py", ".rs", ".tsv", ".svg", ".html", ".log", ".yaml",
        ".yml", ".js", ".mjs", ".sh", ".tex", ".m", ".jsonl", ".cfg", ".ini", ".sha256"}
SKIPDIRS = {"pylap-venv", "node_modules", "target", "vendor", "__pycache__", ".git", ".venv"}
BIG_STORES = {"thr_rzreetwcyu", "thr_rkyj8pbpxt"}      # selective on GitHub
ASTRA = "thr_rzreetwcyu"                                 # bulk outputs left off Drive (Pete)
CAP_BIG_STORE = 60_000_000
SUMMARY = re.compile(r"(readme|summary|status|manifest|report|review|results?|findings|index|overview)", re.I)

ALLOW_EMAILS = {"noreply@anthropic.com", "mh370-iso@invalid"}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SECRETS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"), re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bhf_[A-Za-z0-9]{25,}"), re.compile(r"AKIA[0-9A-Z]{16}"), re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)(bearer|authorization:)\s+[A-Za-z0-9._~+/=-]{16,}"),
    re.compile(r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token)\b[\"']?\s*[:=]\s*[\"']?[^\s\"',]{6,}"),
    re.compile(r"(?i)machine\s+\S+\s+login\s+\S+\s+password\s+\S+"),
    re.compile(r"\b4/0[A-Za-z0-9_-]{20,}"),
]
# Personal identifiers to replace (account names, user IDs), kept out of the published script.
PERSONAL_IDS = json.loads(Path("/jackbox/home/.mh370-secrets/personal-ids.json").read_text())
USERID = re.compile(r'("sender(User)?Id"\s*:\s*)"[^"]*"')


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while b := f.read(1 << 22):
            h.update(b)
    return h.hexdigest()


def scrub(text):
    n = 0
    for pat in SECRETS:
        text, k = pat.subn("<redacted>", text)
        n += k
    text = USERID.sub(r'\1"<id>"', text)
    for k, v in PERSONAL_IDS.items():
        text = text.replace(k, v)
    text = EMAIL.sub(lambda m: m.group(0) if m.group(0) in ALLOW_EMAILS else "<email>", text)
    return text, n


def has_secret(text):
    return any(p.search(text) for p in SECRETS)


def small(p, size):
    e = p.suffix.lower()
    return (e in TEXT and size <= 2_000_000) or (e == ".png" and size <= 1_000_000) or (e == ".pdf" and size <= 5_000_000)


def walk(root):
    for dp, dns, fns in os.walk(root):
        d = Path(dp)
        dns[:] = sorted(x for x in dns if x not in SKIPDIRS and not (d / x).is_symlink())
        for fn in sorted(fns):
            p = d / fn
            if not p.is_symlink() and p.is_file():
                yield p


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "untitled").lower()).strip("-")[:60]


def copy_text_scrubbed(src, dst):
    raw = src.read_text(errors="replace")
    if has_secret(raw):
        return "withheld: possible credential"
    text, _ = scrub(raw)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text)
    return "copied" + (" (emails redacted)" if text != raw else "")


def threads():
    listing = json.loads(run("iso", "thread", "list", "--project", "proj_pm8k5krhiy", "--json"))
    items = listing.get("threads", listing) if isinstance(listing, dict) else listing
    new = {"thr_4pbhvf3sxi", "thr_mgewhqvb78", "thr_dkvnnfnn3b", "thr_6wkhvpqx8k", "thr_kaycpkjz9k", "thr_faie5jqc7p",
           "thr_ec96wswyz6", "thr_uduhvqttbk", "thr_gbqx8u9yfp", "thr_7e786pehut", "thr_vimeq9ezrd"}
    old = [t for t in items if t.get("id") not in new]
    drive_rows, summary = [], []
    for t in old:
        tid = t["id"]
        ts = lambda v: datetime.fromtimestamp(v / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%MZ") if isinstance(v, (int, float)) else v
        d = OUT / "threads" / f"{tid}-{slug(t.get('title'))}"
        d.mkdir(parents=True)
        redactions = 0
        for name, cmd in [("log.txt", ["iso", "thread", "log", tid, "--format", "verbose"]),
                          ("history.json", ["iso", "thread", "history", tid, "--json"]),
                          ("final-output.txt", ["iso", "thread", "output", tid])]:
            text, n = scrub(run(*cmd))
            redactions += n
            (d / name).write_text(text)
        store = STORE / tid
        rows, gh_bytes = [], 0
        files = list(walk(store)) if store.is_dir() else []
        # Priority for selective stores: summaries first, then shallow files, smallest first.
        def prio(p):
            rel = p.relative_to(store)
            return (0 if SUMMARY.search(p.name) else 1, len(rel.parts), p.stat().st_size)
        for p in sorted(files, key=prio):
            rel = p.relative_to(store)
            size = p.stat().st_size
            is_small = small(p, size)
            to_gh = is_small
            if tid in BIG_STORES and to_gh:
                shallow = len(rel.parts) <= 2 or SUMMARY.search(p.name)
                to_gh = bool(shallow) and gh_bytes + size <= CAP_BIG_STORE
            if any(part.startswith("pharlap-") for part in rel.parts):
                to_gh = False  # licensed toolbox copy: private Drive only
            status = "not on GitHub"
            if to_gh:
                target = d / "storage" / rel
                if p.suffix.lower() in TEXT:
                    status = copy_text_scrubbed(p, target)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, target)
                    status = "copied"
                if status.startswith("copied"):
                    gh_bytes += size
            to_drive = not (tid == ASTRA and not is_small)
            rows.append([str(rel), size, sha256(p), status, "yes" if to_drive else "no (bulk Astra output, left off)"])
            if to_drive:
                drive_rows.append(f"{tid}/{rel.as_posix()}")
        with open(d / "storage-index.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["path_in_thread_storage", "bytes", "sha256", "github", "google_drive"])
            w.writerows(rows)
        meta = {"id": tid, "title": t.get("title"), "project": t.get("projectId"), "status_at_export": t.get("status"),
                "created_utc": ts(t.get("createdAt")), "updated_utc": ts(t.get("updatedAt")),
                "environment": t.get("environmentId"), "storage_files": len(rows),
                "storage_bytes": sum(r[1] for r in rows), "storage_files_on_github": sum(r[3].startswith("copied") for r in rows),
                "log_redactions": redactions}
        (d / "meta.json").write_text(json.dumps(meta, indent=1))
        summary.append(meta)
    DRIVE_LISTS.mkdir(exist_ok=True)
    (DRIVE_LISTS / "thread-storage.txt").write_text("\n".join(drive_rows) + "\n")
    return summary


def codebases():
    index, seen, drive = [], {}, []
    for label, root in CODEBASES.items():
        for p in walk(root):
            rel = p.relative_to(root)
            size = p.stat().st_size
            if p.name in CODEBASE_SKIP:
                index.append([label, str(rel), size, "", "skipped (same content as the .tar.zst)", "no"])
                continue
            digest = sha256(p)
            drive_it = p.name in CODEBASE_DRIVE_ONLY or label == "release-v0.1"
            if drive_it:
                drive.append(f"{label}\t{rel.as_posix()}")
            status = "not on GitHub (Drive archive holds it)"
            if p.name not in CODEBASE_DRIVE_ONLY and small(p, size):
                if digest in seen:
                    status = f"duplicate of {seen[digest]}"
                else:
                    target = OUT / "codebases" / label / rel
                    if p.suffix.lower() in TEXT:
                        status = copy_text_scrubbed(p, target)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(p, target)
                        status = "copied"
                    if status.startswith("copied"):
                        seen[digest] = f"{label}/{rel.as_posix()}"
            index.append([label, str(rel), size, digest, status, "yes" if drive_it else "via archive"])
    with open(OUT / "codebases" / "INDEX.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["copy", "path", "bytes", "sha256", "github", "google_drive"])
        w.writerows(index)
    (DRIVE_LISTS / "codebases.tsv").write_text("\n".join(drive) + "\n")
    return len(index), sum(1 for r in index if r[4].startswith("copied"))


if __name__ == "__main__":
    if OUT.exists():
        sys.exit(f"{OUT} exists; remove it first")
    OUT.mkdir(parents=True)
    s = threads()
    n_idx, n_copied = codebases()
    (OUT / "threads" / "THREADS.json").write_text(json.dumps(s, indent=1))
    print(json.dumps({"threads": len(s), "thread_files_on_github": sum(m["storage_files_on_github"] for m in s),
                      "log_redactions": sum(m["log_redactions"] for m in s),
                      "codebase_files_indexed": n_idx, "codebase_files_on_github": n_copied}, indent=1))
