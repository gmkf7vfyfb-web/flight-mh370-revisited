"""Sensitivity of tau90 to the lower edge of the a_bar range (source check, NACA Report 1347).

Headline method 1: a_bar ~ U[0.75, 3.0] g (unchanged; the range is not changed without Pete's ruling).
Sensitivity: a_bar ~ U[0.45, 3.0] g, the lower edge being the smallest recomputed average deceleration of the
standard-configuration calm-water transport runs in Report 1347 (0.45 g, damaged model; undamaged 0.47 g).
Same uniform draw u per row (common random numbers): a_bar = (lo + (3.0 - lo) u) g.
Usage: python abar_sensitivity.py HANDOFF_DIR SIDECAR_DIR OUT_CSV
"""
import sys
import numpy as np, pandas as pd
import settling_energy_transfer_m1 as m1

LO_SENS_G = 0.45


def main(hdir, sdir, out):
    rows = []
    for route in ("df", "wp"):
        h = np.load(f"{hdir}/eof-final-handoff-{route}.npz"); s = np.load(f"{sdir}/settling-energy-transfer-m1-{route}.npz")
        u = (s["a_bar_mps2"] / m1.G0 - m1.A_BAR_G[0]) / (m1.A_BAR_G[1] - m1.A_BAR_G[0])   # recover u exactly from the stored draw
        a2 = (LO_SENS_G + (m1.A_BAR_G[1] - LO_SENS_G) * u) * m1.G0
        v = s["contact_speed_mps"].astype(float); th = np.abs(h["flight_path_angle_deg_descent_positive"].astype(float))
        m = h["mass_kg"].astype(float)
        r2 = m1.method1(v, th, m, a2, s["l_eff_m"])
        fam = h["family_code"]
        for t in ("D7", "D9", "D10"):
            lw = h[f"log_weight_{t}"].astype(float); w = np.exp(lw - lw.max()); w /= w.sum()
            for fname, sel in (("all", np.ones(len(w), bool)), ("no pilot", fam == 1), ("piloted", fam == 2), ("planned descent", fam == 3)):
                if not sel.any():
                    continue
                q1 = m1.weighted_quantiles(s["energy_transfer_tau90_s"][sel], w[sel], [.05, .5, .95])
                q2 = m1.weighted_quantiles(r2["tau90"][sel], w[sel], [.05, .5, .95])
                rows.append(dict(route=route, treatment=t, family=fname,
                                 tau90_q05_headline=q1[0], tau90_q50_headline=q1[1], tau90_q95_headline=q1[2],
                                 tau90_q05_abar045=q2[0], tau90_q50_abar045=q2[1], tau90_q95_abar045=q2[2]))
    pd.DataFrame(rows).to_csv(out, index=False, float_format="%.5g")


if __name__ == "__main__":
    main(*sys.argv[1:4])
