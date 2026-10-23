cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
s=open("common.py").read()
old=s[s.index("    def lnL_grid(self"):s.index("    def marg(self")]
new='''    def prep(self, t, lat, lon, E, tau):
        """Geometry and level base shared by every alpha and receiver set."""
        d = self.distances_km(lat, lon); base, ti = self.level_base(lat, E, tau)
        tp = {rx: t + d[rx] / R.C_SOFAR for rx in R.RECEIVERS}
        sc = {rx: self.in_scored(rx, tp[rx]) & np.isfinite(base[rx]) for rx in R.RECEIVERS}
        return dict(d=d, base=base, ti=ti, tp=tp, sc=sc, n=len(t))

    def lnL_grid(self, P_, Lcal, alpha, receivers):
        """Returns lnL[n, K] = sum_r ln L_r and lnPnd[n, K] = sum_r ln(1 - P_D,r) over the receivers whose predicted arrival
        lies in a scored window (others contribute 0 = no information), and the count of scored receivers per row."""
        n = P_["n"]; K = len(self.eta_eval)
        lnL = np.zeros((n, K)); lnPnd = np.zeros((n, K)); nsc = np.zeros(n, np.int8)
        for rx in receivers:
            sc = P_["sc"][rx]
            if not sc.any(): continue
            nsc[sc] += 1
            snr = P_["base"][rx][sc][:, None] + 10 * self.log10eta[None, :] + Lcal[sc][:, None]
            P = self.pd(rx, alpha, snr, P_["ti"][sc]); mr = self.match(rx, alpha, P_["tp"][rx][sc], P_["d"][rx][sc])
            Lr = (1 - P) + P * mr[:, None]
            lnL[sc] += np.log(np.maximum(Lr, 1e-300)); lnPnd[sc] += np.log(np.maximum(1 - P, 1e-300))
        return lnL, lnPnd, nsc

'''
s=s.replace(old,new); open("common.py","w").write(s)
w=open("worker.py").read()
w=w.replace('''                for k in range(L.shape[1]):
                    self.wPnd[a][j] += np.bincount(b1, weights=w * P[:, k], minlength=NB1)[:, None][:, 0] * 0 if False else 0  # placeholder (vectorised below)
''','')
w=w.replace('''        lnL = {}; lnPnd = {}; lnL_ims = {}; lnPnd_ims = {}
        for a in R.ALPHAS:
            l_g, p_g, nsc = M.lnL_grid(t[idx], lat[idx], lon[idx], E[idx], tau90[idx], Lcal[idx], a, R.RECEIVERS_GATED)
            l_i, p_i, nsc_i = M.lnL_grid(t[idx], lat[idx], lon[idx], E[idx], tau90[idx], Lcal[idx], a, R.RECEIVERS_PROXY)
            lnL[a] = l_g; lnPnd[a] = p_g; lnL_ims[a] = l_g + l_i; lnPnd_ims[a] = p_g + p_i
            if a == R.ALPHA_PRIMARY:
                A.n_scored_any += int((nsc + nsc_i > 0).sum())
                for rx in R.RECEIVERS_GATED:
                    tp = t[idx] + M.distances_km(lat[idx], lon[idx])[rx] / R.C_SOFAR; A.n_scored_rx[rx] += int(M.in_scored(rx, tp).sum())
''','''        lnL = {}; lnPnd = {}; lnL_ims = {}; lnPnd_ims = {}
        PP = M.prep(t[idx], lat[idx], lon[idx], E[idx], tau90[idx])
        for a in R.ALPHAS:
            l_g, p_g, nsc = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_GATED)
            l_i, p_i, nsc_i = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_PROXY)
            lnL[a] = l_g; lnPnd[a] = p_g; lnL_ims[a] = l_g + l_i; lnPnd_ims[a] = p_g + p_i
            if a == R.ALPHA_PRIMARY:
                A.n_scored_any += int((nsc + nsc_i > 0).sum())
                for rx in R.RECEIVERS: A.n_scored_rx[rx] += int(PP["sc"][rx].sum())
''')
w=w.replace('''        lnL = {}; lnPnd = {}; lnL_ims = {}; lnPnd_ims = {}
        for a in R.ALPHAS:
            l_g, p_g, nsc = M.lnL_grid(t[idx], lat[idx], lon[idx], E[idx], tau[idx], Lcal[idx], a, R.RECEIVERS_GATED)
            l_i, p_i, nsc_i = M.lnL_grid(t[idx], lat[idx], lon[idx], E[idx], tau[idx], Lcal[idx], a, R.RECEIVERS_PROXY)
''','''        lnL = {}; lnPnd = {}; lnL_ims = {}; lnPnd_ims = {}
        PP = M.prep(t[idx], lat[idx], lon[idx], E[idx], tau[idx])
        for a in R.ALPHAS:
            l_g, p_g, nsc = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_GATED)
            l_i, p_i, nsc_i = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_PROXY)
''')
w=w.replace("    tau_src = json.load(open(R.RD / \"injection_run_j\" / \"inputs.json\"))[\"tau90_quantiles_s\"] if (R.RD / \"injection_run_j\" / \"inputs.json\").exists() else None\n","")
open("worker.py","w").write(w); print("ok")
EOF
sed -i '' 's/^CHUNK_ROWS = 1_000_000/CHUNK_ROWS = 500_000/' prereg.py; grep -n CHUNK_ROWS prereg.py