cd rr
curl -sL -m 60 "https://api.datacite.org/dois?query=OHASISBIO&page%5Bsize%5D=50" -o dc.json; echo "$? $(wc -c < dc.json)"
python - <<'EOF'
import json
d=json.load(open('dc.json'))
for x in d.get('data',[]):
    a=x['attributes']; print(a['doi'],'|',a.get('publicationYear'),'|',(a.get('titles') or [{}])[0].get('title','')[:110],'|',a.get('types',{}).get('resourceTypeGeneral'))
EOF