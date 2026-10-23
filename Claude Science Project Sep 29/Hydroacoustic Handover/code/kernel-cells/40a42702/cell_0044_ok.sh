cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
python - <<'EOF'
p='inputs.py'; s=open(p).read()
old=s[s.index('    res = {"n_rows"'):s.index('    res["receivers"]')]
new='''    res = {"n_rows": int(len(D["lat"])), "n_seeds": nseeds, "seed_rows": seed_rows, "p_core": p_core,
           "chunks_per_seed": R.CHUNKS_PER_SEED, "chunk_rows": R.CHUNK_ROWS, "tau": {}, "range_km": {}, "E_j": {}, "ess": {}}
    # quantiles on a 1-in-4 systematic thin (the same rows saved for the eta mapping); distances once per receiver
    th = slice(0, None, 4)
    Dt = {k: v[th] for k, v in D.items()}
    dist = {r: W.geodesic_km(Dt["lat"], Dt["lon"], rlat, rlon) for r, (rlat, rlon) in rx.items()}
    o_tau = np.argsort(Dt["tau90_s"]); o_E = np.argsort(Dt["E_j"]); o_d = {r: np.argsort(dist[r]) for r in rx}
    def wq_sorted(xs, w_sorted, qs):
        c = np.cumsum(w_sorted); c /= c[-1]
        return [float(np.interp(q, c, xs)) for q in qs]
    for o in R.OPTIONS:
        for p in R.PS:
            w = np.exp(Dt[f"lnw_{o}"]); f = np.ones(len(w)); dr, ts = Dt["pf_drawn"], Dt["pf_surface"]
            f[dr & ts] = 2 * p; f[dr & ~ts] = 2 * (1 - p); w = w * f
            w = np.where(np.isfinite(Dt["tau90_s"]), w, 0.0)
            key = f"{o}/p{p:g}"
            res["ess"][key] = float(w.sum() ** 2 / (w ** 2).sum())
            res["tau"][key] = wq_sorted(Dt["tau90_s"][o_tau], w[o_tau], list(R.TAU_QS))
            res["E_j"][key] = wq_sorted(Dt["E_j"][o_E], w[o_E], [0.05, 0.25, 0.5, 0.75, 0.95])
            res["range_km"][key] = {r: wq_sorted(dist[r][o_d[r]], w[o_d[r]], list(R.RANGE_QS)) for r in rx}
            print("quantiles", key, round(time.time() - t0), flush=True)
'''
s=s.replace(old,new)
s=s.replace('    thin = slice(0, None, 4)\n    np.savez_compressed(out / "subsample.npz", **{k: (v[thin].astype(np.float32) if v.dtype == np.float64 else v[thin]) for k, v in D.items()})',
            '    np.savez_compressed(out / "subsample.npz", **{k: (v.astype(np.float32) if v.dtype == np.float64 else v) for k, v in Dt.items()}, **{f"dist_{r}": dist[r].astype(np.float32) for r in rx})')
s=s.replace('systematic chunk subsample\n', 'systematic chunk subsample; quantiles and the saved subsample use a 1-in-4 systematic thin of it (declared)\n')
open(p,'w').write(s)
EOF
python -c "import ast;ast.parse(open('inputs.py').read());print('ok')"