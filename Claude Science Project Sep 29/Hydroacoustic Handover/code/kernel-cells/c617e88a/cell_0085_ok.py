ON={"r600-bto-only":"00:19 R600 BTO Only","held-out":"00:19 Held Out","r600-bto-raw-bfo":"00:19 R600 BTO + Raw BFO"}
lines=["| 00:19 option | data set | E[ln R] if H true (± MC) | E[ln R] if no H (± MC) | P(\\|ln R\\| ≥ 0.5) H / no H | P(\\|ln R\\| ≥ 1) H / no H | P(\\|ln R\\| ≥ 2.3) H / no H |","|---|---|---|---|---|---|---|"]
SN={"A":"A: held, as pre-registered","A-IMOS":"A, IMOS only","B":"B: held, all IMOS recordings scored","C":"C: + raw H01W/H08S (not held)"}
for o,nm in ON.items():
    for sc in ["A","A-IMOS","B","C"]:
        H=PW[o]["synthetic"][sc]["H"]["reweighted"]; N=PW[o]["synthetic"][sc]["noH"]["reweighted"]
        lines.append(f"| {nm} | {SN[sc]} | {H['mean']:+.3f} ± {H['mc_se_mean']:.3f} | {N['mean']:+.3f} ± {N['mc_se_mean']:.3f} | {H['p_abs_ge_0p5']:.2f} / {N['p_abs_ge_0p5']:.2f} | {H['p_abs_ge_1']:.2f} / {N['p_abs_ge_1']:.2f} | {H['p_abs_ge_2p3']:.3f} / {N['p_abs_ge_2p3']:.3f} |")
PT="\n".join(lines)
wl=["| 00:19 option | H01W | Perth Canyon 3376 | Portland 3274 | H08S | H08N | stop rule |","|---|---|---|---|---|---|---|"]
for o,nm in ON.items():
    w=PW[o]["windows"]; sr=PW[o]["stop_rule"]
    wl.append(f"| {nm} | "+" | ".join(f"{w[s]['reweighted']['ovl']:.2f} ({(w[s]['reweighted']['q_flight'][1]-w[s]['reweighted']['q_H'][1])/60:.1f} min)" for s in ["H01W","3376","3274","H08S","H08N"])+f" | {'not informative' if sr['not_informative'] else 'informative: proceed'} |")
WT="\n".join(wl)
rl=["| 00:19 option | ln R_hyd, strata re-weighted (± split-half σ; max) | reading | ln R_hyd, fixed weights (± σ) | R_hyd (re-weighted) | ESS flight / under H (rows, 16 seeds) | not-computed weight |","|---|---|---|---|---|---|---|"]
for o in O:
    d=O[o]; a=d["reweighted|A"]; f=d["fixed|A"]
    ef=sum(d["ess_flight"].values()); eh=sum(d["ess_H"].values()); nc=[v for v in d["not_computed_weight"].values()]
    rl.append(f"| {o} | {a['lnR']:+.3f} ± {a['split_half_se']:.3f} ({a['split_half_max']:.3f}) | {a['reading']} (±2σ: {a['reading_lo']} .. {a['reading_hi']}) | {f['lnR']:+.3f} ± {f['split_half_se']:.3f} | {np.exp(a['lnR']):.3f} | {ef/1e6:.1f} M / {eh/1e6:.2f} M | {min(nc)*100:.1f}-{max(nc)*100:.1f} % |")
RT="\n".join(rl)
sl=["| 00:19 option | IMOS only | H01W (Kadri) only | vertical kinetic energy | not-computed excluded from both | per stratum (free / Davey dyn.+radar / descent-climb / routes) |","|---|---|---|---|---|---|"]
for o in O:
    d=O[o]; g=lambda k: f"{d[k]['lnR']:+.3f} ± {d[k]['split_half_se']:.3f}"
    ps=d["reweighted|per_stratum_A"]
    sl.append(f"| {o} | {g('reweighted|A-IMOS')} | {g('reweighted|H01W-only')} | {g('reweighted|A-VKE')} | {g('reweighted|A|nc_both')} | "+" / ".join(f"{ps[s]:+.3f}" for s in ["next-free","next-repro-radar","next-descent-climb","next-routes"])+" |")
ST="\n".join(sl)
zl=["| 00:19 option | ln Ẑ_00:19 free / Davey dyn.+radar / descent-climb / routes (seed sd) | P(family) re-weighted | matches Pléiades stand-in |","|---|---|---|---|"]
z=np.load("/Users/pete/Downloads/mh370-exchange/pleiades/hydro-test/next-run-b/sources-0019-r600-bto-only.npz")
for o,fn in zip(O,["r600-bto-only","held-out","r600-bto-raw-bfo"]):
    d=O[o]; zz=np.load(f"/Users/pete/Downloads/mh370-exchange/pleiades/hydro-test/next-run-b/sources-0019-{fn}.npz"); pr=dict(zip(zz["stratum_names"],zz["p_family_reweighted"]))
    mx=max(abs(pr[s]-d["p_family_reweighted"][s]) for s in pr)
    zl.append(f"| {o} | "+" / ".join(f"{d['ln_Z0019_per_family'][s]:.3f} ({d['ln_Z0019_seed_sd'][s]:.3f})" for s in ["next-free","next-repro-radar","next-descent-climb","next-routes"])+" | "+" / ".join(f"{d['p_family_reweighted'][s]:.4f}" for s in ["next-free","next-repro-radar","next-descent-climb","next-routes"])+f" | max \\|Δ\\| {mx:.1e} |")
ZT="\n".join(zl)
print(PT);print(WT);print(RT);print(ST);print(ZT)