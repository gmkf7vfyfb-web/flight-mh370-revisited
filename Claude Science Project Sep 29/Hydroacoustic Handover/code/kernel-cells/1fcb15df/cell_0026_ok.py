
MODELLED = RC.RECEIVERS  # 3376 3315 3274 3275 H01W H08S
lg = np.linspace(-7, 0, 1401)
def levels_for(c):
    if c["kind"]=="pair":
        m = okS & (np.abs(samp["lat"]-c["lat"])<=1.0); w = samp["w_D0"][m]
        c["E_med"] = wq(samp["E_j"][m].astype(float), w, 0.5); c["tau_med"] = wq(samp["tau90_s"][m].astype(float), w, 0.5)
    if not np.isfinite(c.get("E_med", np.nan)) or not np.isfinite(c["lat"]):
        c["eta_need"]=np.nan; c["eta_basis"]="not computed: no run J impact can produce this arrival"; c["snr"]={}; c["pd"]={}; c["L50"]={}; return
    base, ti = M.level_base(np.array([c["lat"]]), np.array([c["E_med"]]), np.array([c["tau_med"]]))
    c["base"] = {rx: float(base[rx][0]) for rx in MODELLED}
    pdc = {rx: M.pd(rx, 0.05, base[rx][0] + 10*lg[None,:], ti)[0] for rx in MODELLED}
    det = [rx for rx in c["rx"] if rx in MODELLED]
    if det:
        prod = np.prod([pdc[rx] for rx in det], axis=0)
        k = np.argmax(prod>=0.5) if (prod>=0.5).any() else None
        c["eta_need"] = 10**lg[k] if k is not None else np.inf
        c["eta_basis"] = ("P_D = 0.5 jointly at " if len(det)>1 else "P_D = 0.5 at ") + " and ".join(names[r] for r in det)
        if len(det)<len(c["rx"]): c["eta_basis"] += f" ({', '.join(names[r] for r in c['rx'] if r not in MODELLED)}: path blocked, no level model)"
    else:
        c["eta_need"] = np.nan; c["eta_basis"] = "undefined: " + ", ".join(names[r] for r in c["rx"]) + " path blocked in the sound-loss grid"
    eta_line = c["eta_need"] if np.isfinite(c["eta_need"]) else 1e-2
    c["eta_line"] = eta_line; c["eta_line_label"] = (f"needed coupling {eta_line:.2g}" if np.isfinite(c["eta_need"]) else "coupling 0.01 (top of the prior range)")
    l50, sl, ok = {}, {}, {}
    c["snr"] = {rx: c["base"][rx] + 10*np.log10(eta_line) for rx in MODELLED}
    c["pd"] = {rx: float(M.pd(rx, 0.05, np.array([[c["snr"][rx]]]), ti)[0,0]) for rx in MODELLED}
    c["L50"] = {rx: float(M.pd_par[(rx,0.05)][0][ti[0]]) for rx in MODELLED}
    c["snr_anchor"] = {rx: c["base"][rx] + 10*np.log10(RC.ETA_ANCHOR) for rx in MODELLED}
    c["ti"]=int(ti[0])
for c in cands:
    levels_for(c)
    print(c["name"], "| lat", round(c["lat"],2) if np.isfinite(c["lat"]) else None, "E", round(c.get("E_med",np.nan)/1e9,2), "tau", round(c.get("tau_med",np.nan),2), "| eta", c["eta_need"], c["eta_basis"])
    if c["snr"]: print("   SNR", {rx: round(v,1) for rx,v in c["snr"].items()}, "\n   PD", {rx: round(v,3) for rx,v in c["pd"].items()}, "\n   L50", {rx: round(v,1) for rx,v in c["L50"].items()})
