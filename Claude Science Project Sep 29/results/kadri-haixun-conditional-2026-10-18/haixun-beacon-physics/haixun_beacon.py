"""Haixun 01 37.5 kHz contact (4-5 Apr 2014): beacon physics, geometry test and B_H.

Pre-registration Q5 (results/kadri-haixun-conditional-2026-10-18/preregistration.md).
Inputs (all in ./src): WOA23 1-deg decav T/S, March monthly (0-1500 m) and Jan-Mar
seasonal (0-5500 m), cells 25.5 S and 26.5 S at 101.5 E; GEBCO 2020 depth via
OpenTopoData; ERA5 10-m wind via Open-Meteo archive. No run J weights are used:
B_H is a likelihood ratio (prior-free).

Outputs (in OUT): profile.csv, tl_vs_offset.csv, pdet_vs_offset.csv, geometry_test.json,
bh_summary.json, and three figures.
"""
import json, re, os, sys
import numpy as np
from scipy.stats import norm

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261018)
F_KHZ = 37.5

# ---------------------------------------------------------------- environment
def read_woa(path, var):
    txt = open(path).read()
    dep = txt.split("\ndepth[")[1].split("\n", 1)[1].split("\n\n")[0]
    depth = np.array([float(v) for v in dep.replace("\n", "").split(",") if v.strip()])
    vals = {}
    for m in re.finditer(r"^\[0\]\[(\d+)\]\[(\d)\], ([-0-9.eE+]+)", txt, flags=re.M):
        vals[(int(m.group(1)), int(m.group(2)))] = float(m.group(3))
    nd = len(depth)
    a = np.full((nd, 2), np.nan)
    for (k, j), v in vals.items():
        a[k, j] = v if abs(v) < 1e30 else np.nan
    return depth, np.nanmean(a, axis=1)   # mean of 26.5 S and 25.5 S cells

d03, t03 = read_woa("src/woa23_t03.asc", "t"); _, s03 = read_woa("src/woa23_s03.asc", "s")
d13, t13 = read_woa("src/woa23_t13.asc", "t"); _, s13 = read_woa("src/woa23_s13.asc", "s")
# March monthly to 1500 m, Jan-Mar seasonal below
deep = d13 > d03.max()
zp = np.concatenate([d03, d13[deep]]); Tp = np.concatenate([t03, t13[deep]]); Sp = np.concatenate([s03, s13[deep]])
ok = np.isfinite(Tp) & np.isfinite(Sp)
zp, Tp, Sp = zp[ok], Tp[ok], Sp[ok]

gebco = json.load(open("src/gebco_otd.json"))["results"]
Z_BED = -gebco[0]["elevation"]           # 25.975 S 101.461 E
Z_BED_CROSS = -gebco[1]["elevation"]     # arc crossing 25.732 S 101.369 E
if zp.max() < Z_BED:   # extend with last value (adiabatic change negligible over the gap)
    zp = np.append(zp, Z_BED); Tp = np.append(Tp, Tp[-1]); Sp = np.append(Sp, Sp[-1])

def mackenzie(T, S, z):
    return (1448.96 + 4.591*T - 5.304e-2*T**2 + 2.374e-4*T**3 + 1.340*(S-35) + 1.630e-2*z
            + 1.675e-7*z**2 - 1.025e-2*T*(S-35) - 7.139e-13*T*z**3)

def francois_garrison(f, T, S, z, pH=8.0):
    """dB/km, Francois & Garrison (1982b), f in kHz, z in m."""
    c = 1412 + 3.21*T + 1.19*S + 0.0167*z
    A1 = 8.86/c * 10**(0.78*pH - 5); P1 = 1.0; f1 = 2.8*np.sqrt(S/35)*10**(4 - 1245/(T+273))
    A2 = 21.44*S/c*(1 + 0.025*T); P2 = 1 - 1.37e-4*z + 6.2e-9*z**2
    f2 = 8.17*10**(8 - 1990/(T+273))/(1 + 0.0018*(S-35))
    P3 = 1 - 3.83e-5*z + 4.9e-10*z**2
    A3 = np.where(T <= 20, 4.937e-4 - 2.59e-5*T + 9.11e-7*T**2 - 1.50e-8*T**3,
                  3.964e-4 - 1.146e-5*T + 1.45e-7*T**2 - 6.5e-10*T**3)
    return (A1*P1*f1*f**2/(f1**2+f**2) + A2*P2*f2*f**2/(f2**2+f**2) + A3*P3*f**2)

zg = np.arange(0, Z_BED + 0.5, 1.0)
Tg = np.interp(zg, zp, Tp); Sg = np.interp(zg, zp, Sp)
cg = mackenzie(Tg, Sg, zg); ag = francois_garrison(F_KHZ, Tg, Sg, zg)   # dB/km
np.savetxt(f"{OUT}/profile.csv", np.c_[zp, Tp, Sp, mackenzie(Tp, Sp, zp), francois_garrison(F_KHZ, Tp, Sp, zp)],
           delimiter=",", header="depth_m,T_C,S_psu,c_mps,alpha37p5_dBkm", comments="", fmt="%.4f")

# ---------------------------------------------------------------- ray tracing (direct up-going path)
Z_RX = 2.0   # hydrophone on a ~2 m pole (press, grade C)
def trace(theta0_deg, zs=Z_BED, zr=Z_RX):
    """Ray from source at zs (seabed) upward, launch angle above horizontal. Returns x, s, absorption dB,
    or None if the ray turns before reaching zr."""
    i0, i1 = int(round(zr)), int(round(zs))
    c = cg[i0:i1+1]; a = ag[i0:i1+1]
    p = np.cos(np.radians(theta0_deg))/cg[i1]
    pc = p*c
    if np.any(pc >= 1): return None
    sq = np.sqrt(1 - pc**2)
    dz = 1.0
    x = np.trapezoid(pc/sq, dx=dz); s = np.trapezoid(1/sq, dx=dz); A = np.trapezoid(a/sq, dx=dz)/1000
    th_r = np.degrees(np.arccos(pc[0]))
    return x, s, A, th_r

thetas = np.concatenate([np.linspace(89.99, 20, 400), np.linspace(19.9, 0.5, 400)])
rays = []
for th in thetas:
    r = trace(th)
    if r is None: break
    rays.append((th,) + r)
rays = np.array(rays)    # theta0, x, s, A, theta_r
# geometric spreading by ray-tube: I/I0 = cos(th0) / (x * sin(th_r) * |dx/dth0|)
th0 = np.radians(rays[:, 0]); x = rays[:, 1]; thr = np.radians(rays[:, 4])
dxdth = np.gradient(x, th0)
with np.errstate(divide="ignore", invalid="ignore"):
    I = np.cos(th0)/(x*np.sin(thr)*np.abs(dxdth))
TLgeo = -10*np.log10(I)
TLgeo[0] = 20*np.log10(rays[0, 2])    # vertical ray: spherical
TL = TLgeo + rays[:, 3]
xmax_direct = x.max()
offs = np.arange(0, 10001, 50.0)
order = np.argsort(x)
TLx = np.interp(offs, x[order], TL[order]); Ax = np.interp(offs, x[order], rays[order, 3])
Sx = np.interp(offs, x[order], rays[order, 2]); TLsph = 20*np.log10(np.sqrt(offs**2 + (Z_BED-Z_RX)**2))
np.savetxt(f"{OUT}/tl_vs_offset.csv", np.c_[offs, Sx, TLx, Ax, TLsph], delimiter=",",
           header="offset_m,path_m,TL_dB,absorption_dB,TL_spherical_only_dB", comments="", fmt="%.3f")

def TL_of(offset_m):
    return np.interp(offset_m, offs, TLx)

# reference (near-surface warm water) absorption for the calibrations
alpha_surf = float(np.mean(ag[:200]))   # 0-200 m mean, dB/km
def TL_ref(R):  # spherical + near-surface absorption, horizontal path for a diver/boat test
    return 20*np.log10(R) + alpha_surf*R/1000

# ---------------------------------------------------------------- noise
def nl_wind(U):   # APL-UW TR9407 wind-generated noise spectrum level, dB re 1 uPa^2/Hz, f in kHz
    f = F_KHZ
    return 50 + 7.5*np.sqrt(U) - 40*np.log10(f + 0.4) + 20*np.log10(f)
NL_THERMAL = -15 + 20*np.log10(F_KHZ)
era = np.genfromtxt("src/era5_haixun_2014-04-03_06.csv", delimiter=",", names=True, dtype=None, encoding=None)
tt = np.array(era["time"], dtype="datetime64[h]"); U = era["wind_speed_10m"].astype(float)
win1 = (tt >= np.datetime64("2014-04-04T04")) & (tt <= np.datetime64("2014-04-04T12"))
win2 = (tt >= np.datetime64("2014-04-05T04")) & (tt <= np.datetime64("2014-04-05T12"))
U1, U2 = float(U[win1].mean()), float(U[win2].mean())
def psum(*db): return 10*np.log10(sum(10**(np.asarray(d)/10) for d in db))

# ---------------------------------------------------------------- source level vs day
T_IMMERSE = np.datetime64("2014-03-08T00:30")
def day_of(ts): return (np.datetime64(ts) - T_IMMERSE)/np.timedelta64(1, "h")/24
DAY1 = day_of("2014-04-04T08:34")   # 16:34 local (UTC+8, press grade C)
DAY2 = DAY1 + 1.0
def SL_spec(day): return 160.5 - 3.5*np.clip(day, 0, 40)/30   # linear between spec points

# ---------------------------------------------------------------- Monte Carlo of the sonar equation
N = 200_000
def lu(a, b, n): return np.exp(rng.uniform(np.log(a), np.log(b), n))
draw = {
    "dSL_unit": rng.uniform(-3, 2, N),
    "beam_loss": np.where(rng.random(N) < 0.2, rng.uniform(3, 15, N), 0.0),       # 80 % of sphere rated
    "shield_loss": np.where(rng.random(N) < 0.25, rng.uniform(0, 20, N), 0.0),    # partial burial / debris
    "w_point": rng.uniform(0.3, 0.8, N),
    "alpha_scale": rng.normal(1.0, 0.05, N),
    "sigma": rng.uniform(2, 5, N),
    "N_self": rng.uniform(20, 35, N),          # receiver/self noise, dB re 1 uPa^2/Hz equivalent
    "N_boat": rng.uniform(20, 40, N),          # rescue boat / mother ship at 37.5 kHz
    "DI": rng.uniform(13, 18, N),              # 25-30 deg conical beam
    "Beff": lu(100, 2000, N),                  # heterodyne + ear critical band .. 2 kHz receiver band
    "DT": rng.uniform(0, 10, N),
    "Rp_B": rng.uniform(2000, 3600, N),        # Benthos practical 2,000 m .. DK100 manual 3,600 m
    "Uref_B": rng.uniform(5, 8, N),
    "Rp_C": rng.uniform(4000, 5000, N),        # ATSB 'about 4,500 m in favourable conditions'
    "Uref_C": rng.uniform(2, 4, N),
    "dboat_BC": rng.uniform(0, 6, N),          # extra 'surface noise' at the site vs reference
    "P_tx": rng.uniform(0.7, 0.9, N),          # >=1 ULB transmitting at day 27-28 given wreck at site
}
good = rng.random(N) < draw["w_point"]
draw["point_loss"] = np.where(good, rng.uniform(0, 3, N), rng.uniform(10, 25, N))

def SE_offset(cal, offset_m, day, Uact, idx=slice(None)):
    d = {k: v[idx] for k, v in draw.items()}
    TLh = TL_of(offset_m) + (d["alpha_scale"] - 1)*np.interp(offset_m, offs, Ax)
    SL = SL_spec(day) + d["dSL_unit"]
    losses = d["beam_loss"] + d["shield_loss"] + d["point_loss"]
    if cal == "A":
        NL = psum(nl_wind(Uact), NL_THERMAL, d["N_self"], d["N_boat"])
        return SL - TLh - (NL + 10*np.log10(d["Beff"])) + d["DI"] - d["DT"] - losses
    Rp, Uref = (d["Rp_B"], d["Uref_B"]) if cal == "B" else (d["Rp_C"], d["Uref_C"])
    FOM = 160.5 - TL_ref(Rp)                   # SE = 0 at Rp under reference conditions
    N_ref = psum(nl_wind(Uref), NL_THERMAL, d["N_self"])
    N_act = psum(nl_wind(Uact), NL_THERMAL, d["N_self"]) + d["dboat_BC"]
    return SL - TLh - FOM + (N_ref - N_act) - losses

cals = ["A", "B", "C"]
cal_names = {"A": "first-principles sonar equation", "B": "manufacturer practical range 2.0-3.6 km",
             "C": "ATSB favourable-conditions range 4.0-5.0 km"}
rows = []
pdet = {}
for cal in cals:
    P = []
    for o in offs[::2]:
        se = SE_offset(cal, o, DAY1, U1)
        pd_ = draw["P_tx"]*norm.cdf(se/draw["sigma"])
        P.append((o, pd_.mean(), *np.percentile(pd_, [5, 50, 95]), *np.percentile(se, [5, 50, 95])))
    pdet[cal] = np.array(P)
hdr = "offset_m," + ",".join(f"{c}_{k}" for c in cals for k in ["Pmean", "P05", "P50", "P95", "SE05", "SE50", "SE95"])
np.savetxt(f"{OUT}/pdet_vs_offset.csv", np.hstack([pdet["A"][:, :1]] + [pdet[c][:, 1:] for c in cals]),
           delimiter=",", header=hdr, comments="", fmt="%.5g")

# ---------------------------------------------------------------- geometry test
def dTL(o): return TL_of(o) - TL_of(0.0)
grid = np.linspace(-1000, 4000, 2001)      # beacon position along the P1->P2 line, P1 at 0, P2 at +L (west)
geo = {}
for L in (2000.0, 3000.0):
    best = None
    for b in grid:
        d1, d2 = abs(b), abs(L - b)
        if dTL(d2) - dTL(d1) >= 3.0:        # second contact 'much weaker' (>= 3 dB)
            need = max(dTL(d1), dTL(d2))
            if best is None or need < best[0]: best = (need, b)
    geo[L] = {"M_req_dB": best[0], "beacon_offset_from_P1_m": best[1],
              "slant_to_P2_m": float(np.hypot(L - best[1], Z_BED - Z_RX))}
# need also the hard-limit reading: max slant range R such that both contacts possible
def r_needed(L, b): return float(np.hypot(max(abs(b), abs(L-b)), Z_BED - Z_RX))
hard = {f"L{int(L)}": r_needed(L, geo[L]["beacon_offset_from_P1_m"]) for L in geo}
SE0 = {cal: SE_offset(cal, 0.0, DAY1, U1) for cal in cals}
geom_out = {"Z_bed_m": Z_BED, "Z_bed_crossing_m": Z_BED_CROSS, "min_slant_m": Z_BED - Z_RX,
            "two_contact": {str(int(k)): v for k, v in geo.items()},
            "slant_needed_for_both_contacts_m": hard,
            "P_overhead_margin_ge_Mreq": {cal: {str(int(L)): float(np.mean(SE0[cal] >= geo[L]["M_req_dB"])) for L in geo} for cal in cals},
            "SE_overhead_pct_5_50_95": {cal: np.percentile(SE0[cal], [5, 50, 95]).round(2).tolist() for cal in cals},
            "xmax_direct_ray_m": float(xmax_direct)}
json.dump(geom_out, open(f"{OUT}/geometry_test.json", "w"), indent=1)

# ---------------------------------------------------------------- B_H
M = 100_000
idx = rng.choice(N, M, replace=False)
r = 2000*np.sqrt(rng.random(M)); ang = rng.uniform(0, 2*np.pi, M)
bx, by = r*np.cos(ang), r*np.sin(ang)            # beacon relative to P1 (x positive = west)
L2 = rng.uniform(2000, 3000, M)                   # second contact 2 km (press) .. 3 km (ATSB) west
o1 = np.hypot(bx, by); o2 = np.hypot(bx - L2, by)
f1 = lu(0.02, 0.5, M)          # P(false 37.5-kHz-like contact in Haixun's listening that day | no beacon)
f2 = rng.uniform(0.1, 0.7, M)  # P(false repeat next day | first false contact)
qE = rng.uniform(0.2, 0.7, M); qS = rng.uniform(0.2, 0.8, M); qB = rng.uniform(0.5, 0.95, M)
pidie = rng.uniform(0.05, 0.3, M)
def logistic(z): return 1/(1+np.exp(-z))
res = {}
for cal in cals:
    se1 = SE_offset(cal, o1, DAY1, U1, idx); se2 = SE_offset(cal, o2, DAY2, U2, idx)
    sig = draw["sigma"][idx]; ptx = draw["P_tx"][idx]
    p1 = norm.cdf(se1/sig); p2 = norm.cdf(se2/sig)
    weak_H = logistic((se1 - se2 - 3)/2)
    # under H: beacon transmitting (ptx) or not; each contact either true detection or false alarm
    # beacon ON: each contact is a true detection or a false alarm; weakness feature carries weak_H
    # only when both contacts are true detections; reacquisition misses by Echo, submarine, sonobuoys
    PD1 = 1-(1-p1)*(1-f1); PD2 = 1-(1-p2)*(1-f2)
    tt_ = p1*p2/np.maximum(PD1*PD2, 1e-300)       # P(both true | both reported, ON)
    PDw = tt_*weak_H + (1-tt_)*0.5
    PN_on = pidie + (1-pidie)*qE*qS*qB
    num_on = PD1*PD2*PDw*PN_on
    den = f1*f2*0.5                                 # beacon absent (or OFF): false alarms, no reacquisition
    num = ptx*num_on + (1-ptx)*den
    PN = ptx*PN_on + (1-ptx)
    B_marg = num.mean()/den.mean()
    Bc = num/den
    # term-by-term (marginal ratios)
    res[cal] = {"B_H_marginal": float(B_marg), "lnB_marginal": float(np.log(B_marg)),
                "B_conditional_pct_5_50_95": np.percentile(Bc, [5, 50, 95]).round(4).tolist(),
                "lnB_conditional_pct_5_50_95": np.log(np.percentile(Bc, [5, 50, 95])).round(3).tolist(),
                "P_contacts_true_given_H_mean": float((ptx*p1*p2).mean()),
                "p1_mean": float((ptx*p1).mean()), "p2_mean": float((ptx*p2).mean()),
                "PN_given_H_mean": float(PN.mean()),
                "contact_factor_if_on": float((PD1*PD2*PDw).mean()/den.mean()),
                "frac_B_gt_1": float((Bc > 1).mean())}
    # sensitivity over f1 (false-alarm rate)
    sens = []
    for lo, hi in [(0.02, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.5)]:
        m = (f1 >= lo) & (f1 < hi)
        sens.append({"f1_range": [lo, hi], "B_H": float(num[m].mean()/den[m].mean())})
    res[cal]["sensitivity_f1"] = sens
    # sensitivity: optimistic detection (no losses, pointing perfect) -> upper bound
    se1u = se1 + draw["point_loss"][idx] + draw["beam_loss"][idx] + draw["shield_loss"][idx]
    se2u = se2 + draw["point_loss"][idx] + draw["beam_loss"][idx] + draw["shield_loss"][idx]
    p1u, p2u = norm.cdf(se1u/sig), norm.cdf(se2u/sig)
    PD1u = 1-(1-p1u)*(1-f1); PD2u = 1-(1-p2u)*(1-f2)
    ttu = p1u*p2u/np.maximum(PD1u*PD2u, 1e-300)
    PDwu = ttu*logistic((se1u-se2u-3)/2) + (1-ttu)*0.5
    res[cal]["B_H_no_losses_upper"] = float((ptx*PD1u*PD2u*PDwu*PN_on + (1-ptx)*den).mean()/den.mean())
    res[cal]["B_H_no_losses_contacts_only"] = float((ptx*PD1u*PD2u*PDwu + (1-ptx)*den).mean()/den.mean())
    # sensitivity: contacts only (reacquisition term dropped) and reacquisition only
    res[cal]["B_H_contacts_only"] = float((ptx*PD1*PD2*PDw + (1-ptx)*den).mean()/den.mean())
    res[cal]["B_H_reacq_only"] = float((ptx*PN_on + (1-ptx)).mean())
    res[cal]["SE_overhead_no_losses_pct_5_50_95"] = np.percentile(
        SE_offset(cal, 0.0, DAY1, U1) + draw["point_loss"] + draw["beam_loss"] + draw["shield_loss"], [5, 50, 95]).round(2).tolist()
# 50/50 mixture of A and B as headline; C as upper sensitivity
summ = {"calibrations": cal_names, "per_calibration": res,
        "headline_mix_A_B": {"B_H": 0.5*(res["A"]["B_H_marginal"] + res["B"]["B_H_marginal"])},
        "inputs": {"Z_bed_m": Z_BED, "U_day1_mps": U1, "U_day2_mps": U2, "day1": float(DAY1), "day2": float(DAY2),
                   "SL_spec_day1_dB": float(SL_spec(DAY1)), "SL_spec_day2_dB": float(SL_spec(DAY2)),
                   "alpha_surface_0_200m_dBkm": alpha_surf, "alpha_path_mean_dBkm": float(Ax[0]/(Sx[0]/1000)),
                   "TL_overhead_dB": float(TLx[0]), "absorption_overhead_dB": float(Ax[0]),
                   "NL_wind_day1": float(nl_wind(U1)), "NL_thermal": float(NL_THERMAL),
                   "c_surface": float(cg[0]), "c_bed": float(cg[-1]), "c_min": float(cg.min()),
                   "z_cmin": float(zg[np.argmin(cg)]), "xmax_direct_ray_m": float(xmax_direct),
                   "N_mc_sonar": N, "N_mc_BH": M}}
json.dump(summ, open(f"{OUT}/bh_summary.json", "w"), indent=1)
print(json.dumps(summ["inputs"], indent=0))
print(json.dumps(geom_out, indent=0))
for c in cals:
    print(c, {k: v for k, v in res[c].items() if k != "sensitivity_f1"})
    print("   sens", [(s["f1_range"], round(s["B_H"], 3)) for s in res[c]["sensitivity_f1"]])
