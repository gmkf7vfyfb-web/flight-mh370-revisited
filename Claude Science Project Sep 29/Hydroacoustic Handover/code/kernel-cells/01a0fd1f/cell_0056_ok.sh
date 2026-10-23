python - <<'EOF'
import requests,re
for t in ['INS_Kohassa','Car_Nicobar_Air_Force_Station','INS_Baaz','INS_Utkrosh','INS_Kardip','Andaman_and_Nicobar_Command']:
    r=requests.get('https://en.wikipedia.org/w/api.php',params=dict(action='query',prop='coordinates|extracts',explaintext=1,titles=t,format='json',redirects=1),timeout=30,headers={'User-Agent':'research-script/1.0'})
    p=list(r.json()['query']['pages'].values())[0]; ex=p.get('extract','')
    print('##',t,p.get('coordinates'))
    for m in re.finditer(r'[^.\n]*(radar|Radar)[^.\n]*\.',ex): print('   ',m.group(0).strip()[:300])
EOF