"""Boeing engineering-simulator end-of-flight cases (ten, via ATSB and Iannello 2018) as a fit dataset.

    python3 sim/boeing_cases.py <zip> <out.npz>

The zip is `ISO Sept 28 Status/inputs/end-of-flight/2018-08-19-eof-sims.zip` (sha256 e400ac73...d111db, checked
here). Each case is a 1 Hz table of time (s), X and Y (NM) and altitude (ft). Pete ruled on 9 Oct 2026 that the
full traces may be fitted; they are still not redistributed, so the output belongs under engine/runs (ignored).

Per case, besides the raw columns, derived series from a Savitzky-Golay smoother (window 21 s, cubic):
ground speed and track from X/Y, turn rate, the coordinated-turn bank tan(phi) = V psi_dot / g (exact only for a
coordinated turn in still air; the simulator has no wind stated), vertical speed and vertical acceleration.
The altitude quantisation step is measured and stored, because it sets the altitude noise floor of the fit.
"""
import hashlib, io, json, sys, zipfile
import numpy as np
from scipy.signal import savgol_filter

SHA = "e400ac73478dff8698cd344a69d7969804f6adb0eb2121d5cacd3b58d63111db"
G, NM, FT = 9.80665, 1852.0, 0.3048


def derive(t, x, y, h, win=21):
    xs, ys, hs = (savgol_filter(v, win, 3) for v in (x, y, h))
    dt = np.gradient(t)
    vx, vy = (savgol_filter(v, win, 3, deriv=1) / dt * NM for v in (x, y))
    gs = np.hypot(vx, vy); trk = np.degrees(np.arctan2(vx, vy)) % 360.0
    turn = savgol_filter(np.unwrap(np.radians(trk)), win, 3, deriv=1) / dt
    bank = np.degrees(np.arctan(gs * turn / G))
    vs = savgol_filter(h, win, 3, deriv=1) / dt * FT
    az = savgol_filter(h, win, 3, deriv=2) / dt ** 2 * FT
    return dict(gs_mps=gs, track_deg=trk, turn_rate_dps=np.degrees(turn), bank_coord_deg=bank, vs_mps=vs, vacc_mps2=az)


def main():
    zp, out = sys.argv[1], sys.argv[2]
    raw = open(zp, "rb").read(); assert hashlib.sha256(raw).hexdigest() == SHA, "zip checksum mismatch"
    z = zipfile.ZipFile(io.BytesIO(raw)); arrays, meta = {}, {}
    for name in sorted(n for n in z.namelist() if n.endswith(".csv")):
        case = name.rsplit("/", 1)[-1][:-4].replace("Case ", "case")
        a = np.genfromtxt(io.BytesIO(z.read(name)), delimiter=",", skip_header=1)
        t, x, y, h = a.T
        assert np.allclose(np.diff(t), 1.0), case
        d = derive(t, x, y, h)
        steps = np.unique(np.abs(np.diff(h))); steps = steps[steps > 0]
        for k, v in dict(t_s=t, x_nm=x, y_nm=y, alt_ft=h, **d).items():
            arrays[f"{case}/{k}"] = v
        meta[case] = dict(n=len(t), duration_s=float(t[-1]), alt0_ft=float(h[0]), alt_end_ft=float(h[-1]),
                          gs0_kt=float(d["gs_mps"][15] / NM * 3600), track0_deg=float(d["track_deg"][15]),
                          alt_quantum_ft=float(steps.min()) if len(steps) else None,
                          range_nm=float(np.hypot(x[-1] - x[0], y[-1] - y[0])),
                          path_nm=float(np.sum(np.hypot(np.diff(x), np.diff(y)))))
    np.savez_compressed(out, **arrays)
    open(out.replace(".npz", ".json"), "w").write(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=0))


if __name__ == "__main__":
    main()
