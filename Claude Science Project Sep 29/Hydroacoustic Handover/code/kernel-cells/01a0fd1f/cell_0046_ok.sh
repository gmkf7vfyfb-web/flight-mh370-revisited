python - <<'EOF'
import requests
for net,sta,cha in [('II','COCO','BHZ'),('II','COCO','HHZ'),('G','AIS','BHZ'),('IM','H01W1','EDH'),('IM','H08S1','EDH')]:
    r=requests.get("https://service.earthscope.org/fdsnws/dataselect/1/query",params=dict(net=net,sta=sta,cha=cha,start="2014-03-08T00:20:00",end="2014-03-08T00:21:00"),timeout=60)
    print(net,sta,cha,r.status_code,len(r.content))
EOF