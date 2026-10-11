"""Export the Pléiades + all-four-COSMO joint log-likelihood with CORRELATED transport errors (rho) on the module's surface grid,
so that the correlated case is a pure re-weighting of the same impacts (architecture, 10 Oct 19:50 -0600, item 2).

ln L(s | P + C4, H; rho) per ocean model, with the hook's OU variances, the hook's object/contact weights (rating-5 objects, 6 clusters,
equal weights; four contacts equal; dawn/dusk passes equal) and a bivariate normal per component between each object and each contact
(windages independent). At rho = 0 this is the hook's product L_P x L_C4 (checked here against the exported surfaces).
The constant factor A_scene of the hook is not included (it cancels in every conditional); the check is therefore on the ln ratio sd.

Writes <out>/joint-surface-rho<r>.{f32,toml}: [ocean-model][lat][lon] float32, NaN = not computed (land / no afloat track).

    python rho_surface.py <surface dir with likelihood-surface.toml and release grids> <out dir> [rho ...]
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit_closeup as ac  # noqa: E402
import branch_eof289 as b  # noqa: E402


def endpoints(a, m, ti, LON, LAT):
    x = (LON - m["lon0"]) / m["step_deg"]; y = (LAT - m["lat0"]) / m["step_deg"]
    i = np.floor(x).astype(int); j = np.floor(y).astype(int)
    ok = (i >= 0) & (j >= 0) & (i + 1 < a.shape[1]) & (j + 1 < a.shape[0])
    i = np.clip(i, 0, a.shape[1] - 2); j = np.clip(j, 0, a.shape[0] - 2); fx = x - i; fy = y - j
    out = np.zeros(LAT.shape + (a.shape[2], 2))
    for dj, wy in ((0, 1 - fy), (1, fy)):
        for di, wx in ((0, 1 - fx), (1, fx)):
            out += (wx * wy)[..., None, None] * a[j + dj, i + di, :, ti, :]
    out[~ok] = np.nan
    return out


def main(surf, out, rhos):
    surf, out = Path(surf), Path(out); out.mkdir(parents=True, exist_ok=True)
    M = HERE.parent
    mp = b.read_toml_meta(surf / "likelihood-surface.toml")
    lat = mp["lat0"] + mp["step_deg"] * np.arange(int(mp["nlat"])); lon = mp["lon0"] + mp["step_deg"] * np.arange(int(mp["nlon"]))
    tabs = [ac.load_table(surf, n) for n in ac.TABLES]
    tm = [b.read_toml_meta(surf / f"{n}.toml")["ocean_model"] for n in ac.TABLES]
    assert tm == ac.MODELS == mp["ocean_model"], (tm, mp["ocean_model"])
    OUTS = tabs[0][0]["out_unix_s"]
    T5 = pd.read_csv(M / "data/targets-3km.csv").query("arm == 'rating5'")
    Cc = pd.read_csv(M / "data/cosmo-contacts.csv")
    _, models, P, Cm = b.load_fields(surf)
    ref = {mi: P[mi, 0, 0] + Cm[mi, 1] for mi in (0, 1)}            # hook: ln L_P + ln L_C4 (pass-marginal)
    CH = 25
    for rho in rhos:
        t0 = time.time()
        J = np.full((2, len(lat), len(lon)), np.nan, np.float32)
        for mi in (0, 1):
            m, a = tabs[mi]
            for r0 in range(0, len(lat), CH):
                la = lat[r0:r0 + CH]
                if not np.isfinite(ref[mi][r0:r0 + CH]).any():
                    continue
                LAT, LON = np.meshgrid(la, lon, indexing="ij")
                EP = {ti: endpoints(a, m, ti, LON, LAT) for ti in range(4)}
                tot = 0.0
                for ps in (0, 1):
                    vC = ac.ou_var_km2(mi, OUTS[ps] - ac.T_IMP)
                    RC = [ac.resid(EP[ps], (r.longitude, r.latitude)) for _, r in Cc.iterrows()]
                    for _, r in T5.iterrows():
                        ti = 2 if ac.SCENE[r.scene] == OUTS[2] else 3
                        vP = ac.ou_var_km2(mi, ac.SCENE[r.scene] - ac.T_IMP)
                        rP = ac.resid(EP[ti], (r.lon, r.lat))
                        lpP = -0.5 * np.sum(rP ** 2 / vP, -1) - np.log(2 * np.pi * np.sqrt(vP.prod()))
                        bb = rho * np.sqrt(vC / vP); vc = vC * (1 - rho ** 2)
                        for rC in RC:
                            dif = rC[..., None, :, :] - bb * rP[..., :, None, :]
                            lpC = -0.5 * np.sum(dif ** 2 / vc, -1) - np.log(2 * np.pi * np.sqrt(vc.prod()))
                            tot = tot + r.w_equal * 0.25 * 0.5 * np.mean(np.exp(lpP[..., :, None] + lpC), axis=(-2, -1))
                with np.errstate(divide="ignore"):
                    v = np.log(tot)
                v = np.where(np.isfinite(ref[mi][r0:r0 + CH]) & (tot > 0), v, np.nan)
                J[mi, r0:r0 + CH] = v
        chk = {}
        if rho == 0.0:
            for mi in (0, 1):
                ok = np.isfinite(J[mi]) & np.isfinite(ref[mi]) & (ref[mi] > np.nanmax(ref[mi]) - 30)
                d = J[mi][ok].astype(float) - ref[mi][ok]
                chk[models[mi]] = dict(n=int(ok.sum()), lnratio_mean=float(d.mean()), lnratio_sd=float(d.std()))
        tag = f"{rho:g}"
        J.tofile(out / f"joint-surface-rho{tag}.f32")
        (out / f"joint-surface-rho{tag}.toml").write_text(
            f'layout = "[ocean-model][lat][lon] ln L(s | P + C4, H; rho) little-endian float32, without the A_scene constant"\n'
            f"lon0 = {mp['lon0']}\nlat0 = {mp['lat0']}\nstep_deg = {mp['step_deg']}\nnlon = {int(mp['nlon'])}\nnlat = {int(mp['nlat'])}\n"
            f"rho = {rho}\nocean_model = {json.dumps(models)}\nnot_computed = {int((~np.isfinite(J)).sum())}\n"
            f'params = "prepare/rho_surface.py; rating-5 objects, 6 clusters, equal weights; all four COSMO contacts, passes equal; OU variances of run.toml"\n'
            + (f"rho0_check = {json.dumps(json.dumps(chk))}\n" if chk else ""))
        print(f"rho {rho}: {time.time() - t0:.0f} s", chk, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], [float(x) for x in sys.argv[3:]] or [0.0, 0.25, 0.5])
