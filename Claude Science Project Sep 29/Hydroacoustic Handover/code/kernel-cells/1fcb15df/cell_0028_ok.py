
cl = pd.read_csv(os.path.join(MOD,"results-data/composition_run_j/v2/coincidence_locus.csv")).iloc[0]
def levels_pre(c):
    if c["kind"]=="pair":
        m = okS & (np.abs(samp["lat"]-c["lat"])<=1.0)
        E = samp["E_j"][m].astype(float); tau = samp["tau90_s"][m].astype(float); w = samp["w_D0"][m]
        f = np.isfinite(E)&np.isfinite(tau)
        c["E_med"] = wq(E[f], w[f], 0.5); c["tau_med"] = wq(tau[f], w[f], 0.5); c["Etau_src"]="search-geometry sample rows within 1 deg of the locus"
        if c["name"].startswith("Pair 1"):
            c["E_med"]=cl.E_median_GJ*1e9; c["tau_med"]=cl.tau_median_s; c["Etau_src"]="composition coincidence_locus.csv (v2)"
levels_for_orig = levels_for
def levels_for2(c):
    levels_pre(c)
    k = c["kind"]; c["kind"]="_tmp"; levels_for_orig(c); c["kind"]=k
for c in cands:
    if c["kind"]=="single": c["Etau_src"]="sample rows conditioned on the observed arrival"
    levels_for2(c)
    print(c["name"][:60], "| E", round(c.get("E_med",np.nan)/1e9,2), "tau", round(c.get("tau_med",np.nan),2), "| eta", c["eta_need"])
    if c["snr"]: print("   SNR", {rx: round(v,1) for rx,v in c["snr"].items()}, " PD", {rx: round(v,2) for rx,v in c["pd"].items()})
