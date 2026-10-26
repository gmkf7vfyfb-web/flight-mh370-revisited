"""Declared simple path model for the near-field ARRIVAL STRUCTURE (not used for level): Bellhop (Acoustics Toolbox
at_2026_8_29 build, same as the module's KRAKEN) eigenray arrivals on the GEBCO 2026 track of each near-field path
(range-dependent bathymetry, 1-km decimation), one range-independent sound-speed profile (median of the WOA23 B5C2 April
nodes along the path, extended below the deepest WOA level by the last 200-m gradient), module 'hard' bottom halfspace
(cp 1650, rho 1.9, 0.5 dB/lambda, evaluated at 10 Hz), vacuum surface. Source P (40.4496 N 142.9237 E), z_s 2/10/30 m,
receiver 2 m above the seabed.
Impulse response: arrivals in 0.1-s bins, coherent sum inside a bin averaged over 5-40 Hz with weight f^-1.7 (received
spectrum), so surface-image pairs cancel as a dipole; output energy vs time.
Usage: python nearfield_arrivals.py <tl_out_dir_with_paths> <at_bin> <out_dir>
"""
import sys, os, pathlib, subprocess, json
import numpy as np, pandas as pd
tld, at_bin, out = pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
STA = ["DSOH", "KSP1", "KSP2", "KSP3"]; ZS = [2.0, 10.0, 30.0]; FREQ = 10.0
def ssp_profile(ssp, zmax):
    g = ssp.dropna(subset=["c_m_s"]).groupby("depth_m").c_m_s.median()
    z, c = g.index.values.astype(float), g.values
    if z[-1] > zmax:                                               # clip at the deepest point of the track, interpolate there
        cz = float(np.interp(zmax, z, c)); k = z < zmax; z = np.append(z[k], zmax); c = np.append(c[k], cz); return z, c
    if z[-1] < zmax:
        k = z >= z[-1] - 200.0; gr = np.polyfit(z[k], c[k], 1)[0] if k.sum() >= 2 else 0.0165
        z = np.append(z, zmax); c = np.append(c, c[-1] + gr * (zmax - z[-2]))
    return z, c
def read_arr(p):
    tok = open(p).read().replace("'", " ").split()
    i = 0; dim = tok[i]; i += 1; f = float(tok[i]); i += 1
    nsd = int(tok[i]); i += 1; sd = [float(v) for v in tok[i:i + nsd]]; i += nsd
    nrd = int(tok[i]); i += 1; i += nrd
    nr = int(tok[i]); i += 1; i += nr
    res = {}
    for s in sd:
        i += 1                                                     # Narrmx
        na = int(tok[i]); i += 1
        a = np.array(tok[i:i + 8 * na], float).reshape(na, 8) if na else np.zeros((0, 8)); i += 8 * na
        res[s] = a
    return res
rows = []; meta = {}
for st in STA:
    b = pd.read_csv(tld / "paths" / f"bathy_f35aP-{st}-hard.csv"); s = pd.read_csv(tld / "paths" / f"ssp_f35aP-{st}-hard.csv")
    L = float(b.range_km.iloc[-1]); rk = np.arange(0.0, L, 1.0); rk = np.append(rk, L); dep = -np.interp(rk, b.range_km, b.elevation_m)
    rd = float(dep[-1] - 2.0); zmax = float(dep.max() + 50.0); z, c = ssp_profile(s, zmax)
    wd = out / "work" / st; wd.mkdir(parents=True, exist_ok=True)
    with open(wd / "a.bty", "w") as fh:
        fh.write("'L'\n%d\n" % len(rk)); fh.writelines(f"{r:.4f} {d:.1f}\n" for r, d in zip(rk, dep))
    env = ["'F35A near field'", f"{FREQ}", "1", "'CVW'", f"0 0.0 {zmax:.1f}"] + [f"{zz:.1f} {cc:.3f} /" for zz, cc in zip(z, c)]
    env += ["'A*' 0.0", f"{zmax:.1f} 1650.0 0.0 1.9 0.5 /", f"{len(ZS)}", " ".join(f"{v:.1f}" for v in ZS) + " /", "1", f"{rd:.1f} /", "1", f"{L:.4f} /",
            "'A'", "6001", "-89.0 89.0 /", f"0.0 {zmax + 100:.1f} {L + 5:.1f}"]
    open(wd / "a.env", "w").write("\n".join(env) + "\n")
    p = subprocess.run([f"{at_bin}/Bellhop/bellhop.exe", "a"], cwd=wd, capture_output=True, text=True)
    if p.returncode or not (wd / "a.arr").exists():
        print(st, "bellhop failed", p.returncode, p.stdout[-300:], (wd / "a.prt").read_text()[-600:] if (wd / "a.prt").exists() else ""); continue
    A = read_arr(wd / "a.arr")
    meta[st] = dict(range_km=L, rcv_depth_m=rd, c_surface=float(c[0]), c_min=float(c.min()), z_cmin=float(z[np.argmin(c)]), c_bottom=float(np.interp(rd, z, c)),
                    n_arrivals={f"{k:g}": int(len(v)) for k, v in A.items()})
    for zs, a in A.items():
        for r in a:
            rows.append(dict(station=st, src_depth_m=zs, amp=r[0], phase_deg=r[1], delay_s=r[2], src_angle_deg=r[4], rcv_angle_deg=r[5], n_top=int(r[6]), n_bot=int(r[7])))
D = pd.DataFrame(rows); D.to_csv(out / "nearfield_arrivals.csv", index=False)
# impulse-response energy, band-averaged coherent sum in 0.1-s bins
fz = np.arange(5.0, 40.01, 0.25); wf = fz ** -1.7; wf /= wf.sum(); ir = []
for (st, zs), g in D.groupby(["station", "src_depth_m"]):
    t0 = g.delay_s.min(); tb = np.floor((g.delay_s.values - t0) / 0.1).astype(int)
    ph = np.deg2rad(g.phase_deg.values); amp = g.amp.values; tau = g.delay_s.values
    for k in np.unique(tb):
        m = tb == k
        e = np.sum(wf * np.abs((amp[m][None, :] * np.exp(1j * (ph[m][None, :] - 2 * np.pi * fz[:, None] * (tau[m][None, :] - t0)))).sum(1)) ** 2)
        ir.append(dict(station=st, src_depth_m=zs, t_rel_first_s=(k + 0.5) * 0.1, energy=float(e), n_rays=int(m.sum())))
IR = pd.DataFrame(ir); IR.to_csv(out / "nearfield_impulse_response.csv", index=False)
for (st, zs), g in IR.groupby(["station", "src_depth_m"]):
    c = np.cumsum(g.energy.values) / g.energy.sum(); t = g.t_rel_first_s.values
    print(st, zs, "rays", int(g.n_rays.sum()), "5-95 % span s", round(np.interp(.95, c, t) - np.interp(.05, c, t), 2), "t50", round(np.interp(.5, c, t), 2), "last ray s", round(t.max(), 1))
json.dump(meta, open(out / "nearfield_arrivals_meta.json", "w"), indent=1); print(json.dumps(meta))
