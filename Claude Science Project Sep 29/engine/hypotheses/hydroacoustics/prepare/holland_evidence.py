"""Convert end of flight's summary/holland-sweep-summary.json (run D-he) to the run C family-evidence format read by
search_windows_mixture.py (amendment 5). ln Zhat per stratum = log mean exp of the per-seed ln Z (EoF pooling).
Usage: python holland_evidence.py <holland-sweep-summary.json> <out_primary.json> <out_without.json>"""
import json, sys
import numpy as np
d = json.load(open(sys.argv[1])); opts = ["00:19 Held Out", "00:19 R600 BTO Only", "00:19 R600 BTO + Raw BFO", "00:19 Holland H1", "00:19 Holland H2"]
for ver, out in (("primary", sys.argv[2]), ("without survival factor", sys.argv[3])):
    st = {}
    for s in d["strata_weights"]:
        st[s] = {}
        for o in opts:
            v = np.array(d["per_stratum_seed_lnZ"][f"{s}|{o}|{ver}"], float); m = v.max()
            st[s][f"{o} +unpowered"] = {"ln_Zhat": float(m + np.log(np.mean(np.exp(v - m)))), "ln_Z_per_seed": v.tolist()}
    json.dump({"p_core": d["strata_weights"], "strata": st, "source": sys.argv[1], "version": ver}, open(out, "w"), indent=1)
    print(ver, {s: round(st[s]["00:19 Holland H1 +unpowered"]["ln_Zhat"], 3) for s in st})
