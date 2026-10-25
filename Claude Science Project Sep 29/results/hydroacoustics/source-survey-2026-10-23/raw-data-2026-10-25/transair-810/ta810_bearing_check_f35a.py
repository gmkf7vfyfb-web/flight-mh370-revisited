"""Calibration check of the C3 coherence + plane-wave bearing estimator on the F-35A raw H11 record (2019-04-09):
estimated back-azimuth at the C3 maximum within +/-20 s of the arrival peak vs the geodesic back-azimuth to the module
working point (40.64 N 142.96 E) and to Kadri's S1 point (40 30'10\"N 142 04'37\"E)."""
import sys, pathlib, numpy as np
from obspy import read, read_inventory, UTCDateTime
from pyproj import Geod
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import ta810_common as T
WS = T.WS; G = Geod(ellps="WGS84"); st0 = read(str(WS / "inputs/f35a_H11_raw.mseed")); inv = read_inventory(str(WS / "inputs/f35a_H11_resp.xml"))
GEO = T.element_geometry(inv); PK = {"H11N": UTCDateTime("2019-04-09T11:03:05"), "H11S": UTCDateTime("2019-04-09T11:04:07")}
for tri, els in T.TRIADS.items():
    files = {}
    for e in els:
        fn = WS / f"data/_f35_{e}.mseed"; st0.select(station=e).write(str(fn), format="MSEED"); files[e] = str(fn)
    t0, X, M = T.triad_block(files, inv); t, c3, lag = T.c3_triad(X, GEO[tri]["xy"])
    m = np.abs(t - (PK[tri] - t0)) <= 20; j = np.where(m)[0][np.argmax(c3[m])]
    baz, v = T.plane_fit(lag[:, j], GEO[tri]["xy"])
    exp1 = G.inv(GEO[tri]["lon"], GEO[tri]["lat"], 142.96, 40.64)[0] % 360; exp2 = G.inv(GEO[tri]["lon"], GEO[tri]["lat"], 142 + 4 / 60 + 37 / 3600, 40 + 30 / 60 + 10 / 3600)[0] % 360
    bz = [T.plane_fit(lag[:, k], GEO[tri]["xy"])[0] for k in np.where(m & (c3 > 0.8 * c3[j]))[0]]
    print(f"{tri}: C3 max {c3[j]:.2f} at {(t0 + t[j]).strftime('%H:%M:%S')}; estimated baz {baz:.2f} deg, v_app {v:.3f} km/s; frames >= 0.8 max: baz {np.min(bz):.2f}-{np.max(bz):.2f}; expected {exp1:.2f} (module point), {exp2:.2f} (Kadri S1 point)")
    for f in files.values(): pathlib.Path(f).unlink()
