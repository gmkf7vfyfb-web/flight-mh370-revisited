cd "audit/repo/Claude Science Project Sep 29/results/hydroacoustics-audit/scripts"; cat >> sens.py <<'EOF'

if mode == "rhyd":
    # ln R_hyd on the stand-in's 5,000-row source package (NOT the full impact rows of rhyd_result.py), scenario A
    # and A-IMOS, real event lists, K = 8 nuisance replicas per row (as power_check.K_REP), seed as power_check.
    import json, pathlib
    from scipy.special import logsumexp
    mod, evj, kd, srcp, outd = sys.argv[4:9]
    m = Model(mod, evj, kd); src = np.load(srcp)
    c = {n: i for i, n in enumerate(src["state_columns"])}; S = src["state"]
    t, la, lo, E = S[:, c["unix_s"]], S[:, c["latitude_deg"]], S[:, c["longitude_deg"]], S[:, c["kinetic_energy_j"]]
    K = 8; rep = np.repeat(np.arange(len(la)), K)
    st = m.station_terms(t[rep], la[rep], lo[rep], E[rep], np.random.default_rng(20261010), "A")
    out = {"variant": VAR, "stations": WHICH, "n_rows": int(len(la)), "K": K}
    for lab, (k0, kH) in (("reweighted", ("w_flight", "w_H")), ("fixed", ("w_flight_fixed", "w_H_fixed"))):
        w0 = np.asarray(src[k0], float)[rep]; wH = np.asarray(src[kH], float)[rep]
        for v, L in (("A", st["total"]), ("A-IMOS", sum(st[lg] for lg in m.B.LOGGERS)), ("H01W-only", st["H01W"])):
            lr = float(logsumexp(np.log(wH) + L) - np.log(wH.sum()) - (logsumexp(np.log(w0) + L) - np.log(w0.sum())))
            half = []
            for h in (0, 1):
                mk = (rep % 2) == h
                half.append(float(logsumexp(np.log(wH[mk]) + L[mk]) - np.log(wH[mk].sum()) - (logsumexp(np.log(w0[mk]) + L[mk]) - np.log(w0[mk].sum()))))
            out[f"{lab}|{v}"] = dict(lnR=lr, split_half=half)
    pathlib.Path(outd).mkdir(parents=True, exist_ok=True)
    (pathlib.Path(outd) / "rhyd_pkg.json").write_text(json.dumps(out, indent=1))
    print(VAR, {k: round(v["lnR"], 4) for k, v in out.items() if isinstance(v, dict)})
EOF
python -c "import ast;ast.parse(open('sens.py').read())" && echo ok