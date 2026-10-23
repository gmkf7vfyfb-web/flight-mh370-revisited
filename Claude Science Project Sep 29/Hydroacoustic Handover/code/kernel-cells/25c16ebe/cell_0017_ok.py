print("tau method/note:", int(tz["method"]), str(tz["note"]))
tau = tz["tau90_s"][idx]; etj = tz["energy_transferred_j"][idx]
print("tau90 nonfinite frac:", 1-np.isfinite(tau).mean(), " quantiles(none):", [round(x,2) for x in wq(tau,P['none'])])
print("energy_transferred_j quantiles (GJ, none):", [round(x,3) for x in wq(etj/1e9,P['none'])])
print("decel_g q:", [round(x,2) for x in wq(tz['decel_g'][idx],P['none'])], " l_eff_m q:", [round(x,1) for x in wq(tz['l_eff_m'][idx],P['none'])])

eof = json.loads(json.dumps(rj["config"]))["hypotheses"]["end-of-flight"]
for k in sorted(eof.keys()): 
    v = eof[k]
    print(f"\n[{k}]")
    if isinstance(v, dict):
        for kk in sorted(v): print("   ", kk, "=", v[kk])
    else: print("   ", v)
