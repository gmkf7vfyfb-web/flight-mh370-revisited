import subprocess
SS={s:json.load(open(O/s/"summary.json"))["arms"] for s in ["next-free","next-repro-radar","next-descent-climb","next-routes"]}
S289=json.load(open(MW/"summary.json"))["arms"]; M=summ
keys=["none__other","none__fuel-exhaustion","r600_inflated__other","r600_no-offset__other","r600-bto__other","r1200_inflated__other","both_inflated__other","both_startup-offset__fuel-exhaustion","both_no-offset__other"]
lines=[]
for k in keys:
    for v in ("+alive","+silent"):
        kk=k+v; m=M[kk]; r=S289[kk]
        lines.append(f"| `{kk}` | {m['ess_mixture_kish']:,.0f} | {m['impact_q_pooled_utc'][0]} | {m['impact_q_pooled_utc'][4]} | {m['impact_q_pooled_utc'][-1]} | {m['share_after_011556']:.4f} | {r['ess_pooled']:,.0f} | {r['impact_q_pooled_utc'][0]} | {r['impact_q_pooled_utc'][4]} | {r['impact_q_pooled_utc'][-1]} | {r['share_after_011556_seed_mean']:.4f} |")
print("\n".join(lines))
print(subprocess.run(["date","-u","+%Y-%m-%d %H:%M:%SZ"],capture_output=True,text=True).stdout)