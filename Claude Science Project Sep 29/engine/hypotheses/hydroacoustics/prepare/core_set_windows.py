"""Request windows for architecture's standard 00:19 option set, under the plain names (ruling ~16:30 UTC 10 Oct 2026).

Post-processing only. Reads a `windows_by_arm.csv` written by `search_windows.py` (or by the adopted stratum mixture)
and writes the core-set rows and their union, with plain names. No weights, quantiles or window rules are recomputed;
the per-arm rows are copied as they are.

CORE SET (architecture ruling, Pete): the names to use on every chart, table and note, in this order.
  1 00:19 Held Out                 none            x other
  2 00:19 R600 BTO Only            r600-bto        x other
  3 00:19 R600 BTO + Raw BFO       r600_no-offset  x other
  4 00:19 Holland H1               both_startup-offset x fuel-exhaustion
  5 00:19 Holland H2               both_no-offset  x other
Existence constraints: `+alive` is the core variant; `+silent` is reported beside it (see the open question to
architecture on whether the ruling's "did not answer at 01:15:56" means `+silent`).
UNION RULE: as in search_windows.py, over the core options with ESS >= 1,000. Options below that are labelled
"not yet estimable - targeted sampler in progress" (ruling item 5) and are not in the union.

Usage: python core_set_windows.py <windows_by_arm.csv> <out_dir>
"""
import csv, pathlib, sys, time

CORE = [("00:19 Held Out", "none__other"),
        ("00:19 R600 BTO Only", "r600-bto__other"),
        ("00:19 R600 BTO + Raw BFO", "r600_no-offset__other"),
        ("00:19 Holland H1", "both_startup-offset__fuel-exhaustion"),
        ("00:19 Holland H2", "both_no-offset__other")]
ESS_MIN = 1000
NOT_EST = "not yet estimable - targeted sampler in progress"


def hms(t):
    return time.strftime("%H:%M:%S", time.gmtime(float(t)))


def main(src, out):
    rows = list(csv.DictReader(open(src))); out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    arm2name = {a: n for n, a in CORE}
    core = []
    for r in rows:
        if r["arm"] in arm2name and r["variant"] in ("alive", "unpowered", "silent"):
            est = int(r["ess_pooled"]) >= ESS_MIN
            core.append(dict(option=arm2name[r["arm"]], option_no=[a for _, a in CORE].index(r["arm"]) + 1,
                             status="estimable" if est else NOT_EST, **r))
    core.sort(key=lambda r: (r["option_no"], r["variant"], r["receiver"], r["branch"]))
    with open(out / "core_windows_by_option.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(core[0])); w.writeheader(); w.writerows(core)
    rec = []
    for var in ("alive", "unpowered", "silent"):
        for nm in dict.fromkeys(r["receiver"] for r in core):
            for br in ("sofar", "agw"):
                sel = [r for r in core if r["variant"] == var and r["receiver"] == nm and r["branch"] == br and r["status"] == "estimable"]
                excl = sorted({r["option"] for r in core if r["variant"] == var and r["status"] != "estimable"})
                if sel:
                    rec.append(dict(variant=var, receiver=nm, branch=br, n_options=len(sel),
                                    window_start=hms(min(float(r["window_start_unix"]) for r in sel)),
                                    window_end=hms(max(float(r["window_end_unix"]) for r in sel)),
                                    any_unconverged=any(r["converged"] == "no" for r in sel),
                                    options=" ; ".join(r["option"] for r in sel), not_yet_estimable=" ; ".join(excl)))
    with open(out / "core_recommended_windows.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rec[0])); w.writeheader(); w.writerows(rec)
    print(len(core), len(rec))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
