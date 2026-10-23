python - <<'EOF'
import requests
for t in ['INS_Kohassa','Car_Nicobar_Air_Force_Station','INS_Baaz','INS_Utkrosh','INS_Kardip']:
    try:
        r=requests.get('https://en.wikipedia.org/w/api.php',params=dict(action='query',prop='coordinates|revisions',titles=t,format='json',rvprop='timestamp'),timeout=30,headers={'User-Agent':'research-script/1.0'})
        p=list(r.json()['query']['pages'].values())[0]; print(t,p.get('coordinates'),p.get('revisions',[{}])[0].get('timestamp'))
    except Exception as e: print(t,'ERR',str(e)[:150])
EOF