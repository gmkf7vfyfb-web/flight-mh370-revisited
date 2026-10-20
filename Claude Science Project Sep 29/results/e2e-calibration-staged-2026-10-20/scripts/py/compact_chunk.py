"""A2 shared truth pool: compact one chunk of single-particle prior replicates into one npz, with the deterministic
BTO/BFO predictions at every cruise epoch (so a case's synthetic data is prediction + bias + noise, drawn per case).
The handoff-m0011 directory of every seed is kept under POOL/handoff/seed-N/ (the end-of-flight stage needs it);
the residual snapshots are compacted and deleted. Same candidate rules as pick_truth.py (fuel hard reject, hand-off row match).
Usage: compact_chunk.py CHUNK_DIR OUT_NPZ OBS_CSV EPH_CSV POOL_DIR"""
import sys, os, glob, math, shutil, tomllib
import numpy as np
from e2e_common import read_rows, sat_state, bto_us, bfo_nobias

NAMES = ["LateralNavigation", "MagneticHeading", "MagneticTrack", "TrueHeading", "TrueTrack"]


def stop_header(p):
    txt = open(p).read(); head = txt.split("[lookahead]")[0] if "[lookahead]" in txt else txt.split("[[row]]")[0]
    return tomllib.loads(head)["stop"]


def main():
    chunk, out, obs_csv, eph_csv, pool = sys.argv[1:6]
    O = {r["epoch_id"]: r for r in read_rows(obs_csv)}; EP = read_rows(eph_csv)
    ep_ids = [e for e in O if not e.startswith("m0019")]
    bfo_eps = [e for e in ep_ids if "bfo" in O[e]["cruise"].split()]
    sat = {e: sat_state(EP, e) for e in ep_ids}
    seeds, strata, rows, logw, H, S, BP, FP, VU = [], [], [], [], [], [], [], [], []
    n_seed = n_rej = 0
    for sd in sorted(glob.glob(f"{chunk}/prior/seed-*")):
        seed = int(os.path.basename(sd)[5:]); n_seed += 1
        st = stop_header(f"{sd}/handoff-m0011/handoff.toml"); lz = st["log_evidence_by_mode"]
        Hn = np.load(f"{sd}/handoff-m0011/handoff.npy")
        for s, name in enumerate(NAMES):
            if lz[s] < -1e5: n_rej += 1; continue
            snap = {}; ok = True
            for e in ep_ids + ["w" + e for e in bfo_eps] + ["x" + e for e in bfo_eps]:
                f = f"{sd}/residuals/{name}-{e}.npy"
                if not os.path.exists(f): ok = False; break
                snap[e] = np.load(f)[0].astype(np.float64)
            if not ok: continue
            m11 = snap["m0011"]; d = np.hypot(Hn[:, 1] - m11[0], Hn[:, 2] - m11[1]); j = int(np.argmin(d))
            if d[j] > 1e-4: continue
            bp = np.full(len(ep_ids), np.nan); fp = np.full(len(ep_ids), np.nan); vu = np.zeros(len(ep_ids))
            for i, e in enumerate(ep_ids):
                r = O[e]; sn = snap[e]; lat, lon, alt, gs, trk = sn[:5]
                if r["bto_us"]: bp[i] = float(r["bto_us"]) - sn[7]
                if e in bfo_eps:
                    fwd = (snap["x" + e][2] - alt) * 60.0; bwd = (alt - snap["w" + e][2]) * 60.0
                    v = 0.0 if (abs(fwd) < 1 or abs(bwd) < 1) else (fwd if abs(fwd) >= abs(bwd) else bwd)
                    sp, sv = sat[e]; vn, ve = gs * math.cos(math.radians(trk)), gs * math.sin(math.radians(trk))
                    fp[i] = bfo_nobias(sp, sv, float(r["satellite_afc_hz"]), lat, lon, alt, vn, ve, v); vu[i] = v
            seeds.append(seed); strata.append(s); rows.append(j); logw.append(float(lz[s])); H.append(Hn[j])
            S.append(np.array([snap[e][:5] for e in ep_ids])); BP.append(bp); FP.append(fp); VU.append(vu)
        hd = f"{chunk}/handoff/seed-{seed}"; os.makedirs(hd, exist_ok=True)
        shutil.move(f"{sd}/handoff-m0011/handoff.npy", f"{hd}/handoff.npy"); shutil.move(f"{sd}/handoff-m0011/handoff.toml", f"{hd}/handoff.toml")
        os.system(f"gzip -f {hd}/handoff.toml")
    # one tar per chunk (A2 pool layout): the end-of-flight stage extracts only the candidates a case flies
    tarf = out.replace(".tmp.npz", "").replace(".npz", "") + "-handoff.tar"
    rc = os.system(f"tar cf {tarf}.tmp -C {chunk}/handoff . && mv {tarf}.tmp {tarf}")
    if rc != 0: sys.exit("handoff tar failed")
    np.savez_compressed(out, ep_ids=np.array(ep_ids), seed=np.array(seeds, np.int64), stratum=np.array(strata, np.int8), row=np.array(rows, np.int16),
                        chunk_tar=np.array([os.path.basename(tarf)] * len(seeds)), log_w=np.array(logw), H=np.array(H), state=np.array(S), bto_pred=np.array(BP), bfo_pred=np.array(FP), vup=np.array(VU))
    print(f"chunk {chunk}: seeds {n_seed}, candidates {len(seeds)}, fuel-rejected strata {n_rej}")


if __name__ == "__main__":
    main()
