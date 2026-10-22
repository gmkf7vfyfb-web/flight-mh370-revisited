"""Background null worker (preregistration.py section 5): window maxima of every pre-registered statistic on the
IMOS background files of one logger shard; for 3376 also the emulated-panel statistics (null A for the digitised
Kadri panels). Usage: python null_worker.py <logger> <shard> <nshards> <out.npz>"""
from __future__ import annotations
import sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import preregistration as R, detectors as D
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import imos_noise as N, imos_preregistration as P


def main(logger, shard, nshards, out):
    t0 = time.time()
    files = sorted((R.BG_ROOT / logger).glob("2014*/*.DAT"))[shard::nshards]
    T = np.load(R.TEMPLATES)
    bank_i, _ = D.bank_env(T, R.IMOS_BANK_RANGES, 100)
    bank_p = {st: D.bank_env(T, (R.PANEL_BANK_RANGE[st],), 100)[0] for st in R.IMS}
    acc, accp, nfile, nbad = {}, {st: {} for st in R.IMS}, 0, 0
    for k, f in enumerate(files):
        try:
            fs, _, _, _ = P.header(f)
            if fs != 6000: nbad += 1; continue
            x500 = N.decimate(N.read_volts(f))
        except Exception:  # noqa: BLE001
            nbad += 1; continue
        st, _ = D.imos_stats(x500, bank_i)
        sc = D.scores_all(st, len(x500) / R.FS_D)
        for key, (ws, s, tm) in sc.items():
            acc.setdefault(key, []).append(s)
        if logger == "3376":
            x20 = D.emulate_plot(x500)
            for stn in R.IMS:
                stp, _ = D.panel_stats(x20, bank_p[stn])
                scp = D.scores_all(stp, len(x20) / R.PANEL_FS)
                for key, (ws, s, tm) in scp.items():
                    accp[stn].setdefault(key, []).append(s)
        nfile += 1
        if k % 50 == 0:
            print(logger, shard, k, len(files), round(time.time() - t0), flush=True)
    res = {k: np.concatenate(v) for k, v in acc.items()}
    for stn in R.IMS:
        for k, v in accp[stn].items():
            res[f"panel_{stn}_{k}"] = np.concatenate(v)
    res["n_files"] = np.array([nfile, nbad])
    np.savez_compressed(out, **res)
    print("done", logger, shard, nfile, nbad, round(time.time() - t0), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
