s2s=lambda h:sum(int(x)*m for x,m in zip(h.split(":"),(3600,60,1)))
Q=[0.005,0.025,0.05,0.25,0.5,0.75,0.95,0.975,0.995]
K={"H01W":("00:27:00","00:57:00"),"H08S":("01:00:00","01:20:00")}
def cover(rows, arm, var, st):
    r=[x for x in rows if x["arm"]==arm and x["variant"]==var and x["receiver"]==st and x["branch"]=="sofar"][0]
    t=np.array([s2s(r[k]) for k in QK]); F=lambda x: np.interp(x,t,Q,left=0,right=1)
    return F(s2s(K[st][1]))-F(s2s(K[st][0])), r["q50"]
ARMS5=["none__other","none__fuel-exhaustion","r600_inflated__other","r600_no-offset__other","r600-bto__other"]
cov=[]
for arm in ARMS5:
    row=[arm]
    for st in K:
        for var in ("alive","silent"):
            c,_=cover(RowsM,arm,var,st); c2,_=cover(Rows289,arm,var,st); row.append((round(c,2),round(c2,2)))
    cov.append(row); print(row)
for st in ("H01W","H08S"):
    for var in ("alive","silent"):
        h=[r for r in sel if r["receiver"]==st and r["branch"]=="sofar" and r["variant"]==var]
        e=max(h,key=lambda r:float(r["window_end_unix"])); print(st,var,"end-driver",e["arm"],e["q99.5"],e["converged"],e["seed_spread_q99p5_s"], e["window_end"])
for k in ["none__other+alive","none__fuel-exhaustion+alive","r600-bto__other+alive","r600_inflated__other+alive","r600_no-offset__other+alive"]:
    print(k, round(M[k]["share_after_011556"],4), round(S289[k]["share_after_011556_seed_mean"],4))