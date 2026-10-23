
t = PD[(PD.method=="M2_pairs")].pivot_table(index=["alpha","tau"], columns="snr_db", values="pd"); print(t.round(2).to_string())
for lg in ("3274","3250"):
    t = PD[(PD.logger.astype(str)==lg)&(PD.alpha==0.01)&(PD.tau==1.0)].pivot_table(index="method", columns="snr_db", values="pd"); print("---",lg,"alpha 0.01 tau 1"); print(t.round(2).to_string())
print(json.dumps({k:{m:{a:round(v,3) for a,v in d.items()} for m,d in S["thresholds"][k].items()} for k in ("3376",)}, indent=0)[:1500])
