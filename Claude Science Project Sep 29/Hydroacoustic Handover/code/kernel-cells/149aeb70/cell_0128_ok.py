import numpy as np, pandas as pd
PC = (-31.8422, 115.0137)   # Perth Canyon 3376
def crossing(brg, rng_max=2600):
    rr = np.arange(50, rng_max, 0.5)
    la_, lo_ = fwd(*H01W, brg, rr)
    resid = lo_ - np.polyval(cf, la_)
    i = np.where(np.diff(np.sign(resid)) != 0)[0]
    if len(i) == 0: return None
    k = i[0]; return la_[k], lo_[k], rr[k]
C_NOM, SIG_C = 1.48, 0.015      # km/s, stated 1% group-speed uncertainty
PICK = 5.0                      # s, pick/digitisation uncertainty at H01W
rows = []
for d in (-3.3, -1.0, 0.0, 1.0, 3.3):
    la_, lo_, dCL = crossing(306.18 + d)
    dDG = float(gc_km(la_, lo_, *RX["H08S Diego Garcia S"])); dPC = float(gc_km(la_, lo_, *PC))
    rows.append(dict(dbrg=d, lat=round(la_,2), lon=round(lo_,2), d_CL=round(dCL),
                     d_DG=round(dDG), d_PC=round(dPC),
                     dt_DG=round((dDG-dCL)/C_NOM), dt_PC=round((dPC-dCL)/C_NOM)))
G = pd.DataFrame(rows); print(G.to_string(index=False))
base = G[G.dbrg == 0].iloc[0]
for lbl, d in (("±1.0° bearing", 1.0), ("±3.3° bearing", 3.3)):
    sub = G[G.dbrg.abs() == d]
    sg_dg = (sub.dt_DG.max() - sub.dt_DG.min())/2; sg_pc = (sub.dt_PC.max() - sub.dt_PC.min())/2
    sc_dg = abs(base.dt_DG)*SIG_C/C_NOM; sc_pc = abs(base.dt_PC)*SIG_C/C_NOM
    z_dg = float(np.hypot(np.hypot(sg_dg, sc_dg), PICK)); z_pc = float(np.hypot(np.hypot(sg_pc, sc_pc), PICK))
    print(f"\n{lbl}: DG  geometry ±{sg_dg:.0f} s, speed ±{sc_dg:.0f} s, pick ±{PICK:.0f} s  ->  combined ±{z_dg:.0f} s")
    print(f"{' '*len(lbl)}  PC  geometry ±{sg_pc:.0f} s, speed ±{sc_pc:.0f} s, pick ±{PICK:.0f} s  ->  combined ±{z_pc:.0f} s")
    for nm, tCL in (("text 00:52:03", 3123), ("caption 00:54:30", 3270)):
        for rx, dtv, z in (("DG", base.dt_DG, z_dg), ("Perth Canyon", base.dt_PC, z_pc)):
            a = tCL + dtv
            fmt = lambda t: f"{int(t//3600):02d}:{int(t%3600//60):02d}:{int(round(t%60)):02d}"
            print(f"   {nm:17s} {rx:12s} arrival {fmt(a)}  window {fmt(a-2*z)} to {fmt(a+2*z)}  (2 sigma, ±{2*z:.0f} s)")
