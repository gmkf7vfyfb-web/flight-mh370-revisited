cd rr
python - <<'EOF'
import requests
base="https://service.earthscope.org/fdsnws/dataselect/1/query"
for sta in ['I07H1','I52H1','I06H1']:
    for d in ['2012-06-01','2013-06-01','2014-04-02','2014-04-03']:
        r=requests.get(base,params=dict(net='IM',sta=sta,cha='BDF',start=f"{d}T12:00:00",end=f"{d}T12:01:00"),timeout=60)
        print(sta,d,r.status_code)
# find first hour on 2014-04-03 for I06
for h in range(0,13,2):
    r=requests.get(base,params=dict(net='IM',sta='I06H1',cha='BDF',start=f"2014-04-03T{h:02d}:00:00",end=f"2014-04-03T{h:02d}:01:00"),timeout=60)
    print('I06 04-03',h,r.status_code)
EOF
curl -sL -m 60 -o kane.pdf "http://archive.org/wayback/available?url=casis.llnl.gov/content/pages/casis-2014/docs/poster/Kane1-CASIS-2014.pdf"; echo "$?"; cat kane.pdf | head -c 600