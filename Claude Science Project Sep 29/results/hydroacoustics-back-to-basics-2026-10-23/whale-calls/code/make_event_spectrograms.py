"""Step 1: calibrated spectrograms of every 8 March 2014 IMOS record (all five loggers, all roles incl. 'S').
Output: whale/work/spec_event/<cid>_<hex>.npz with
  L  : float16 [f, t] dB re 1 uPa^2/Hz, 4.096 s Hann, 0.5 s step, 0.244 Hz bins, 5-120 Hz
  Ls : float16 [f, t] dB re 1 uPa^2/Hz, 0.512 s Hann, 0.128 s step, 1.95 Hz bins, 5-120 Hz (pulse resolution)
  f, t, fs_, ts_, t0_utc (ISO), t0_logger (ISO)
"""
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import imos_io as io  # noqa: E402

OUT = Path("whale/work/spec_event")
FMIN, FMAX = 5.0, 120.0


def one(args):
    cid, rel = args
    out = OUT / f"{cid}_{Path(rel).stem}.npz"
    if out.exists():
        return str(out)
    d = io.load(cid, io.IMOS / rel)
    f, t, P = io.spectrogram(d["x"], 1024, 125)
    m = (f >= FMIN) & (f <= FMAX)
    L = 10 * np.log10(P[m] + 1e-30) + io.cal_db(cid, f[m])[:, None]
    fs_, ts_, Ps = io.spectrogram(d["x"], 128, 32)
    ms = (fs_ >= FMIN) & (fs_ <= FMAX)
    Ls = 10 * np.log10(Ps[ms] + 1e-30) + io.cal_db(cid, fs_[ms])[:, None]
    np.savez_compressed(out, L=L.astype(np.float16), Ls=Ls.astype(np.float16), f=f[m], t=t, fs_=fs_[ms], ts_=ts_,
                        t0_utc=str(d["t0_utc"]), t0_logger=str(d["t0_logger"]), cid=cid, src=rel,
                        dur=len(d["x"]) / io.FS)
    return str(out)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    recs = pd.read_csv(sys.argv[1])
    jobs = [(str(r.logger), r.file) for r in recs.itertuples()]
    k, n = int(sys.argv[2]), int(sys.argv[3])      # shard k of n (run shards as separate processes)
    res = [one(j) for j in jobs[k::n]]
    print(len(res), "done")
