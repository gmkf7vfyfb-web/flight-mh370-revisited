#!/usr/bin/env python3
"""Build the "ISO Sept 28 Status" recovery package for Pete's GitHub repository.

Mechanical parts only: code (anonymised git bundle of every branch, a browsable snapshot of main,
per-branch diffs, uncommitted work), results (small run outputs; large arrays listed with
checksums), input manifests (nothing restricted or bulky is copied), thread set-up material,
decision notes and the environment. The report (README.md) and STATUS.json are written by hand.
"""
import csv, hashlib, json, os, shutil, subprocess, sys, tarfile, tempfile
from pathlib import Path

REPO = Path("/jackbox/home/MH370")
WT = Path("/jackbox/home/MH370-worktrees")
INPUTS = Path("/jackbox/home/MH370-inputs")
PROMPTS = Path("/jackbox/home/.iso/thread-storage/thr_4pbhvf3sxi/prompts")
D1 = Path("/jackbox/home/.iso/thread-storage/thr_6wkhvpqx8k/d1-api-proposal.txt")
MAPS = Path("/jackbox/home/.iso/thread-storage/thr_4pbhvf3sxi/maps")
MEMORY = Path("/jackbox/home/.claude/projects/-jackbox-home-MH370/memory")
OUT = Path("/jackbox/home/MH370-export/ISO Sept 28 Status")
ANON_NAME, ANON_EMAIL = "MH370 iso agents", "mh370-iso@invalid"

# Results: what is copied. Everything else under runs/ is listed with size and sha256.
COPY_EXT = {".json", ".csv", ".png", ".toml", ".txt", ".tsv", ".svg", ".py"}
COPY_MAX = 5_000_000
PDF_MAX = 15_000_000
# Drafts of correspondence Pete has not approved, and plots of the Boeing simulator runs
# (restricted Boeing material; this repository's rule), are never published.
EXCLUDE_PARTS = {"cover.txt", "requests.txt", "outreach"}


def run(*cmd, cwd=None, check=True):
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True).stdout


def sha256(path, bufsize=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(bufsize):
            h.update(chunk)
    return h.hexdigest()


def code():
    dest = OUT / "code"
    dest.mkdir(parents=True)
    tmp = Path(tempfile.mkdtemp(prefix="mh370-anon-"))
    mirror = tmp / "mirror.git"
    run("git", "clone", "--quiet", "--mirror", str(REPO), str(mirror))
    mapfile = tmp / "map.txt"
    env_filter = (f'export GIT_AUTHOR_NAME="{ANON_NAME}" GIT_AUTHOR_EMAIL="{ANON_EMAIL}" '
                  f'GIT_COMMITTER_NAME="{ANON_NAME}" GIT_COMMITTER_EMAIL="{ANON_EMAIL}"')
    commit_filter = f'n=$(git commit-tree "$@"); echo "$GIT_COMMIT $n" >> {mapfile}; echo $n'
    subprocess.run(["git", "filter-branch", "-f", "--env-filter", env_filter, "--commit-filter", commit_filter,
                    "--", "--all"], cwd=mirror, check=True, capture_output=True,
                   env={**os.environ, "FILTER_BRANCH_SQUELCH_WARNING": "1"})
    for ref in run("git", "for-each-ref", "--format=%(refname)", "refs/original/", cwd=mirror).split():
        run("git", "update-ref", "-d", ref, cwd=mirror)
    heads = run("git", "for-each-ref", "--format=%(refname)", "refs/heads/", cwd=mirror).split()
    run("git", "bundle", "create", str(dest / "mh370.bundle"), "HEAD", *heads, cwd=mirror)
    run("git", "bundle", "verify", str(dest / "mh370.bundle"), cwd=mirror)
    # Proof that nothing personal survived: clone the bundle and list every identity in it.
    check_clone = tmp / "check"
    run("git", "clone", "--quiet", "--mirror", str(dest / "mh370.bundle"), str(check_clone))
    identities = set(run("git", "log", "--all", "--format=%an <%ae>|%cn <%ce>", cwd=check_clone).replace("|", "\n").split("\n")) - {""}
    assert identities == {f"{ANON_NAME} <{ANON_EMAIL}>"}, identities
    bodies = run("git", "log", "--all", "--format=%B", cwd=check_clone)
    assert "@gmail" not in bodies and "comcast" not in bodies

    pairs = [line.split() for line in mapfile.read_text().splitlines()]
    with open(dest / "commit-map.tsv", "w") as f:
        f.write("original_commit\tpublished_commit\n")
        for old, new in pairs:
            f.write(f"{old}\t{new}\n")
    newof = {old: new for old, new in pairs}

    # Branches: heads (original and published), relation to main, subject.
    rows = []
    for ref in run("git", "for-each-ref", "--format=%(refname:short)", "refs/heads/", cwd=REPO).split():
        orig = run("git", "rev-parse", ref, cwd=REPO).strip()
        ahead = run("git", "rev-list", "--count", f"main..{ref}", cwd=REPO).strip()
        behind = run("git", "rev-list", "--count", f"{ref}..main", cwd=REPO).strip()
        subject = run("git", "log", "-1", "--format=%s", ref, cwd=REPO).strip()
        date = run("git", "log", "-1", "--format=%cI", ref, cwd=REPO).strip()
        rows.append([ref, orig, newof.get(orig, ""), ahead, behind, date, subject])
    with open(dest / "branches.tsv", "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["branch", "original_head", "published_head", "commits_ahead_of_main", "commits_behind_main",
                    "last_commit_utc", "last_subject"])
        w.writerows(rows)

    # A browsable snapshot of main (plain files) and every other branch as a diff against main.
    main_dir = dest / "main"
    main_dir.mkdir()
    archive = subprocess.run(["git", "archive", "--format=tar", "refs/heads/main"], cwd=mirror, check=True,
                             capture_output=True).stdout
    tar_path = tmp / "main.tar"
    tar_path.write_bytes(archive)
    with tarfile.open(tar_path) as t:
        t.extractall(main_dir, filter="data")
    diffs = dest / "branch-diffs"
    diffs.mkdir()
    for ref in [r[0] for r in rows if r[0] != "main" and int(r[3]) > 0]:
        name = ref.replace("/", "__")
        (diffs / f"{name}.patch").write_text(run("git", "diff", "--binary", f"main...{ref}", cwd=mirror))
        (diffs / f"{name}.log.txt").write_text(run("git", "log", "--format=%H %cI %s", f"main..{ref}", cwd=mirror))

    # Work in progress that is on no branch: tracked changes and untracked files, per checkout.
    wip = dest / "uncommitted"
    wip.mkdir()
    checkouts = {"main-checkout": REPO} | {p.name: p for p in sorted(WT.iterdir()) if (p / ".git").exists()}
    wip_rows = []
    for name, path in checkouts.items():
        branch = run("git", "rev-parse", "--abbrev-ref", "HEAD", cwd=path).strip()
        head = run("git", "rev-parse", "HEAD", cwd=path).strip()
        patch = run("git", "diff", "--binary", "HEAD", cwd=path)
        untracked = [u for u in run("git", "ls-files", "--others", "--exclude-standard", cwd=path).splitlines() if u]
        kept, skipped = [], []
        for u in untracked:
            p = path / u
            if p.is_symlink() or not p.is_file():
                continue
            (kept if p.stat().st_size <= 20_000_000 else skipped).append(u)
        if patch:
            (wip / f"{name}.patch").write_text(patch)
        if kept:
            with tarfile.open(wip / f"{name}-untracked.tar.gz", "w:gz") as t:
                for u in kept:
                    t.add(path / u, arcname=u)
        wip_rows.append({"checkout": name, "path": str(path), "branch": branch, "head_original": head,
                         "head_published": newof.get(head, ""), "tracked_changes": bool(patch),
                         "untracked_files": kept, "untracked_skipped_over_20MB": skipped})
    (wip / "checkouts.json").write_text(json.dumps(wip_rows, indent=1))
    shutil.rmtree(tmp)


def results():
    dest = OUT / "results"
    copied, listed = [], []
    sources = [("core-main-checkout", REPO / "runs")] + [
        (f"worktree-{p.name}", p / "runs") for p in sorted(WT.iterdir()) if (p / "runs").is_dir()]
    for label, root in sources:
        for dirpath, dirnames, filenames in os.walk(root):
            d = Path(dirpath)
            # davey2016-next is the corrected base run still being written at export time. The
            # fixture (placeholder impacts, regenerated by `make fixture` in 20 s) is kept once.
            dirnames[:] = [x for x in dirnames if not (d / x).is_symlink() and x not in EXCLUDE_PARTS
                           and x != "davey2016-next"
                           and not (x == "fixture" and d == root and label != "worktree-core-stages")]
            for fn in filenames:
                p = d / fn
                if p.is_symlink() or fn in EXCLUDE_PARTS or fn == "handoff.toml":
                    continue
                rel = p.relative_to(root)
                size = p.stat().st_size
                ext = p.suffix.lower()
                ok = ((ext in COPY_EXT and size <= COPY_MAX) or (ext == ".pdf" and size <= PDF_MAX)) \
                    and not fn.lower().startswith("boeing")
                if ok:
                    target = dest / label / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, target)
                    copied.append([label, str(rel), size])
                else:
                    listed.append([label, str(rel), size, sha256(p)])
    with open(dest / "NOT_COPIED.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "path", "bytes", "sha256"])
        w.writerows(listed)
    arch = dest / "architecture-thread"
    arch.mkdir(parents=True, exist_ok=True)
    for p in MAPS.iterdir():
        shutil.copy2(p, arch / p.name)
    return copied, listed


# What each external input folder is, and why it is not copied here.
INPUT_NOTES = {
    "fuel": ("Ulich 9M-MRO fuel model v5.6 and BSM workbook", "RESTRICTED: tables carry Boeing-confidential notices; never redistribute"),
    "antenna": ("Large (2019) gain workbook; Ball AES gain-pattern spec", "Ball spec bundles licensed ARINC/Ball pages: not redistributable. Gain workbook is public on Hugging Face (peteabiome/mh370-dissertation-spreadsheets, CC BY 4.0)"),
    "satcom": ("Unredacted SITA log 35200217, 8 Mar 2014", "Your repository AGENTS.md: do not redistribute SITA material; a same-data copy already sits at your repository root"),
    "acars": ("ACARS position and wind reports (includes MH371 truth)", "Kept out: the MH371 known-flight control must stay blind; source not yet recorded"),
    "end-of-flight": ("Boeing end-of-flight simulator runs (via Iannello) and report text extracts", "RESTRICTED: Boeing material"),
    "search-coverage": ("GA/AusSeabed coverage samples; Ocean Infinity 2018 community outline", "OI outline: unclear licence, never published; GA layers are CC BY 4.0 and regenerable by the module's prepare script"),
    "ocean": ("GLORYS12/WAVERYS (CMEMS), OSCAR v2, BRAN2016, ERA5 10 m wind, GSHHG, GDP drifters", "Public but about 13 GB; regenerable from .sources/ocean-drift/ scripts"),
    "imos-acoustic": ("IMOS/Curtin Perth Canyon, Scott Reef and Portland recordings (MH370.zip)", "Public (AODN, CC BY 4.0), 540 MB: s3://imos-data/IMOS/ANMN/Acoustic/MH370.zip"),
    "papers": ("Papers and report text extracts", "Copyright varies: cite and fetch from the publishers"),
    "bathymetry": ("ETOPO 2022 1 arc-minute subset", "Public domain (NOAA); regenerable"),
    "drift": ("Drift maps built by `mh370 drift` (derived)", "Derived and about 107 MB; regenerable from code and ocean inputs"),
    "recovered-v01": ("Small files recovered from the 7 Sep v01 share snapshot", "Prior-work files, some of unclear licence (OI outlines); not republished"),
    "godfrey": ("Godfrey workbook v19.8", "Licence unrecorded"),
    "wspr": ("WSPR authors' results workbook", "Licence unrecorded"),
    "satellite": ("Inmarsat-3F1 position/velocity workbook", "Source of data/satellite-ephemeris.csv; licence unrecorded"),
    "radar": ("JORN FAQ", "Public web page"),
    "aero": ("Aerodynamic-model survey sources", "Copyright varies"),
    "hydroacoustics": ("Hydroacoustics sources", "Copyright varies"),
}


def inputs():
    dest = OUT / "data"
    dest.mkdir(parents=True)
    rows = []
    for dirpath, dirnames, filenames in os.walk(INPUTS):
        d = Path(dirpath)
        dirnames[:] = [x for x in dirnames if not (d / x).is_symlink()]
        for fn in sorted(filenames):
            p = d / fn
            if p.is_symlink():
                continue
            rel = p.relative_to(INPUTS)
            top = rel.parts[0] if len(rel.parts) > 1 else "(top level)"
            what, why = INPUT_NOTES.get(top, ("", ""))
            rows.append([str(rel), p.stat().st_size, sha256(p), top, what, why])
    with open(dest / "MH370-inputs-manifest.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["path_in_MH370-inputs", "bytes", "sha256", "folder", "what", "why_not_copied"])
        w.writerows(rows)
    shutil.copy2(INPUTS / "INDEX.txt", dest / "MH370-inputs-INDEX.txt")
    grids = []
    for p in sorted((REPO / "data").glob("*.bin")):
        grids.append([p.name, p.stat().st_size, sha256(p)])
    with open(dest / "data-grids-manifest.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file_in_repo_data", "bytes", "sha256"])
        w.writerows(grids)
    return len(rows), sum(r[1] for r in rows)


def threads_and_decisions():
    dest = OUT / "threads"
    (dest / "master-prompts").mkdir(parents=True)
    for p in sorted(PROMPTS.glob("*.txt")):
        shutil.copy2(p, dest / "master-prompts" / p.name)
    (dest / "design").mkdir()
    shutil.copy2(D1, dest / "design" / D1.name)
    listing = json.loads(run("iso", "thread", "list", "--project", "proj_pm8k5krhiy", "--json"))
    items = listing.get("threads", listing) if isinstance(listing, dict) else listing
    keep = {"thr_4pbhvf3sxi", "thr_mgewhqvb78", "thr_dkvnnfnn3b", "thr_6wkhvpqx8k", "thr_kaycpkjz9k",
            "thr_faie5jqc7p", "thr_ec96wswyz6", "thr_uduhvqttbk", "thr_gbqx8u9yfp", "thr_7e786pehut",
            "thr_vimeq9ezrd"}
    reg = [{"id": t.get("id"), "title": t.get("title"), "status_at_export": t.get("status"),
            "environment": t.get("environmentId")} for t in items if t.get("id") in keep]
    (dest / "iso-threads.json").write_text(json.dumps(reg, indent=1))
    dec = OUT / "decisions"
    dec.mkdir()
    for p in sorted(MEMORY.glob("*.md")):
        shutil.copy2(p, dec / p.name)


def environment():
    dest = OUT / "environment"
    dest.mkdir()
    lines = [
        "Environment of the iso host at export (29 Sep 2026)",
        f"OS: {run('uname', '-srm').strip()}; Arch Linux rolling (container; tools installed with pacman: git python base-devel unzip rsync jq)",
        f"Rust: {run('rustc', '--version').strip()}; {run('cargo', '--version').strip()}",
        f"Python: {run(str(REPO / '.venv/bin/python'), '--version').strip()} (shared venv at MH370/.venv; `make venv` rebuilds it)",
        "Hardware: 6 cores, 23 GB RAM; heavy jobs serialised with `flock /jackbox/home/.mh370-heavy.lock <cmd>`",
        "Make targets: " + " ".join(sorted(set(
            l.split(":")[0] for l in (REPO / "Makefile").read_text().splitlines()
            if l and l[0].isalpha() and ":" in l and not l.startswith(("export", "ifeq", "else", "endif"))))),
        "Worktrees: one per thread under MH370-worktrees/<name>; `.iso-env-setup.sh` links the ignored inputs.",
    ]
    (dest / "environment.txt").write_text("\n".join(lines) + "\n")
    (dest / "python-requirements-freeze.txt").write_text(run(str(REPO / ".venv/bin/pip"), "freeze"))


if __name__ == "__main__":
    if OUT.exists():
        sys.exit(f"{OUT} exists; remove it first")
    OUT.mkdir(parents=True)
    code()
    copied, listed = results()
    n_inputs, bytes_inputs = inputs()
    threads_and_decisions()
    environment()
    print(json.dumps({"results_copied": len(copied), "results_copied_MB": round(sum(c[2] for c in copied) / 1e6, 1),
                      "results_listed_only": len(listed), "results_listed_GB": round(sum(l[2] for l in listed) / 1e9, 2),
                      "inputs_listed": n_inputs, "inputs_GB": round(bytes_inputs / 1e9, 2)}, indent=1))
