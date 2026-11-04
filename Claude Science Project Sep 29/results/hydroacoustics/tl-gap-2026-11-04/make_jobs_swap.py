"""Batch 3: source-region sound-speed swap (4 Nov 2026). Only the WOA23 sound-speed nodes of the first 400 km of a section
are replaced by the donor's FIRST node profile (blended linearly in sound speed from 400 to 500 km); bathymetry, seabed and
the rest of the path are unchanged. Forward RAM, 10 m source, frozen physics (gapdiag.fwd_freq), L1 seabed.
  SW_wake_warm : F-35A -> H11N with the 35.5 S arc-point March profile under the source region
  SW_arc_cold  : 35.5 S -> H01W with the F-35A (40.64 N, April) profile under the source region
  SW_arc39_cold: 39.0 S -> H01W with the F-35A profile under the source region
Usage: python make_jobs_swap.py <workdir>"""
import json, os, pickle, sys
import numpy as np
W = sys.argv[1]
sys.path.insert(0, os.environ["TLCHAIN_DIR"])
from tlchain import chain as C                     # noqa: E402
from tlchain.bottom import LAYERED                 # noqa: E402
sd = os.path.join(W, "sec")
ld = lambda n: pickle.load(open(os.path.join(sd, n + ".pkl"), "rb"))   # noqa: E731


def swap(sec, donor_profile, r_full=400.0, r_blend=500.0):
    zd, cd = donor_profile
    s = dict(sec); nodes = []
    for r, z, c in sec["nodes"]:
        if r <= r_blend:
            cdi = np.interp(z, zd, cd)
            w = 1.0 if r <= r_full else (r_blend - r) / (r_blend - r_full)
            c = w * cdi + (1 - w) * c
        nodes.append((r, z, c))
    s["nodes"] = nodes
    return s


wake, a35, a39 = ld("f35a-H11N"), ld("arc35.5S-H01W"), ld("arc39.0S-H01W")
prof = lambda s: (s["nodes"][0][1], s["nodes"][0][2])   # noqa: E731
cases = {"SW_wake_warm": (swap(wake, prof(a35)), 730.6666666666666), "SW_arc_cold": (swap(a35, prof(wake)), 1055.0),
         "SW_arc39_cold": (swap(a39, prof(wake)), 1055.0)}
J = []
for nm, (s, rd) in cases.items():
    pk = os.path.join(sd, nm + ".pkl"); pickle.dump(s, open(pk, "wb"))
    for fc in [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]:
        for f in C.band_freqs(fc, 7):
            J.append(dict(id=f"fwd|L1|{nm}|{fc:g}|{f:.4f}", kind="fwd", sec=pk, f=float(f), zsrc=10.0, rd=rd, bottom=LAYERED.as_dict(),
                          rec_every_m=1000.0, cost=float(s["L_km"] * f * max(f, 30.0))))
json.dump(J, open(os.path.join(W, "jobs_swap.json"), "w")); print(len(J), "jobs")
