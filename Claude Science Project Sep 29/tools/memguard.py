#!/usr/bin/env python3
"""memguard.py - memory-aware job launcher for heavy local runs on the Mac.

Why: the sandbox cannot see host processes (ps/pgrep/sysctl are blocked), so a
session that starts N background jobs cannot tell how much memory they take.
Eight parallel jobs of 7 GB each took the 64 GB machine down on 3-4 Nov and
again on 8-9 Nov 2026.  This tool measures one job first, then runs as many
in parallel as the free memory allows and no more, and stops launching (or
kills its children) if the machine runs short.

Usage
  python memguard.py status
      Print available memory, kernel free percentage and the launch budget.

  python memguard.py measure -- CMD ARGS...
      Run one command in the foreground; print its peak RSS (GB) and wall time.

  python memguard.py run [--max N] [--headroom GB] [--min-free GB]
                         [--log DIR] [--peak GB] --args A B C ... -- CMD ... {} ...
      Run CMD once per argument, substituting {} with the argument.
      Job 1 runs alone and is measured (unless --peak is given).
      Concurrency = min(--max, CPU count, floor((available - headroom) / peak)).
      A watchdog samples memory every 2 s: below --min-free available it stops
      launching new jobs; below the critical level it terminates all children.
      Logs go to DIR/<arg>.log (default: memguard-logs/).

Only the standard library is used.  All figures are from vm_stat and
memory_pressure, which work inside the sandbox.
"""
import argparse, os, re, resource, shlex, signal, subprocess, sys, time

PAGE = 16384

def vm_stat():
    out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
    m = re.search(r"page size of (\d+)", out); page = int(m.group(1)) if m else PAGE
    d = {}
    for line in out.splitlines():
        mm = re.match(r"\s*(.+?):\s+(\d+)\.?\s*$", line)
        if mm: d[mm.group(1).strip()] = int(mm.group(2)) * page / 2**30
    return d

def mem_status():
    d = vm_stat()
    free = d.get("Pages free", 0) + d.get("Pages speculative", 0)
    inactive = d.get("Pages inactive", 0); purgeable = d.get("Pages purgeable", 0)
    total = sum(d.get(k, 0) for k in ("Pages free", "Pages active", "Pages inactive",
              "Pages speculative", "Pages wired down", "Pages occupied by compressor"))
    try:
        total = max(total, os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE") / 2**30)
    except (ValueError, OSError, AttributeError):
        pass
    available = free + inactive + purgeable            # what new processes can take without compressing
    pct = None
    try:
        mp = subprocess.run(["memory_pressure"], capture_output=True, text=True, timeout=10).stdout
        mm = re.search(r"free percentage:\s*(\d+)%", mp); pct = int(mm.group(1)) if mm else None
    except Exception:
        pass
    return dict(total_gb=total, available_gb=available, free_gb=free,
                compressor_gb=d.get("Pages occupied by compressor", 0), kernel_free_pct=pct)

def fmt_status(s):
    return (f"total {s['total_gb']:.1f} GB, available {s['available_gb']:.1f} GB "
            f"(free {s['free_gb']:.1f}, compressor {s['compressor_gb']:.1f}), kernel free {s['kernel_free_pct']}%")

def cmd_status(a):
    s = mem_status(); print(fmt_status(s))
    budget = max(0.0, s["available_gb"] - a.headroom)
    print(f"launch budget with {a.headroom:.0f} GB headroom: {budget:.1f} GB")
    return 0

def measure_one(cmd, log=None):
    before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    t0 = time.time()
    with (open(log, "w") if log else open(os.devnull, "w")) as fh:
        rc = subprocess.run(cmd, stdout=fh if log else None, stderr=subprocess.STDOUT if log else None).returncode
    peak = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 2**30   # macOS: bytes
    return rc, max(peak, before / 2**30), time.time() - t0

def cmd_measure(a):
    if not a.cmd: sys.exit("measure: give the command after --")
    rc, peak, wall = measure_one(a.cmd)
    print(f"[memguard] exit {rc}, peak RSS {peak:.2f} GB, wall {wall:.0f} s")
    return rc

def cmd_run(a):
    if not a.cmd or not a.args: sys.exit("run: need --args A B ... and a command after --")
    os.makedirs(a.log, exist_ok=True)
    sub = lambda arg: [c.replace("{}", str(arg)) for c in a.cmd]
    logf = lambda arg: os.path.join(a.log, f"{arg}.log")
    s = mem_status(); print(f"[memguard] start: {fmt_status(s)}", flush=True)
    queue = list(a.args); results = {}
    peak = a.peak
    if peak is None:
        first = queue.pop(0)
        print(f"[memguard] measuring job {first} alone ...", flush=True)
        rc, peak, wall = measure_one(sub(first), logf(first)); results[first] = rc
        print(f"[memguard] job {first}: exit {rc}, peak RSS {peak:.2f} GB, wall {wall:.0f} s", flush=True)
        if rc != 0: print("[memguard] first job failed; not launching the rest", flush=True); return rc
    s = mem_status()
    n_mem = int(max(0.0, s["available_gb"] - a.headroom) // max(peak, 0.1))
    conc = max(1, min(a.max or 10**6, os.cpu_count() or 1, n_mem))
    print(f"[memguard] peak {peak:.2f} GB per job, available {s['available_gb']:.1f} GB, "
          f"headroom {a.headroom:.0f} GB -> running {conc} job(s) at a time ({len(queue)} remaining)", flush=True)
    running = {}
    def kill_all(why):
        print(f"[memguard] CRITICAL: {why}; terminating {len(running)} job(s)", flush=True)
        for p in running.values(): p.send_signal(signal.SIGTERM)
        time.sleep(3)
        for p in running.values():
            if p.poll() is None: p.kill()
    try:
        while queue or running:
            for arg, p in list(running.items()):
                if p.poll() is not None:
                    results[arg] = p.returncode; running.pop(arg); p.stdout.close()
                    print(f"[memguard] job {arg} finished, exit {p.returncode}", flush=True)
            s = mem_status()
            if s["kernel_free_pct"] is not None and s["kernel_free_pct"] < a.critical_pct:
                kill_all(f"kernel free {s['kernel_free_pct']}% < {a.critical_pct}%"); return 3
            can_launch = (len(running) < conc and queue
                          and s["available_gb"] - a.headroom >= peak * (1 if running else 0.5)
                          and s["available_gb"] >= a.min_free)
            if can_launch:
                arg = queue.pop(0); fh = open(logf(arg), "w")
                p = subprocess.Popen(sub(arg), stdout=fh, stderr=subprocess.STDOUT); p.stdout = fh
                running[arg] = p
                print(f"[memguard] launched job {arg} (pid {p.pid}); running {len(running)}, "
                      f"available {s['available_gb']:.1f} GB", flush=True)
                time.sleep(a.ramp)          # let it allocate before judging the next launch
                continue
            time.sleep(2)
    except KeyboardInterrupt:
        kill_all("interrupted"); return 130
    bad = {k: v for k, v in results.items() if v != 0}
    print(f"[memguard] done: {len(results)} jobs, {len(bad)} failed {bad if bad else ''}", flush=True)
    return 1 if bad else 0

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="mode", required=True)
    p0 = sp.add_parser("status"); p0.add_argument("--headroom", type=float, default=10.0)
    p1 = sp.add_parser("measure"); p1.add_argument("cmd", nargs=argparse.REMAINDER)
    p2 = sp.add_parser("run")
    p2.add_argument("--args", nargs="+", required=True, help="one job per argument; {} in CMD is replaced")
    p2.add_argument("--max", type=int, default=None, help="upper bound on parallel jobs (default: CPU count)")
    p2.add_argument("--headroom", type=float, default=10.0, help="GB kept free for the OS, Word, browsers, kernels")
    p2.add_argument("--min-free", type=float, default=6.0, help="GB available below which nothing new is launched")
    p2.add_argument("--critical-pct", type=int, default=8, help="kernel free %% below which children are terminated")
    p2.add_argument("--peak", type=float, default=None, help="known peak GB per job; skips the measuring run")
    p2.add_argument("--ramp", type=float, default=15.0, help="seconds to wait after each launch before the next")
    p2.add_argument("--log", default="memguard-logs")
    p2.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    if hasattr(a, "cmd") and a.cmd and a.cmd[0] == "--": a.cmd = a.cmd[1:]
    sys.exit({"status": cmd_status, "measure": cmd_measure, "run": cmd_run}[a.mode](a))

if __name__ == "__main__":
    main()
