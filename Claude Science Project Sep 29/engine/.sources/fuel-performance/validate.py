#!/usr/bin/env python3
"""Check a fuel-flow model against Boeing's published 9M-MRO performance analysis (SIR App. 1.6E).

Usage: .venv/bin/python .sources/fuel-performance/validate.py [TABLES] [SIR_TEXT]
  TABLES    default data/fuel-tables.json (from extract.py)
  SIR_TEXT  default /jackbox/home/MH370-inputs/end-of-flight/report-text/boeing_performance_appendix_1_6E.txt

Targets are parsed from the SIR text, not typed in:
  Table 3: five constant segments from the last ACARS report (17:06:43, 96,562.5 lb fuel, gross
           weight 480,600 lb) to arc 1, with Boeing's fuel at the end of each.
  Table 4: time to fuel exhaustion from arc 1 for 22 flight-level/speed pairs.
Nothing here uses arc 1 or later SATCOM events, so the check is not circular with them.

The reference model: per-engine fuel flow at (flight level, weight, Mach) from the FPPM grids,
bilinear in flight level and weight. Between neighbouring speed schedules (holding with the 5 %
racetrack allowance removed, MRC, CI 52, LRC, M0.84) FF(M) = a M^2 + b / M^2, the drag-polar
shape, exact at both; beyond them the nearest pair is extrapolated. ISA day: Boeing's Table 3
TAS match ISA to 1 kt, so Table 4's Mach is taken from each row's TAS at ISA (it prints M0.824
for both 475 and 466 kt at FL350; 466 kt is M0.809).

Cell classes used (see extract.py): fppm-open, fppm-confidential and fppm-optimum (Boeing data),
and derived (the MRC and CI 52 grids, Ulich's reconstruction). Filler cells are never used; a
query that needs one is treated as outside the table.

Each Boeing number (a Table 3 segment's burn, started from Boeing's fuel at its start, or a
Table 4 endurance) gives the fuel-flow factor that would make the model match it. The factors
from numbers inside the tabulated schedules give the model's calibration and its spread; those
needing extrapolation in Mach (above M0.84, or below the slowest schedule) show the extra error
there. FL030 has no table coverage.
"""

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "data/fuel-tables.json"
SIR = Path("/jackbox/home/MH370-inputs/end-of-flight/report-text/boeing_performance_appendix_1_6E.txt")
LB = 0.45359237
SCHEDULES = [("holding_mach", "holding_ff", 1 / 1.05), ("mrc_mach", "mrc_ff", 1.0), ("ci52_mach", "ci52_ff", 1.0),
             ("lrc_mach", "lrc_ff", 1.0), (None, "m084_ff", 1.0)]
TOLERANCE_SD = 0.03  # s.d. of the implied fuel-flow factor across the in-range evidence


def parse_sir(text):
    fuel_lb = float(re.search(r"last ACARS transmission, the\s+amount of fuel onboard was recorded at [\d,]+ kg \(([\d,.]+) lb\)",
                              text).group(1).replace(",", ""))
    gross_lb = float(re.search(r"gross weight at ([\d,]+) lb", text).group(1).replace(",", ""))
    t3 = re.search(r"Table 3: Flight Segment Details(.*?)Performance Range Capability", text, re.S).group(1)
    seg = [dict(hours=float(m[0]), nm=float(m[1]), fl=float(m[2]), wind=float(m[3]), tas=float(m[4]), mach=float(m[5]),
                end_lb=float(m[6].replace(",", "")))
           for m in re.findall(r"^\s*\d\s+([\d.]+)\s+([\d.]+)\s+FL(\d+)\s+([-+]?\d+)\s+(\d+)\s+([\d.]+)\s+([\d,]+)\s*$", t3, re.M)]
    t4 = re.search(r"Table 4: Range Capability(.*?)Using the time constraints", text, re.S).group(1)
    end = [dict(fl=float(m[0]), tas=float(m[1]), mach=float(m[2]), mrc=bool(m[3]), hours=float(m[4]), nm=float(m[5]))
           for m in re.findall(r"^\s*FL(\d+)\s+(\d+)\s+([\d.]+)(\*?)\s+([\d.]+)\s+(\d+)\s*$", t4, re.M)]
    arc1_lb = float(re.search(r"calculated fuel on board WB175 was ([\d,]+) lb", text).group(1).replace(",", ""))
    assert len(seg) == 5 and len(end) == 22, (len(seg), len(end))
    return fuel_lb * LB, (gross_lb - fuel_lb) * LB, seg, end, arc1_lb * LB


def bilinear(tab, fl, w):
    """Per-cell value at (fl, w), or None outside the grid or next to a filler/missing cell."""
    fls, ws, v, cls = tab["flight_levels"], tab["weights_t"], tab["values"], tab["source_class"]
    if not (fls[0] <= fl <= fls[-1] and ws[0] <= w <= ws[-1]):
        return None
    j = max(k for k in range(len(fls) - 1) if fls[k] <= fl) if fl < fls[-1] else len(fls) - 2
    i = max(k for k in range(len(ws) - 1) if ws[k] <= w) if w < ws[-1] else len(ws) - 2
    corners = [(i, j), (i + 1, j), (i, j + 1), (i + 1, j + 1)]
    if any(v[a][b] is None or cls[a][b] == "filler" for a, b in corners):
        return None
    x = (fl - fls[j]) / (fls[j + 1] - fls[j])
    y = (w - ws[i]) / (ws[i + 1] - ws[i])
    return (v[i][j] * (1 - x) * (1 - y) + v[i + 1][j] * (1 - x) * y + v[i][j + 1] * x * (1 - y) + v[i + 1][j + 1] * x * y)


def fuel_flow(tables, fl, w_t, mach):
    """Total fuel flow (kg/h, both engines) and a flag when the Mach is outside the tabulated schedules."""
    pts = []
    for mkey, fkey, scale in SCHEDULES:
        f = bilinear(tables[fkey], fl, w_t)
        m = 0.84 if mkey is None else bilinear(tables[mkey], fl, w_t)
        if f is not None and m is not None:
            pts.append((m, f * scale))
    pts = sorted(dict(pts).items())
    if len(pts) < 2:
        return None, "no table coverage"
    k = 0 if mach < pts[0][0] else len(pts) - 2 if mach >= pts[-1][0] else max(i for i in range(len(pts) - 1) if pts[i][0] <= mach)
    (m0, f0), (m1, f1) = pts[k], pts[k + 1]
    # FF ~ a M^2 + b / M^2 (parasite + induced drag at fixed altitude and weight), exact at both points.
    det = m0**2 / m1**2 - m1**2 / m0**2
    a = (f0 / m1**2 - f1 / m0**2) / det
    b = (m0**2 * f1 - m1**2 * f0) / det
    flag = "" if pts[0][0] <= mach <= pts[-1][0] else "extrapolated in Mach"
    return 2 * (a * mach**2 + b / mach**2), flag


def bracket(tables, fl, w_t, mach):
    """Names of the two schedules the model interpolates (or extrapolates) between."""
    pts = []
    for mkey, fkey, _ in SCHEDULES:
        f = bilinear(tables[fkey], fl, w_t)
        m = 0.84 if mkey is None else bilinear(tables[mkey], fl, w_t)
        if f is not None and m is not None:
            pts.append((m, fkey.removesuffix("_ff")))
    pts.sort()
    k = 0 if mach < pts[0][0] else len(pts) - 2 if mach >= pts[-1][0] else max(i for i in range(len(pts) - 1) if pts[i][0] <= mach)
    return f"{pts[k][1]}-{pts[k + 1][1]}"


def isa_mach(fl, tas_kt):
    temp = max(288.15 - 0.0019812 * fl * 100, 216.65)
    return tas_kt * 0.514444 / math.sqrt(1.4 * 287.05287 * temp)


def fly(tables, fuel_kg, zfw_kg, fl, mach, hours=None, factor=1.0, dt_h=1 / 60):
    """Integrate burn at constant FL and Mach for `hours`, or to exhaustion when hours is None."""
    t, flags = 0.0, set()
    while (hours is None and fuel_kg > 0) or (hours is not None and t < hours - 1e-12):
        step = dt_h if hours is None else min(dt_h, hours - t)
        ff, flag = fuel_flow(tables, fl, (zfw_kg + fuel_kg) / 1000, mach)
        if ff is None or ff <= 0 or t > 24:
            return None, t, {flag or "extrapolation failed"}
        flags.add(flag)
        burn = ff * factor * step
        if hours is None and burn > fuel_kg:
            return 0.0, t + step * fuel_kg / burn, flags - {""}
        fuel_kg -= burn
        t += step
    return fuel_kg, t, flags - {""}


def implied_factor(tables, zfw, fuel_kg, fl, mach, hours=None, target_burn=None, target_hours=None):
    """Fuel-flow factor that makes the model match one Boeing number, and the weight midpoint (t)."""
    if target_burn is not None:
        left, _, flags = fly(tables, fuel_kg, zfw, fl, mach, hours)
        return None if left is None else (fuel_kg - left) / target_burn, flags, (zfw + fuel_kg - target_burn / 2) / 1000
    left, t1, flags = fly(tables, fuel_kg, zfw, fl, mach)
    return None if left is None else target_hours / t1, flags, (zfw + fuel_kg / 2) / 1000  # mean weight: half the fuel


def summarise(rows):
    f = [r[0] for r in rows]
    mean = sum(f) / len(f)
    sd = math.sqrt(sum((x - mean) ** 2 for x in f) / (len(f) - 1)) if len(f) > 1 else float("nan")
    return mean, sd


def main():
    tables = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else TABLES).read_text())["tables"]
    fuel0, zfw, seg, end, arc1 = parse_sir(Path(sys.argv[2] if len(sys.argv) > 2 else SIR).read_text())
    print(f"ACARS 17:06:43 fuel {fuel0:,.0f} kg, zero-fuel weight {zfw:,.0f} kg; Boeing's fuel at arc 1 {arc1:,.0f} kg")
    print("Implied factor = model fuel flow / fuel flow Boeing's number requires (>1: the model burns more).")
    inside, outside = [], []

    print("\nTable 3, each segment started from Boeing's fuel at its start:")
    print("  seg  FL   Mach   hours  weight(t)  Boeing burn  model burn   factor  note")
    start = fuel0
    for i, s in enumerate(seg, 1):
        target = start - s["end_lb"] * LB
        f, flags, w = implied_factor(tables, zfw, start, s["fl"], s["mach"], s["hours"], target_burn=target)
        (outside if flags else inside).append((f, w, s["mach"], f"T3 seg {i}", bracket(tables, s["fl"], w, s["mach"])))
        print(f"  {i}   {s['fl']:.0f}  {s['mach']:.3f}  {s['hours']:.3f}   {w:6.1f}     {target:7,.0f}     {f * target:7,.0f}    "
              f"{f:.4f}  {'extrapolated in Mach' if flags else 'inside'}")
        start = s["end_lb"] * LB

    print(f"\nTable 4, from Boeing's {arc1:,.0f} kg at arc 1 to exhaustion (Mach from TAS at ISA):")
    print("  FL    TAS  Mach(printed, ISA)  Boeing h  model h  factor  note")
    for e in end:
        mach = isa_mach(e["fl"], e["tas"])
        f, flags, w = implied_factor(tables, zfw, arc1, e["fl"], mach, target_hours=e["hours"])
        head = f"  {e['fl']:3.0f}   {e['tas']:3.0f}  {e['mach']:.3f}{'*' if e['mrc'] else ' '} {mach:.3f}       {e['hours']:4.2f}"
        if f is None:
            print(f"{head}       -        -    no result: {' '.join(sorted(flags))}")
            continue
        (outside if flags else inside).append((f, w, mach, f"T4 FL{e['fl']:.0f} M{mach:.3f}", bracket(tables, e["fl"], w, mach)))
        print(f"{head}     {e["hours"] / f:4.2f}   {f:.4f}  {'extrapolated in Mach' if flags else 'inside'}")

    mean, sd = summarise(inside)
    print(f"\nInside the tabulated schedules ({len(inside)} items): factor {mean:.4f} +/- {sd:.4f} (s.d.)")
    for f, w, m, name, br in sorted(inside, key=lambda r: (r[4], r[1])):
        print(f"    {name:18s} mean weight {w:5.1f} t  M{m:.3f}  between {br:12s} factor {f:.4f}")
    derived = [r for r in inside if "mrc" in r[4] or "ci52" in r[4]]
    boeing = [r for r in inside if r not in derived]
    for label, rows in (("Boeing schedules only (LRC, M0.84, holding)", boeing), ("using Ulich's derived MRC/CI 52", derived)):
        if len(rows) > 1:
            m_, s_ = summarise(rows)
            print(f"  {label}: {len(rows)} items, factor {m_:.4f} +/- {s_:.4f}")
    wts = [r[1] for r in inside]
    fs = [r[0] for r in inside]
    wm, fm = sum(wts) / len(wts), sum(fs) / len(fs)
    slope = sum((a - wm) * (b - fm) for a, b in zip(wts, fs)) / sum((a - wm) ** 2 for a in wts)
    print(f"  weight trend: {slope * 10:+.4f} per 10 t (weights {min(wts):.0f}-{max(wts):.0f} t)")
    above = [r for r in outside if r[2] > 0.84]
    below = [r for r in outside if r[2] <= 0.84]
    for label, rows in (("above M0.84", above), ("below the lowest schedule", below)):
        if rows:
            print(f"Extrapolated {label} ({len(rows)} items): " + ", ".join(
                f"{name} {f / mean - 1:+.1%}" for f, w, m, name, _ in sorted(rows, key=lambda r: r[2])) + "  (relative to the inside factor)")
    bad = sum(abs(f - mean) > 3 * sd for f, *_ in inside)
    print(f"[{'PASS' if sd <= TOLERANCE_SD and bad == 0 else 'FAIL'}] inside-range factors agree to s.d. {sd:.3f} "
          f"(tolerance {TOLERANCE_SD}); {bad} beyond 3 s.d.")
    sys.exit(0 if sd <= TOLERANCE_SD and bad == 0 else 1)

if __name__ == "__main__":
    main()
