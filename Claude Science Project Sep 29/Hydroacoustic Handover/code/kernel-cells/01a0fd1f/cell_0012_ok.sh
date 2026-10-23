cd rr
curl -sIL -m 30 "https://casis.llnl.gov/content/pages/casis-2014/docs/poster/Kane1-CASIS-2014.pdf" 2>&1 | head -5; echo "exit $?"
python - <<'EOF'
import requests, datetime as dt
base="https://service.earthscope.org/fdsnws/dataselect/1/query"
res={}
for sta in ['I06H1','I04H1']:
    out=[]
    d=dt.date(2014,1,1)
    while d<=dt.date(2014,4,10):
        r=requests.get(base,params=dict(net='IM',sta=sta,cha='BDF',start=f"{d}T12:00:00",end=f"{d}T12:01:00"),timeout=60)
        out.append((str(d),r.status_code))
        d+=dt.timedelta(days=3) if d<dt.date(2014,3,25) else dt.timedelta(days=1)
    print(sta,[x for x in out])
EOF