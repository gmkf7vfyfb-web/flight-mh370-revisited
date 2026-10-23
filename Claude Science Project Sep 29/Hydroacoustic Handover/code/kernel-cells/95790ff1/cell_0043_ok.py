def norm_rcv(r):
    r=str(r)
    for k in ["H08N","H08S","H01","H04N","H04S"]:
        if r.startswith(k): return k
    if "Diego Garcia IMS" in r: return "H08 (subarray unspecified)"
    if "IMS" in r: return "all IMS"
    return r
srcmap={"A4 SUS (two charges)":"A4sus3; A4sus2","A8 SUS 610 m":"A8sus2 or A8sus2b (not specified)","A11 SUS 915 m":"A11sus","A11 five-sphere cluster":"A11sph5"}
diffs=[]
for i,r in dr.iterrows():
    sid=srcmap.get(r.source_id,r.source_id); rc=norm_rcv(r.receiver)
    m=ro[(ro.event_id==sid)]
    if rc in("H08N","H08S","H01","H04N","H04S"): mm=m[m.receiver==rc]
    elif rc=="all IMS": mm=m
    else: mm=m
    news="; ".join(sorted(set(f"{a}:{b}:{c}" for a,b,c in zip(mm.receiver,mm.analysis.str.split(" ").str[0],mm.status)))) or "NO MATCHING ROW"
    diffs.append(dict(drive_row=i+2,drive_source_id=r.source_id,drive_receiver=r.receiver,drive_status=r.status,drive_range_km=r.source_receiver_range_km,new_rows=news))
dd=pd.DataFrame(diffs)
print(dd[["drive_row","drive_source_id","drive_receiver","drive_status","drive_range_km","new_rows"]].to_string())