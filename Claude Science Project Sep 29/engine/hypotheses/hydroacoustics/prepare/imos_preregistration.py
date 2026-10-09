"""PRE-REGISTRATION for amended-sequence items 1d (noise per station and band) and the windows of 2b
(raw-data detectors), IMOS/Curtin CMST passive-acoustic loggers, 7-9 March 2014.

Written and committed BEFORE any sample of any recording is read. Up to this commit only these were read:
the package file listings, the 5 ASCII header lines and the ASCII footer of each .DAT (start time,
sample rate, filter settings), the metadata .txt files, CalibrationNotes.txt and load_loggerdatanew.m.
CMST's 'Scott Reef IMOS logger data analysis for 2014_03_08_Release.pdf' in the package has NOT been read;
it will be read after this commit and cited, not used to move windows.

DATA (provenance; sha256 per archive in SHA256SUMS.txt beside them; per-file sha256 written by this script):
  https://imos-data.s3-ap-southeast-2.amazonaws.com/IMOS/ANMN/Acoustic/MH370.zip           (566,154,736 B)
  https://imos-data.s3-ap-southeast-2.amazonaws.com/IMOS/ANMN/Acoustic/Portland_MH370.zip  (481,482,329 B)
  held at /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/ (not committed: ~1 GB).
  Loggers: 3315 and 3376 Perth Canyon (3315 = CMST's 'RCS', 450 m water depth, CMST 2014-30 p. 6);
  3250 Scott Reef (216 m); 3274 and 3275 Portland. 6 kHz, 16 bit, ~307 s every 15 min (34 % duty cycle).
  Hardware filter LF=008: the analogue high-pass corner is 8 Hz on every logger.

FORMAT (load_loggerdatanew.m): big-endian; 5 header lines; interleaved uint16 samples; ASCII footer from
'Record'; volts = counts*5/65536, mean removed. Start time = footer 'First Data' (logger clock).

CLOCK (metadata): logger error e(t) linear between 'system clock set 1' and 'set 2'. The sign convention
is NOT stated in the package. Two conventions: A: true = logger - e(t); B: true = logger + e(t). On 8 March
they differ by 2 e(t) (about 52 s at 3315). PRE-REGISTERED RESOLUTION: the Curtin event at RCS (3315),
peak energy 01:33:44 UTC +/- 4 s after CMST's drift correction (CMST 2014-30 p. 6). Procedure: in the 3315
recording(s) covering logger time 01:32-01:36 under either convention, band-pass 5-40 Hz (4th-order
Butterworth, zero phase), envelope = |Hilbert|, smoothed with a 2 s moving mean; the peak's logger time
is converted under A and B; a convention is ACCEPTED if it lands within 4 + 2 s of 01:33:44 and the other
does not. Otherwise 'unresolved' and every window below is the union under A and B. The same convention is
applied to every logger (same manufacturer, same clock-set procedure); this is an assumption, disclosed.

PREDICTED ARRIVALS: impact samples from the parametric 7th-arc stand-in (synthetic_composer_test,
N_PRIOR, SEED, BASE: impact time 00:19:37 + 300 s, sd 180 s), as in 2a, until end of flight publishes
impacts. Travel time = geodesic range / c_g with c_g ~ N(1.482, 0.006) km/s. The final up-slope leg to a
shallow logger is not modelled (it adds seconds, not minutes). Path blockage is NOT assessed here: there is
no shared bathymetry and no stub ruling for these paths (ruling request H5). The Scott Reef path passes
near North West Cape and the Exmouth Plateau and is flagged.

SIGNAL WINDOW S (true UTC): [q0.5 - 120 s, q99.5 + 120 s] of the predicted arrival. Mapped to logger time
under the accepted convention (or the union). COVERAGE = predictive probability that the arrival falls
inside a recording, reported per logger; it multiplies any P_D.

BACKGROUND B: every recording that starts within [S_start - 6 h, S_end + 6 h] and does not overlap
[S_start - 300 s, S_end + 300 s]. The MH370 set starts at 00:00 on 8 March (logger time), so B is
asymmetric there; that is reported, not padded.

ITEM 1d, NOISE (run by imos_noise.py; recordings in S are NOT opened by 1d):
  - calibration: system gain G(f) = PSD of the pre-deployment calibration file (white noise at
    -90 dB re 1 V^2/Hz input) minus (-90); p(f) [Pa^2/Hz] = V^2/Hz / 10^(G/10) / 10^(S_h/10), with S_h the
    hydrophone sensitivity in dB re V^2/Pa^2 from the metadata. Calibration file per logger from the
    metadata 'system gain file'.
  - spectra: decimate to 500 Hz (FIR anti-alias); Welch, 4 s Hann, 50 % overlap, per recording.
  - bands [Hz]: 2-5, 5-10, 10-20, 20-40, 40-80, 80-160, 160-240. Band level = mean calibrated PSD in the
    band, dB re 1 uPa^2/Hz.
  - percentiles 5/50/95 over the 1 s band-level series pooled across B (1 s Hann-windowed periodograms on
    the decimated series), and over per-recording Welch levels.
  - burstiness: (P99 - P50) of the 1 s band levels in dB, and the excess kurtosis of 1 s band energy.
  - flags: a band is 'ROLL-OFF' if its mean G is more than 20 dB below G at 100 Hz (the 8 Hz analogue
    corner); its calibrated levels are reported but marked provisional.

OUTPUTS: data/imos/preregistration.json (windows, coverage, B lists, clock model), data/imos/recordings.csv
(every file: logger, name, sha256, start logger time, samples, role S/B/other).
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import synthetic_composer_test as sct  # noqa: E402
from pyproj import Geod  # noqa: E402

IMOS = Path("/Users/pete/Downloads/mh370-inputs/hydroacoustics/imos")
SETS = {"3315": "MH370/3315_PerthCanyon", "3376": "MH370/3376_PerthCanyon", "3250": "MH370/3250_ScottReef",
        "3274": "Portland_MH370/3274_Portland", "3275": "Portland_MH370/3275_Portland"}
META = ["MH370/3315_3250_3376__MetaData.txt", "Portland_MH370/MetaData_3274_3275.txt"]
CAL_DIRS = ["MH370/Calibration", "Portland_MH370/calibration"]
T_IMPACT_REF = pd.Timestamp("2014-03-08T00:19:37Z")
C_G, SD_C = 1.482, 0.006
PAD_S, GUARD_S, BG_H = 120.0, 300.0, 6.0
CURTIN_RCS_UTC, CURTIN_TOL_S = pd.Timestamp("2014-03-08T01:33:44Z"), 6.0
GEOD = Geod(ellps="WGS84")


def dm(s):
    m = re.match(r"\s*(\d+)\s*deg\s*([\d.]+)'\s*([NSEW])", s)
    v = int(m.group(1)) + float(m.group(2)) / 60
    return -v if m.group(3) in "SW" else v


def parse_meta():
    out = {}
    for mf in META:
        txt = (IMOS / mf).read_text(errors="replace").replace("\r", "")
        for block in txt.split("Curtin ID")[1:]:
            lines = ("Curtin ID" + block).splitlines()
            kv = {ln[:40].strip(): ln[40:].strip() for ln in lines if len(ln) > 40}
            cid = kv["Curtin ID"]
            c1, c2 = kv["system clock set 1"].split(), kv["system clock set 2"].split()
            out[cid] = dict(lat=dm(kv["Latitude (WGS84)"]), lon=dm(kv["Longitude (WGS84)"]),
                            set_details=kv["Set details"],
                            clock1=(pd.Timestamp(f"{c1[0]} {c1[1]}", tz="UTC"), float(c1[2])),
                            clock2=(pd.Timestamp(f"{c2[0]} {c2[1]}", tz="UTC"), float(c2[2])),
                            sens_db=float(kv["hydrophone sensitivity (dB re V^2/Pa^2)"]),
                            cal_file=kv["system gain file"].split()[-1])
    return out


def clock_err(meta, t):
    (t1, e1), (t2, e2) = meta["clock1"], meta["clock2"]
    return e1 + (e2 - e1) * (t - t1).total_seconds() / (t2 - t1).total_seconds()


def header(path):
    with open(path, "rb") as f:
        hdr = [f.readline().decode("latin1").rstrip() for _ in range(5)]
        start = f.tell()
        f.seek(-1000, 2)
        tail = f.read().decode("latin1")
        size = f.seek(0, 2)
    fs = int(re.search(r"Sample Rate (\d+)", hdr[2]).group(1))
    first = re.search(r"First Data-(\d{4}/\d\d/\d\d \d\d:\d\d:\d\d)", tail).group(1)
    footer_bytes = 1000 - tail.index("Record")
    n = (size - footer_bytes - 2 - start) // 2
    return fs, pd.Timestamp(first.replace("/", "-"), tz="UTC"), int(n), hdr[3]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def predicted(meta, summary_path):
    rng = np.random.default_rng(sct.SEED)
    ridge, grid, dens, _ = sct.ridge_and_marginal(summary_path)
    q, _ = sct.fit_small_circle(ridge)
    pr = sct.draw_prior(rng, q, grid, dens, sct.N_PRIOR, sct.BASE["sigma_x_nm"])
    n = len(pr)
    t_imp = sct.BASE["mu_t_s"] + rng.normal(0, sct.BASE["sigma_t_s"], n)
    c = rng.normal(C_G, SD_C, n)
    out = {}
    for cid, m in meta.items():
        az, _, d = GEOD.inv(np.full(n, m["lon"]), np.full(n, m["lat"]), pr[:, 1], pr[:, 0])
        d = d / 1000
        ta = t_imp + d / c
        qs = np.quantile(ta, [0.005, 0.025, 0.5, 0.975, 0.995])
        out[cid] = dict(samples_s=ta, range_km_q=np.quantile(d, [0.025, 0.5, 0.975]).round(1).tolist(),
                        backazimuth_q=np.quantile(np.mod(az, 360), [0.025, 0.5, 0.975]).round(2).tolist(),
                        arrival_q=[str(T_IMPACT_REF + pd.Timedelta(seconds=float(x))) for x in qs],
                        S_true=[T_IMPACT_REF + pd.Timedelta(seconds=float(qs[0] - PAD_S)),
                                T_IMPACT_REF + pd.Timedelta(seconds=float(qs[-1] + PAD_S))])
    return out


def main(summary_path, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = parse_meta()
    pred = predicted(meta, summary_path)
    rows, prereg = [], {"clock_conventions": {"A": "true = logger - e(t)", "B": "true = logger + e(t)"},
                        "curtin_control": {"logger": "3315", "utc": str(CURTIN_RCS_UTC), "tol_s": CURTIN_TOL_S},
                        "loggers": {}}
    for cid, d in SETS.items():
        m, p = meta[cid], pred[cid]
        files = sorted(glob.glob(str(IMOS / d / "*.DAT")))
        recs = []
        for fpath in files:
            fs, t0, n, filt = header(fpath)
            recs.append(dict(logger=cid, file=os.path.relpath(fpath, IMOS), sha256=sha256(fpath), fs=fs,
                             start_logger=t0, n_samples=n, dur_s=n / fs, filter0=filt))
        recs = pd.DataFrame(recs)
        e_mid = clock_err(m, recs.start_logger.iloc[len(recs) // 2])
        # S in logger time: union over conventions until the Curtin control resolves it
        s_true = p["S_true"]
        conv = {}
        for name, sign in [("A", +1), ("B", -1)]:  # logger = true + sign*e
            conv[name] = [s_true[0] + pd.Timedelta(seconds=sign * e_mid), s_true[1] + pd.Timedelta(seconds=sign * e_mid)]
        s_log = [min(conv["A"][0], conv["B"][0]), max(conv["A"][1], conv["B"][1])]
        end = recs.start_logger + pd.to_timedelta(recs.dur_s, unit="s")
        in_s = (end > s_log[0]) & (recs.start_logger < s_log[1])
        guard = (end > s_log[0] - pd.Timedelta(seconds=GUARD_S)) & (recs.start_logger < s_log[1] + pd.Timedelta(seconds=GUARD_S))
        in_b = (recs.start_logger >= s_log[0] - pd.Timedelta(hours=BG_H)) & (recs.start_logger <= s_log[1] + pd.Timedelta(hours=BG_H)) & ~guard
        recs["role"] = np.where(in_s, "S", np.where(in_b, "B", "other"))
        cov = {}
        for name, sign in [("A", +1), ("B", -1)]:
            ta = np.array([(T_IMPACT_REF - pd.Timestamp("2014-03-08", tz="UTC")).total_seconds()]) + p["samples_s"] + sign * e_mid
            st = (recs.start_logger - pd.Timestamp("2014-03-08", tz="UTC")).dt.total_seconds().values
            inside = np.zeros(len(ta), bool)
            for a, b in zip(st, st + recs.dur_s.values):
                inside |= (ta >= a) & (ta <= b)
            cov[name] = round(float(inside.mean()), 4)
        prereg["loggers"][cid] = dict(
            set_details=m["set_details"], lat=round(m["lat"], 6), lon=round(m["lon"], 6), sens_db=m["sens_db"],
            cal_file=m["cal_file"], clock_err_s_on_8_March=round(e_mid, 2), n_files=len(recs),
            span_logger=[str(recs.start_logger.min()), str(end.max())], range_km_q=p["range_km_q"],
            backazimuth_q=p["backazimuth_q"], arrival_true_q=p["arrival_q"],
            S_true=[str(x) for x in s_true], S_logger_union=[str(x) for x in s_log],
            S_logger_by_convention={k: [str(x) for x in v] for k, v in conv.items()},
            coverage_by_convention=cov, n_S=int(in_s.sum()), n_B=int(in_b.sum()),
            B_hours_before_S=round(float((s_log[0] - recs.start_logger[in_b].min()).total_seconds() / 3600), 2) if in_b.any() else None,
            B_hours_after_S=round(float((recs.start_logger[in_b].max() - s_log[1]).total_seconds() / 3600), 2) if in_b.any() else None,
            path_flag="near North West Cape / Exmouth Plateau; blockage unassessed" if cid == "3250" else "blockage unassessed")
        rows.append(recs)
    cal = []
    for cd in CAL_DIRS:
        for fpath in sorted(glob.glob(str(IMOS / cd / "*.DAT"))):
            fs, t0, n, filt = header(fpath)
            cal.append(dict(file=os.path.relpath(fpath, IMOS), sha256=sha256(fpath), start=str(t0), n_samples=n, filter0=filt))
    prereg["calibration_files"] = cal
    allr = pd.concat(rows)
    allr.to_csv(out_dir / "recordings.csv", index=False)
    (out_dir / "preregistration.json").write_text(json.dumps(prereg, indent=1, default=str))
    for cid, v in prereg["loggers"].items():
        print(cid, v["arrival_true_q"][2][11:19], v["S_logger_union"][0][11:19], v["S_logger_union"][1][11:19],
              v["coverage_by_convention"], v["n_S"], v["n_B"], v["B_hours_before_S"], v["B_hours_after_S"],
              v["range_km_q"], v["backazimuth_q"], v["clock_err_s_on_8_March"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
