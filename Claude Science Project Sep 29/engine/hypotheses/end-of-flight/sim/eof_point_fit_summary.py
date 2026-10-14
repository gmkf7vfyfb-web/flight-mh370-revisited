"""Item 2 summary: the leave-one-out table (each case predicted by the fit that did NOT see it) beside the all-data fit.
    python eof_point_fit_summary.py OUT_DIR      ->  OUT_DIR/summary.json, OUT_DIR/loo-table.csv, a text table on stdout
Gate rule (approved README): a case passes when every target that applies to it is inside its tolerance OUT OF SAMPLE, here judged
on the predictive median of the model's feature under the fold's fitted mixture, AND the predictive probability of the right
dive class and turn direction is at least 0.5. A case that fails is reported with its residuals; it is not dropped or refitted."""
import json, sys, pathlib, csv
out = pathlib.Path(sys.argv[1]); allfit = json.load(open(out / "all" / "fit.json"))
cases = sorted(allfit["prediction"]); rows = []; summ = {"theta_all": allfit["theta"], "theta_loo": {}, "cases": {}}
for c in cases:
    f = json.load(open(out / f"loo-{c}" / "fit.json")); summ["theta_loo"][c] = f["theta"]
    p = f["prediction"][c]; ok_cat = p["p_dive_class"] >= 0.5 and p["p_direction"] >= 0.5
    tg = {}
    for k, v in p["targets"].items():
        tg[k] = dict(boeing=v["boeing"], tol=v["tol"], median=v.get("median"), residual=(v["median"] - v["boeing"]) if v.get("median") is not None else None,
                     pass_=bool(v.get("pass_median", False)), p_within=v.get("p_within"))
        rows.append(dict(case=c, dive_case=c in ("Case 03", "Case 04", "Case 05", "Case 06", "Case 10"), target=k, boeing=v["boeing"], tolerance_2sigma=v["tol"],
                         loo_median=v.get("median"), residual=tg[k]["residual"], within_tol=tg[k]["pass_"], p_within=v.get("p_within"),
                         all_data_median=allfit["prediction"][c]["targets"][k].get("median")))
    passed = ok_cat and all(t["pass_"] for t in tg.values())
    summ["cases"][c] = dict(passed=passed, p_dive_class=p["p_dive_class"], p_direction=p["p_direction"], loglik_oos=f["case_loglik"][c],
                            loglik_in_all=allfit["case_loglik"][c], targets=tg)
summ["gate_passed"] = all(v["passed"] for v in summ["cases"].values())
json.dump(summ, open(out / "summary.json", "w"), indent=1)
with open(out / "loo-table.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("all-data theta:", {k: round(v, 5) for k, v in allfit["theta"].items()})
for c, v in summ["cases"].items():
    fails = [k for k, t in v["targets"].items() if not t["pass_"]]
    print(f"{c}: {'PASS' if v['passed'] else 'FAIL'}  p(dive class) {v['p_dive_class']:.2f}  p(direction) {v['p_direction']:.2f}  out-of-sample loglik {v['loglik_oos']:.1f}  failed: {', '.join(fails) or '-'}")
print("gate:", "PASSED" if summ["gate_passed"] else "FAILED")
