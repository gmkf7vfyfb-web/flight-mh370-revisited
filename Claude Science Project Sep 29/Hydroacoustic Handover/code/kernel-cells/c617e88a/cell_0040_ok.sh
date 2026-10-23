W=$PWD; cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare; W=$W PYTHONPATH=. OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python - <<'E' 2>&1 | tail -30
import json, os, numpy as np, pandas as pd
import imos_coincidence as IC, imos_preregistration as P, imos_detectors as D
meta=P.parse_meta(); cal=IC.cal_for(meta)
thr_all=json.loads((IC.HERE/"results-data/stageA/summary_union.json").read_text())["thresholds"]
thr={3376:thr_all["3376"],3274:thr_all["3274"],3315:thr_all["3376"],3275:thr_all["3274"]}
mh=pd.read_csv(IC.HERE/"results-data/imos2b/mh370_windows.csv",parse_dates=["win_a","win_b"])
win={int(c):((g.win_a.iloc[0]-D.DAY0).total_seconds(),(g.win_b.iloc[0]-D.DAY0).total_seconds()) for c,g in mh.groupby("logger")}
recs=pd.read_csv(IC.HERE/"data/imos/recordings.csv",parse_dates=["start_logger"])
out={}
for cid in [3315,3376,3274,3275]:
    a,b=win[cid]; segs=[]; allsegs=[]; evs={"loose":[],"strict":[]}
    for f in recs[recs.logger==cid].file:
        r=IC.rec_events(P.IMOS/f,cid,meta,cal,thr[cid])
        if r is None: continue
        s0,s1,ev=r; allsegs.append([s0+32,s1])
        lo,hi=max(s0+32,a),min(s1,b)
        if hi>lo:
            segs.append([lo,hi])
            for op in evs: evs[op]+= [(t,v) for t,v in ev[op] if lo<=t<=hi]
    out[cid]=dict(window=[a,b],scored_segments=segs,covered_s=sum(h-l for l,h in segs),recorded_segments=allsegs,events=evs)
    print(cid, round(out[cid]["covered_s"],1), len(allsegs), {k:[(str(D.DAY0+pd.Timedelta(seconds=t))[11:19],round(v,2)) for t,v in e] for k,e in evs.items()})
open(os.environ["W"]+"/work/imos_events_searched.json","w").write(json.dumps({str(k):v for k,v in out.items()},indent=1))
E