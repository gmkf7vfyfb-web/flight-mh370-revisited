cd "./.tmp/repo/ISO Sept 28 Status/results/worktree-hydroacoustics/hydroacoustics"; python3 - <<'EOF'
import json
from datetime import datetime as D, timedelta as T
k=json.load(open('kadri-tests/kadri-tests.json'))
imp={'F-35A':'10:26:30','Yemenia 626':'22:50:00','Sriwijaya 182':'07:40:00','Air France 447':'02:14:00','Transair 810':'11:46:00','Lion Air 904':'07:10:00'}
panel={('F-35A','H11N'):'10:58',('F-35A','H11S'):'10:59',('Sriwijaya 182','H08S'):'08:06',('Yemenia 626','H08S'):'23:27',('Yemenia 626','H08N'):'23:29'}
f=lambda s:D.strptime(s,'%H:%M:%S' if s.count(':')==2 else '%H:%M')
rows=[]
for r in k['loudness']:
    c,s,R=r['crash'],r['station'],r['range_km']
    t0=f(imp[c]); lo=t0+T(seconds=R/1.52); hi=t0+T(seconds=R/1.45)
    p=panel.get((c,s)); pm = (f(p)+T(minutes=5)).strftime('%H:%M:%S') if p else None
    off_mid = ((f(p)+T(minutes=5))-(t0+T(seconds=R/1.485))).total_seconds()/60 if p else None
    print(f"{c:15s} {s:5s} R={R:5d} impact {imp[c]} pred {lo:%H:%M:%S}-{hi:%H:%M:%S} | S1panel {p} mid {pm} mid-pred(1.485) {off_mid if off_mid is None else round(off_mid,1)} | prior-session transient {r['figure_transient_utc']} off {r['timing_offset_min']} min")
EOF