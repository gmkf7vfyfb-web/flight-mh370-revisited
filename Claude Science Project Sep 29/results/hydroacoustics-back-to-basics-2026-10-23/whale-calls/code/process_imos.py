"""Step 2: run every whale detector on every IMOS record (8 March 2014 records of all five loggers and the
14-day backgrounds of 3250, 3274, 3376). One pass per record:
  * template (kernel) detectors, real and null templates (target-decoy false-alarm estimate);
  * pulse detectors on a 0.512 s spectrogram: fin-whale 20 Hz pulses (15-30 Hz vs 35-45 Hz), fin-whale upper
    component (92-100 Hz vs 80-88 / 104-112 Hz), Omura's noisy pulsed units (20-45 Hz vs 50-60 Hz, 2.5-9 s);
  * long-term spectral average (median and 90th percentile spectrum, 0.244 Hz bins) and chorus metrics.
Usage: python process_imos.py <job_list.csv> <shard k> <n shards> <out_dir>
job_list columns: cid, path (absolute), set ('event' | 'background').
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import imos_io as io  # noqa: E402
import whale_detectors as wd  # noqa: E402

BANK = wd.template_bank()
DUR = {k: max(v[3] for v in vs) for k, vs in BANK.items()}
THR = 4.0


def template_rows(L, f, t):
    N = wd.noise_normalise(L)
    hb = (f >= 85) & (f <= 120)
    bb_series = np.median(N[hb], axis=0)                       # broadband index (dB above floor, 85-120 Hz)
    b1530 = wd.band_db(L, f, 15, 30)
    b_med = np.median(b1530)
    dt = t[1] - t[0]
    out, _ = wd.run_templates(L, f, t, BANK)
    nul, _ = wd.run_templates(L, f, t, BANK, null=True)
    rows = []
    for kind, res in (("real", out), ("null", nul)):
        for name, (s, arg) in res.items():
            for i in wd.peaks_from_score(s, t, THR, min_sep_s=0.6 * DUR[name]):
                segs, harm, w, D = BANK[name][arg[i]]
                if kind == "null":
                    sh = wd.NULL_SHIFT_HZ.get(name)
                    segs = wd.mirrored(segs, D) if sh is None else wd.shifted(segs, sh)
                fr = [x for s_ in segs for x in (s_[2], s_[3])]
                i0, i1 = i, min(len(t), i + int(round(D / dt)) + 1)
                bb = float(np.mean(bb_series[i0:i1]))
                exc = float(10 * np.log10(np.mean(10 ** (b1530[i0:i1] / 10))) - b_med)
                lvl = float(10 * np.log10(np.mean(10 ** (b1530[i0:i1] / 10))))
                rows.append(dict(kind=kind, family=name, t_start=float(t[i] - 1.0), dur=float(D),
                                 score=float(s[i]), variant=int(arg[i]), f_lo=float(min(fr)), f_hi=float(max(fr)),
                                 f_first=float(segs[0][2]), f_last=float(segs[-1][3]),
                                 bb_db=bb, band15_30_excess_db=exc, band15_30_level_db=lvl))
    return rows


def pulse_rows(Ls, fs_, ts_):
    rows = []
    specs = {"FIN20": dict(band=(15, 30), flanks=((35, 45),), thr_db=4.0, min_dur=0.4, max_dur=2.5),
             "FIN_HF": dict(band=(92, 100), flanks=((80, 88), (104, 112)), thr_db=4.0, min_dur=0.4, max_dur=2.5),
             "OMURA_PULSED": dict(band=(20, 45), flanks=((50, 60),), thr_db=4.0, min_dur=2.5, max_dur=9.0)}
    for name, kw in specs.items():
        ev, _ = wd.pulse_events(Ls, fs_, ts_, **kw)
        for r in ev.itertuples():
            rows.append(dict(family=name, t_peak=r.t_peak, dur=r.dur, excess_db=r.excess_db, level_db=r.level_db))
    return rows


def ltsa(L, f):
    lin = 10 ** (L / 10)
    med = np.median(L, axis=1)
    p90 = np.percentile(L, 90, axis=1)
    mean = 10 * np.log10(lin.mean(axis=1))

    def band(lo, hi, v):
        m = (f >= lo) & (f < hi)
        return float(10 * np.log10(np.mean(10 ** (v[m] / 10))))
    ch = dict(abw_peak=band(25.7, 26.5, med), abw_ref=0.5 * (band(24.4, 25.2, med) + band(27.0, 27.8, med)),
              pb_h3=band(64.0, 70.5, p90), pb_h3_ref=0.5 * (band(58.0, 62.0, p90) + band(73.0, 77.0, p90)),
              lvl_5_40=band(5, 40, mean), lvl_17_27=band(17, 27, mean), lvl_10_17=band(10, 17, mean),
              lvl_27_40=band(27, 40, mean))
    return med.astype(np.float32), p90.astype(np.float32), mean.astype(np.float32), ch


def one(cid, path, set_):
    d = io.load(cid, path)
    f, t, P = io.spectrogram(d["x"], 1024, 125)
    m = (f >= 5) & (f <= 120)
    f = f[m]
    L = 10 * np.log10(P[m] + 1e-30) + io.cal_db(cid, f)[:, None]
    fs_, ts_, Ps = io.spectrogram(d["x"], 128, 32)
    ms = (fs_ >= 5) & (fs_ <= 120)
    fs_ = fs_[ms]
    Ls = 10 * np.log10(Ps[ms] + 1e-30) + io.cal_db(cid, fs_)[:, None]
    meta = dict(cid=cid, src=str(path), set=set_, t0_utc=str(d["t0_utc"]), t0_logger=str(d["t0_logger"]),
                dur=len(d["x"]) / io.FS)
    tr = [dict(meta, **r) for r in template_rows(L, f, t)]
    pr = [dict(meta, **r) for r in pulse_rows(Ls, fs_, ts_)]
    med, p90, mean, ch = ltsa(L, f)
    return tr, pr, dict(meta, **ch), (med, p90, mean), f


if __name__ == "__main__":
    jobs = pd.read_csv(sys.argv[1])
    k, n, out = int(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4])
    out.mkdir(parents=True, exist_ok=True)
    TR, PR, CH, SP = [], [], [], []
    for j in jobs.iloc[k::n].itertuples():
        try:
            tr, pr, ch, sp, f = one(str(j.cid), j.path, j.set)
        except Exception as e:  # noqa: BLE001
            CH.append(dict(cid=str(j.cid), src=j.path, set=j.set, error=repr(e)))
            continue
        TR += tr
        PR += pr
        CH.append(ch)
        SP.append(np.stack(sp))
    pd.DataFrame(TR).to_parquet(out / f"templates_{k:02d}.parquet")
    pd.DataFrame(PR).to_parquet(out / f"pulses_{k:02d}.parquet")
    pd.DataFrame(CH).to_parquet(out / f"records_{k:02d}.parquet")
    np.savez_compressed(out / f"ltsa_{k:02d}.npz", spec=np.array(SP, dtype=np.float16), f=f,
                        src=np.array([c["src"] for c in CH if "error" not in c]))
    print(k, len(CH), "records")
