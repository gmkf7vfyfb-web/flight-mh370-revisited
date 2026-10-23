def recd(p): return {(r["variant"],r["receiver"],r["branch"]):r for r in csv.DictReader(open(p/"recommended_windows.csv"))}
R289=recd(MW); RM=recd(O/"mixture")
bad=[k for k in RM if not (s2m(RM[k]["window_start"])>=s2m(R289[k]["window_start"]) and s2m(RM[k]["window_end"])<=s2m(R289[k]["window_end"]))]
print("mixture outside", bad)
for s in ["next-free","next-repro-radar","next-descent-climb","next-routes"]:
    RS=recd(O/s); print(s,[k for k in RS if not (s2m(RS[k]["window_start"])>=s2m(R289[k]["window_start"]) and s2m(RS[k]["window_end"])<=s2m(R289[k]["window_end"]))])
d=[(k, s2m(S289[k+"+alive"]["impact_q_pooled_utc"][-1])-s2m(M[k+"+alive"]["impact_q_pooled_utc"][-1])) for k in M if k.endswith("__other") and M[k+"+alive"]["ess_mixture_kish"]>=1000]
print(sorted(d,key=lambda x:x[1]))
print([ (k, s2m(R289[k]["window_end"])-s2m(RM[k]["window_end"])) for k in RM if k[2]=="sofar"])