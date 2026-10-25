"""F-35A raw-record templates (pre-registration v986504a4 s3, s6): per triad, envelope template (mean of the three
element 10 Hz envelopes, [peak - 35 s, peak + 15 s], zero-mean, unit energy) and waveform template (element 1,
5-40 Hz, 100 Hz, same cut, 2 s cosine tapers). Check values against OB01-OB06 (1-s RMS peak, time, exposure)."""
import json, sys, pathlib
import numpy as np
from obspy import read, read_inventory
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import ta810_common as T
WS = T.WS
st0 = read(str(WS / "inputs/f35a_H11_raw.mseed")); inv = read_inventory(str(WS / "inputs/f35a_H11_resp.xml"))
out = {}; chk = []
for tri, els in T.TRIADS.items():
    X = {}; ts = {}
    for e in els:
        st = st0.select(station=e).copy(); fn = WS / f"data/_tmp_{e}.mseed"; st.write(str(fn), format="MSEED")
        t0, x, g = T.process_file(str(fn), inv); fn.unlink(); X[e] = x; ts[e] = t0
    t00 = max(ts.values()); n = min(len(x) - int(round((t00 - ts[e]) * T.FS)) for e, x in X.items())
    X = {e: x[int(round((t00 - ts[e]) * T.FS)): int(round((t00 - ts[e]) * T.FS)) + n] for e, x in X.items()}
    for e, x in X.items():
        ms = np.convolve(np.asarray(x, float) ** 2, np.ones(T.FS) / T.FS, "same"); k = int(np.argmax(ms))
        noise = np.median(ms); a, b = k - 15 * T.FS, k + 15 * T.FS
        se = float(np.sum(np.asarray(x[a:b], float) ** 2) / T.FS - noise * 30)
        chk.append(dict(element=e, peak_utc=str(t00 + k / T.FS), rms_peak_pa=float(np.sqrt(ms[k])), median_rms_pa=float(np.sqrt(noise)),
                        inst_peak_pa=float(np.max(np.abs(x[a:b]))), se_5_40_pa2s=se))
    env = T.env_triad(X)
    e1 = np.convolve(env, np.ones(10) / 10, "same"); pk = int(np.argmax(e1))
    h = env[pk - 350: pk + 150].astype(float); h = h - h.mean(); h /= np.sqrt(np.sum(h ** 2))
    x1 = np.asarray(X[els[0]], float); ms = np.convolve(x1 ** 2, np.ones(T.FS) / T.FS, "same"); k1 = int(np.argmax(ms))
    w = x1[k1 - 35 * T.FS: k1 + 15 * T.FS].copy(); nt = 2 * T.FS; tap = 0.5 * (1 - np.cos(np.pi * np.arange(nt) / nt))
    w[:nt] *= tap; w[-nt:] *= tap[::-1]
    wm = np.convolve(w ** 2, np.ones(T.FS) / T.FS, "same")
    noise_ms = float(np.median(ms))
    out[tri] = dict(env=h, wave=w.astype(np.float32), wave_rms_peak=float(np.sqrt(wm.max())), wave_inst_peak=float(np.abs(w).max()),
                    wave_se_pm15=float(np.sum(w[(35 - 15) * T.FS:(35 + 15) * T.FS] ** 2) / T.FS - noise_ms * 30),
                    wave_noise_ms=noise_ms, env_peak_utc=str(t00 + pk / 10.0))
np.savez(WS / "out/f35a_templates.npz", **{f"{k}_{tri}": v[k] for tri, v in out.items() for k in ("env", "wave")})
meta = {tri: {k: v for k, v in d.items() if k not in ("env", "wave")} for tri, d in out.items()}
json.dump(dict(meta=meta, check=chk), open(WS / "out/f35a_templates.json", "w"), indent=1)
print(json.dumps(meta, indent=1)); import pandas as pd; print(pd.DataFrame(chk).round(3).to_string())
