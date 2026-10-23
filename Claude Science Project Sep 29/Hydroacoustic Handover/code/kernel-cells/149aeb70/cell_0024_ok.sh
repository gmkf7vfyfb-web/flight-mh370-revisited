R=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i
python3 - <<'PY'
import json, csv
R="/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i"
a=json.load(open(f"{R}/loud_tail_ess.json")); b=json.load(open(f"{R}/parent_ess.json"))
rows=[]
for r in a["rows"]:
    o=r["option"]; p=b["options"].get(o,{})
    rows.append(dict(option=o, ess_impacts_all=round(r["ess_all"]),
        ess_parents_all=round(p.get("ess_parents_all",float("nan"))) if p else "",
        mass_loud_decile=round(r["mass_p90"],4), ess_impacts_loud=round(r["ess_p90"]),
        ess_parents_loud=round(p.get("ess_parents_loud_p90",float("nan"))) if p else "",
        mass_loud_pct=round(r["mass_p99"],4), ess_impacts_top_pct=round(r["ess_p99"]),
        median_peak_power_W=f'{r["med_peak_W"]:.3e}', median_tau90_s=round(r["med_tau90_s"],3)))
with open("run-i-loud-tail-estimability.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(json.dumps(rows,indent=0))
print("thresholds",a["thresholds_W"],"parents",b["n_parents"])
PY