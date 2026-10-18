"""As measure_eof.py, but 00:11 parents with IDENTICAL states (latitude, longitude, altitude, BFO bias mean) are merged:
Kish ESS over distinct 00:11 STATES, per treatment and impact band, overall and per mode."""
import json, sys, pathlib, numpy as np
sys.path.insert(0, sys.argv[6]); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from compact_impacts import load
from run_i_maps import cell_logmass
from measure_eof import seeds, acc, CELLS, BANDS, NB
def main(eof, core, out, k, n):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    for st, P, K, sd in seeds(eof)[k::n]:
        f = out / f"{st}.{sd.name}.json"
        if f.exists(): continue
        meta, g = load(sd)
        hpath = pathlib.Path(core) / st / "bto-bfo" / sd.name / "handoff-m0011" / "handoff.npy"
        lm = cell_logmass(g, meta, hpath); H = np.load(hpath)
        _, sid = np.unique(H[:, [1, 2, 3, 8]], axis=0, return_inverse=True); sid = sid.ravel()
        lat = g("latitude_deg"); par = g("parent").astype(np.int64); st_id = sid[par]
        b = np.digitize(lat, BANDS) - 1; b[(b < 0) | (b >= NB)] = -1
        mode = H[par, 6].astype(int); c = np.log(P / K)
        R = {"stratum": st, "seed": sd.name, "distinct_states": int(sid.max() + 1)}
        for d in CELLS:
            a = lm[d]; m = np.zeros(len(a)); fin = np.isfinite(a); m[fin] = np.exp(c + a[fin])
            R[d] = {"full": [x.tolist() for x in acc(m, b, st_id)], "total": float(m.sum()),
                    "by_mode": {int(md): [x.tolist() for x in acc(np.where(mode == md, m, 0), b, st_id)] for md in range(5)}}
        json.dump(R, open(f, "w")); print(st, sd.name, flush=True)
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
