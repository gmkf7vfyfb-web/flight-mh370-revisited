"""Observation + ephemeris tables with dummy BTO epochs 1 s before ('w'+id) and after ('x'+id) every cruise-BFO epoch, so the fuel-only truth run's
residual snapshots carry the altitude 1 s later (vertical rate for the cruise BFO model, bfo_vertical_rate = true).
Dummy BTO values are placeholders and are never scored (truth run: use_bto = use_bfo = false)."""
import sys
from e2e_common import read_rows, write_rows, header_of, utc_plus
obs_in, eph_in, obs_out, eph_out = sys.argv[1:5]
H = header_of(obs_in); HE = header_of(eph_in); O = read_rows(obs_in); EP = read_rows(eph_in)
oo, ee = [], []
for r in O:
    oo.append(r); e = next(x for x in EP if x["epoch_id"] == r["epoch_id"]); ee.append(e)
    if "bfo" not in r["cruise"].split(): continue
    for pre, ds in (("w", -1), ("x", 1)):
        d = {k: "" for k in H}; d.update(epoch_id=pre + r["epoch_id"], time_utc=utc_plus(r["time_utc"], ds), seconds_from_t0=str(float(r["seconds_from_t0"]) + ds),
                                         bto_us="12000", bto_sd_us="29", satellite_afc_hz=r["satellite_afc_hz"], cruise="bto", note=f"e2e dummy {ds:+d} s")
        de = dict(e); de["epoch_id"] = d["epoch_id"]; de["time_utc"] = d["time_utc"]
        if ds < 0: oo.insert(len(oo) - 1, d); ee.insert(len(ee) - 1, de)
        else: oo.append(d); ee.append(de)
write_rows(obs_out, oo, H); write_rows(eph_out, ee, HE); print(len(oo), "rows")
