"""Calibration evidence for the fuel models (fuel session, 9-10 Oct 2026).

Public (usable for the paper):
  * SIR Appendix 1.6E (Boeing performance analysis), printed pp. 1-8: ACARS fuel and gross weight at
    17:06:43 (p. 1, p. 4), standard day (p. 3), Table 3 segments (p. 5), arc-1 fuel 73,908 lb (p. 5),
    Table 4 endurance from arc 1 (p. 6). Parsed from the text copy in
    `ISO Sept 28 Status/inputs/end-of-flight/report-text/boeing_performance_appendix_1_6E.txt`
    with the regular expressions of `.sources/fuel-performance/validate.py`.
  * SIR main report Table 1.9A (printed p. 113, located via the archive citation ledger): MH370 ACARS
    at 17:01:43 and 17:06:43 (FL350, M0.819/0.821, SAT -43.9/-43.8 C, FQIS 44,500/43,800 kg).

Internal only (provenance unverified; recorded in results/restricted-sources-ledger.md):
  * `library_full_audit/MH370/mh371-acars.xlsx` and `MH371_EHM_Export.xls`: 9M-MRO's previous flight,
    MH371 ZBAA-WMKK on 7 Mar 2014. Five-minute ACARS position reports (pressure altitude, Mach, SAT,
    gross weight GWT in lb at 40 lb resolution, FQIS fuel TOTFW in kg at 100 kg resolution) and
    decoded EHM snapshots with per-engine fuel flow.
"""

import math
import re
import sys
from pathlib import Path

import numpy as np

LB = 0.45359237
HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent


def parse_sir(text):
    """SIR App. 1.6E targets, with validate.py's regular expressions (copied: validate.py needs Python 3.12)."""
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
    for s in seg:  # durations from distance / ground speed (wind is +headwind), ~0.2 % precision
        s["hours_gs"] = s["nm"] / (s["tas"] - s["wind"])
    return dict(fuel0_kg=fuel_lb * LB, zfw_kg=(gross_lb - fuel_lb) * LB, seg=seg, end=end, arc1_kg=arc1_lb * LB)


def mh370_acars():
    return [dict(utc="17:01:43", alt_ft=34998.0, mach=0.819, sat_c=-43.9, fuel_kg=44500.0),
            dict(utc="17:06:43", alt_ft=35004.0, mach=0.821, sat_c=-43.8, fuel_kg=43800.0)]


def mh371_cruise(path):
    """Constant-altitude 5-min intervals of MH371 (|dALT| < 30 ft at both ends, both ends in cruise)."""
    import pandas as pd
    ac = pd.read_excel(path)
    ac = ac.loc[:, ~ac.columns.astype(str).str.startswith("Unnamed")]
    t = [x.hour * 3600 + x.minute * 60 + x.second for x in ac["UT"]]
    ac["t_s"] = t
    rows = []
    for k in range(len(ac) - 1):
        a, b = ac.iloc[k], ac.iloc[k + 1]
        if abs(a.ALT - b.ALT) < 30 and a.ALT > 25000:
            rows.append(dict(t0=a.t_s, t1=b.t_s, fl=(a.ALT + b.ALT) / 200.0, mach0=a.MACH, mach1=b.MACH,
                             sat0=a.SAT, sat1=b.SAT, gwt0_kg=a.GWT * LB, gwt1_kg=b.GWT * LB,
                             fw0=a.TOTFW, fw1=b.TOTFW))
    return rows


def segments(rows):
    """Group consecutive constant-FL intervals into segments (same FL within 30 ft)."""
    segs, cur = [], []
    for r in rows:
        if cur and (abs(r["fl"] - cur[-1]["fl"]) > 0.3 or r["t0"] != cur[-1]["t1"]):
            segs.append(cur)
            cur = []
        cur.append(r)
    if cur:
        segs.append(cur)
    return segs
