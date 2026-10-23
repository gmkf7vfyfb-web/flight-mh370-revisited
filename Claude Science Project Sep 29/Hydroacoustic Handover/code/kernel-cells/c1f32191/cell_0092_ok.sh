cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
r=open("reduce.py").read()
r=r.replace('''from worker import KEYS, NB1, NBH, FAM_CODES''','''from worker import KEYS, NB1, NBH, FAM_CODES
import os
STATS_ONLY = os.environ.get("B11_STATS_ONLY") == "1"     # amendment A4: RAM-grid IMOS TL + amplitude-weighted variant present in the accumulators''')
# upper limits: amplitude variant rows (full-likelihood Bayes only; Pnd identical to IMOS gated)
r=r.replace('''            for ims in (False, True):
                wP = mx[f"wPnd{'_ims' if ims else ''}_{t}"][j]; wL = mx[f"wL{'_ims' if ims else ''}_{t}"][j]; sw = mx["sum_w"][j]; sw2 = mx["sum_w2"][j]''','''            variants = [(False, "IMOS gated"), (True, "IMS proxy + IMOS")] + ([("A", "IMOS gated (amplitude-weighted)")] if STATS_ONLY else [])
            for ims, label in variants:
                wP = mx[f"wPnd{'_ims' if ims is True else ''}_{t}"][j]; wL = mx[f"wL_A_{t}" if ims == "A" else f"wL{'_ims' if ims else ''}_{t}"][j]; sw = mx["sum_w"][j]; sw2 = mx["sum_w2"][j]''')
r=r.replace('''                    if W <= 0: rows.append(dict(option=key.split("/")[0], p=float(key.split("/p")[1]), alpha=a, receivers="IMS proxy + IMOS" if ims else "IMOS gated", lat_lo=lo, lat_hi=hi, share=0.0, ess=0.0)); continue''','''                    if W <= 0: rows.append(dict(option=key.split("/")[0], p=float(key.split("/p")[1]), alpha=a, receivers=label, lat_lo=lo, lat_hi=hi, share=0.0, ess=0.0)); continue''')
r=r.replace('''                    rows.append({"option": key.split("/")[0], "p": float(key.split("/p")[1]), "alpha": a, "receivers": "IMS proxy + IMOS" if ims else "IMOS gated", "lat_lo": lo, "lat_hi": hi,''','''                    rows.append({"option": key.split("/")[0], "p": float(key.split("/p")[1]), "alpha": a, "receivers": label, "lat_lo": lo, "lat_hi": hi,''')
# evidence three ways: amplitude variant
r=r.replace('''        for a in R.ALPHAS:
            for ims in (False, True):
                wL = mx[f"half_wL{'ims' if ims else ''}_{ALPHA_TAGS[a]}"][j]
                comb = wL / wL.sum() if wL.sum() > 0 else wL''','''        for a in R.ALPHAS:
            for ims, label in [(False, "IMOS gated"), (True, "IMS proxy + IMOS")] + ([("A", "IMOS gated (amplitude-weighted)")] if STATS_ONLY else []):
                wL = mx[f"half_wLA_{ALPHA_TAGS[a]}" if ims == "A" else f"half_wL{'ims' if ims else ''}_{ALPHA_TAGS[a]}"][j]
                comb = wL / wL.sum() if wL.sum() > 0 else wL''')
r=r.replace('''                dists[(key, a, ims)] = dict(mid=mid, core=corep, combined=comb, alone=alone)
                rows.append(dict(option=key.split("/")[0], p=float(key.split("/p")[1]), alpha=a, receivers="IMS proxy + IMOS" if ims else "IMOS gated",''','''                dists[(key, a, ims)] = dict(mid=mid, core=corep, combined=comb, alone=alone)
                rows.append(dict(option=key.split("/")[0], p=float(key.split("/p")[1]), alpha=a, receivers=label,''')
r=r.replace('''    np.savez_compressed(out / "latitude_distributions.npz", **{f"{k[0]}|a{k[1]:g}|{'ims' if k[2] else 'imos'}|{n}": v for k, d in dists.items() for n, v in d.items()})''','''    np.savez_compressed(out / "latitude_distributions.npz", **{f"{k[0]}|a{k[1]:g}|{'amp' if k[2] == 'A' else ('ims' if k[2] else 'imos')}|{n}": v for k, d in dists.items() for n, v in d.items()})''')
# families + holland: amplitude variant
r=r.replace('''            rows.append(dict(option=o, p=p, family=FAM_NAMES[c], share=float(w / Z) if Z > 0 else 0.0, ess=float(w * w / w2) if w2 > 0 else 0.0,
                             lnZ_hydro_imos=float(np.log(wL / w)) if w > 0 and wL > 0 else None, lnZ_hydro_ims_proxy=float(np.log(wLi / w)) if w > 0 and wLi > 0 else None))''','''            wLA = mx["fam_wLA"][j, k] if STATS_ONLY else np.nan
            rows.append(dict(option=o, p=p, family=FAM_NAMES[c], share=float(w / Z) if Z > 0 else 0.0, ess=float(w * w / w2) if w2 > 0 else 0.0,
                             lnZ_hydro_imos=float(np.log(wL / w)) if w > 0 and wL > 0 else None, lnZ_hydro_ims_proxy=float(np.log(wLi / w)) if w > 0 and wLi > 0 else None,
                             lnZ_hydro_imos_ampweighted=float(np.log(wLA / w)) if (STATS_ONLY and w > 0 and wLA > 0) else None))''')
r=r.replace('''            z[p] = {a: dict(imos=mx[f"wLmarg_{ALPHA_TAGS[a]}"][j] / Z, ims=mx[f"wLmarg_ims_{ALPHA_TAGS[a]}"][j] / Z,''','''            z[p] = {a: dict(imos=mx[f"wLmarg_{ALPHA_TAGS[a]}"][j] / Z, ims=mx[f"wLmarg_ims_{ALPHA_TAGS[a]}"][j] / Z, amp=(mx[f"wLmarg_A_{ALPHA_TAGS[a]}"][j] / Z) if STATS_ONLY else np.nan,''')
r=r.replace('''                            lnBF_p1_vs_p0_nondetection_only=float(np.log(z[1.0][a]["nd_imos"] / z[0.0][a]["nd_imos"])),''','''                            lnBF_p1_vs_p0_nondetection_only=float(np.log(z[1.0][a]["nd_imos"] / z[0.0][a]["nd_imos"])),
                            lnBF_p1_vs_p0_ampweighted=float(np.log(z[1.0][a]["amp"] / z[0.0][a]["amp"])) if STATS_ONLY else None,''')
# conditionals: amplitude variant
r=r.replace('''    for a in R.ALPHAS:
        lg, pg, nsc = M.lnL_grid(PP, Lcal, a, R.RECEIVERS_GATED); li, pi, nsci = M.lnL_grid(PP, Lcal, a, R.RECEIVERS_PROXY)
        out[f"L_imos_a{a:g}"] = float(np.exp(M.marg(lg)).mean()); out[f"L_ims_a{a:g}"] = float(np.exp(M.marg(lg + li)).mean())''','''    for a in R.ALPHAS:
        lg, pg, nsc, la_ = M.lnL_grid(PP, Lcal, a, R.RECEIVERS_GATED, amp=True); li, pi, nsci = M.lnL_grid(PP, Lcal, a, R.RECEIVERS_PROXY)
        out[f"L_imos_a{a:g}"] = float(np.exp(M.marg(lg)).mean()); out[f"L_ims_a{a:g}"] = float(np.exp(M.marg(lg + li)).mean()); out[f"L_imos_amp_a{a:g}"] = float(np.exp(M.marg(la_)).mean())''')
r=r.replace('''    for a in R.ALPHAS:
        df[f"lnBF_imos_a{a:g}"] = np.log(df[f"L_imos_a{a:g}"] / Zrun[a]["imos"]); df[f"lnBF_ims_proxy_a{a:g}"] = np.log(df[f"L_ims_a{a:g}"] / Zrun[a]["ims"])''','''    for a in R.ALPHAS:
        df[f"lnBF_imos_a{a:g}"] = np.log(df[f"L_imos_a{a:g}"] / Zrun[a]["imos"]); df[f"lnBF_ims_proxy_a{a:g}"] = np.log(df[f"L_ims_a{a:g}"] / Zrun[a]["ims"])
        if "amp" in Zrun[a]: df[f"lnBF_imos_amp_a{a:g}"] = np.log(df[f"L_imos_amp_a{a:g}"] / Zrun[a]["amp"])''')
r=r.replace('''    S = concat_sub(sub, supp_sub); M = Machinery()
    j = KEYS.index("D0/p0.5"); Z = mx["sum_w"][j].sum()
    Zrun = {a: dict(imos=mx[f"wLmarg_{ALPHA_TAGS[a]}"][j] / Z, ims=mx[f"wLmarg_ims_{ALPHA_TAGS[a]}"][j] / Z) for a in R.ALPHAS}''','''    S = concat_sub(sub, supp_sub); M = Machinery(imos_ramgrid=STATS_ONLY)
    j = KEYS.index("D0/p0.5"); Z = mx["sum_w"][j].sum()
    Zrun = {a: dict(imos=mx[f"wLmarg_{ALPHA_TAGS[a]}"][j] / Z, ims=mx[f"wLmarg_ims_{ALPHA_TAGS[a]}"][j] / Z, **({"amp": mx[f"wLmarg_A_{ALPHA_TAGS[a]}"][j] / Z} if STATS_ONLY else {})) for a in R.ALPHAS}''')
r=r.replace('''    summary = dict(prereg="90d7181",''','''    summary = dict(prereg="90d7181" + (" + A4 e13a32e (RAM-grid IMOS TL, statistics only)" if STATS_ONLY else ""), imos_tl="imos_tl_ram_arc.csv" if STATS_ONLY else "imos_tl_ramcorr_arc.csv", ramgrid_covered_share=M.ramgrid_covered_share,''')
open("reduce.py","w").write(r); print("ok")
EOF
python -c "import ast,sys; ast.parse(open('reduce.py').read()); print('syntax ok')"
S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/stats-ramgrid; tail -1 $S/driver.log; ls $S/_parts 2>/dev/null | wc -l