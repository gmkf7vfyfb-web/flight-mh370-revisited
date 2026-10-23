import glob
for tag, base in [("run-i (level-off only)", "/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i"),
                  ("run-i-dive",             R)]:
    tot_desc = 0; tot_rt = 0; n = 0
    for p in sorted(glob.glob(f"{base}/next-*/seed-*/run.json")):
        j = json.load(open(p)); t = json.load(open(p.replace("run.json","terminal.json")))
        tot_desc += t["descents"]; tot_rt += j.get("runtime_s",0); n += 1
    print(f"{tag:24s} stratum-seeds={n:3d}  descents={tot_desc:,}  summed runtime={tot_rt/3600:.2f} h")
    if tot_desc: print(f"{'':24s} -> {tot_rt/tot_desc*1e6:.3f} us per descent (12 threads, wall-summed)")
j1 = json.load(open(f"{S}/run.json"))
print("\none stratum-seed:", {k: j1[k] for k in ("runtime_s","code_revision","replicates") if k in j1})
print("descents this seed:", term["descents"], "| children:", term["children"], "| parents:", term["parents"])
print(f"-> {j1['runtime_s']/term['descents']*1e6:.3f} us per descent on 12 threads "
      f"= {j1['runtime_s']*12/term['descents']*1e6:.2f} us of CPU per descent")
print("mean descent duration (onset->impact, s):", round(float(np.nansum(dur*w)/np.nansum(w)),1),
      "| integration steps at 2 s:", round(float(np.nansum(dur*w)/np.nansum(w))/2))
