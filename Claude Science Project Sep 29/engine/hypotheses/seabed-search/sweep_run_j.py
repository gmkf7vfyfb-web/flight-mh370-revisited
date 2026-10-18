"""Score every run J seed with score_run_j.py and publish the exchange set, with a disk guard.

    python hypotheses/seabed-search/sweep_run_j.py --src <eof run-j dir> --out <exchange searched-areas/run-j>
        --summaries <dir> [--workers 4] [--threads 2] [--floor-gib 15] [--binary <mh370>]

Order of writing: per seed (columns, then the seed's SHA256SUMS); per family when all its seeds are done (family SHA256SUMS
merged from the seeds, README.md, then READY); top level last (SHA256SUMS, README.md, then READY). A family with any failed
seed gets no READY, and then there is no top-level READY. The disk guard stops new seeds (running ones finish) when free space
would fall below --floor-gib, and writes STOPPED instead of READY.
"""
import argparse
import concurrent.futures as cf
import json
import pathlib
import shutil
import subprocess
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
FAMILIES = ["run-j-waypoints", "run-j-free", "run-j-descent-climb", "run-j-repro-radar"]
BYTES_PER_ROW = 8 + 3 * 4 + 4 + 4 + 1          # lnL f64, three rho f32, without-OI f32, searched fraction f32, next-area u8
TEMP_BYTES_PER_ROW = 21 * 8 + 9 * 8            # rebuilt float64 eval input + evaluate.npy, deleted per seed
GIB = 1024 ** 3


def free_bytes(p):
    return shutil.disk_usage(p).free


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--summaries", type=pathlib.Path, required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--threads", default="2")
    ap.add_argument("--floor-gib", type=float, default=15.0)
    ap.add_argument("--binary", type=pathlib.Path)
    ap.add_argument("--scratch", type=pathlib.Path)
    ap.add_argument("--readme", type=pathlib.Path, help="top-level README text to publish")
    a = ap.parse_args()
    t0 = time.time()
    tasks = []
    for fam in FAMILIES:
        if not (a.src / fam / "READY").is_file():
            sys.exit(f"{a.src / fam}: no READY from end of flight")
        seeds = sorted((d.name for d in (a.src / fam).glob("seed-*") if d.is_dir()), key=lambda s: int(s.split("-")[1]))
        for s in seeds:
            n = int(np.load(a.src / fam / s / "impacts32.npy", mmap_mode="r").shape[0])
            tasks.append((fam, s, n))
    total_rows = sum(t[2] for t in tasks)
    print(f"{len(tasks)} seeds, {total_rows:,} rows, publish {total_rows * BYTES_PER_ROW / GIB:.2f} GiB, "
          f"free {free_bytes(a.out.parent) / GIB:.1f} GiB", flush=True)
    a.out.mkdir(parents=True, exist_ok=True)
    for f in ("READY", "STOPPED"):
        (a.out / f).unlink(missing_ok=True)

    done, failed, stopped = {}, {}, False
    min_free = free_bytes(a.out.parent)

    def run(task):
        fam, s, n = task
        cmd = [sys.executable, str(HERE / "score_run_j.py"), str(a.src / fam), s, "--out", str(a.out / fam / s),
               "--summary", str(a.summaries / f"{fam}_{s}.json"), "--threads", a.threads]
        if a.binary:
            cmd += ["--binary", str(a.binary)]
        if a.scratch:
            cmd += ["--scratch", str(a.scratch)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return task, r.returncode, (r.stdout.strip().splitlines() or [""])[-1], r.stderr[-2000:]

    pending = list(tasks)
    running = {}
    with cf.ThreadPoolExecutor(a.workers) as ex:
        while pending or running:
            while pending and len(running) < a.workers and not stopped:
                rem = sum(t[2] for t in pending)
                need = rem * BYTES_PER_ROW + (len(running) + 1) * max(t[2] for t in pending) * TEMP_BYTES_PER_ROW
                fb = free_bytes(a.out.parent)
                min_free = min(min_free, fb)
                if fb - need < a.floor_gib * GIB:
                    stopped = True
                    print(f"DISK GUARD: free {fb / GIB:.1f} GiB, need {need / GIB:.1f} GiB, floor {a.floor_gib} GiB - stopping",
                          flush=True)
                    break
                t = pending.pop(0)
                running[ex.submit(run, t)] = t
            if stopped and not running:
                break
            if not running:
                break
            fin, _ = cf.wait(list(running), timeout=30, return_when=cf.FIRST_COMPLETED)
            min_free = min(min_free, free_bytes(a.out.parent))
            for fu in fin:
                t = running.pop(fu)
                task, rc, last, err = fu.result()
                (done if rc == 0 else failed)[(task[0], task[1])] = last if rc == 0 else err
                print(f"[{time.time() - t0:7.0f}s] {task[0]}/{task[1]} rc={rc} {last if rc == 0 else err[-300:]}", flush=True)
            if stopped:
                pending = [] if not running else pending
    # ---- per family
    ok_fams = []
    for fam in FAMILIES:
        seeds = [t for t in tasks if t[0] == fam]
        if any((fam, s) not in done for _, s, _ in seeds):
            print(f"{fam}: incomplete ({sum((fam, s) in done for _, s, _ in seeds)}/{len(seeds)}) - no READY", flush=True)
            continue
        lines = []
        for _, s, _ in seeds:
            for line in (a.out / fam / s / "SHA256SUMS").read_text().splitlines():
                h, _, fn = line.partition("  ")
                lines.append(f"{h}  {s}/{fn}")
        (a.out / fam / "SHA256SUMS").write_text("\n".join(lines) + "\n")
        rows = sum(n for _, _, n in seeds)
        (a.out / fam / "README.md").write_text(
            f"# Searched areas on end of flight run J, {fam}\n\n{len(seeds)} seeds, {rows:,} rows, each seed row-aligned with "
            f"`end-of-flight/run-j/{fam}/seed-N/impacts32.npy`. Columns and labels: see ../README.md.\n")
        (a.out / fam / "READY").write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + f" {len(seeds)} seeds {rows} rows\n")
        ok_fams.append(fam)
    # ---- top level, last
    if len(ok_fams) == len(FAMILIES) and not failed:
        lines = []
        for fam in FAMILIES:
            for line in (a.out / fam / "SHA256SUMS").read_text().splitlines():
                h, _, fn = line.partition("  ")
                lines.append(f"{h}  {fam}/{fn}")
        (a.out / "SHA256SUMS").write_text("\n".join(lines) + "\n")
        if a.readme:
            shutil.copy(a.readme, a.out / "README.md")
        (a.out / "READY").write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + f" {len(tasks)} seeds {total_rows} rows\n")
    else:
        (a.out / "STOPPED").write_text(json.dumps({"failed": {f"{k[0]}/{k[1]}": v for k, v in failed.items()},
                                                   "stopped_by_disk_guard": stopped, "done": len(done)}, indent=1))
    print(json.dumps({"seeds_done": len(done), "seeds_failed": len(failed), "disk_guard_stopped": stopped,
                      "rows_total": total_rows, "min_free_gib": round(min_free / GIB, 2), "wall_s": round(time.time() - t0)}),
          flush=True)


if __name__ == "__main__":
    main()
