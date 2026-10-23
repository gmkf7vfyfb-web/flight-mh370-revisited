cd pod; curl -s -m 30 -o svc.json "https://services1.arcgis.com/wfNKYeHsOyaFyPw3/arcgis/rest/services/Search_And_Rescue_Search_Area2014/FeatureServer?f=json"; curl -s -m 30 -o lyr.json "https://services1.arcgis.com/wfNKYeHsOyaFyPw3/arcgis/rest/services/Search_And_Rescue_Search_Area2014/FeatureServer/0?f=json"; curl -s -m 30 -o post.html -w "%{http_code} %{size_download}\n" "https://mh370.radiantphysics.com/2017/11/25/possible-mh370-debris-seen-in-aerial-search-in-spring-2014/"; curl -s -m 20 -o ds.html -w "ds %{http_code} %{size_download}\n" "https://www.duncansteel.com/"; python3 - <<'E'
import json
for f in ['svc.json','lyr.json']:
    d=json.load(open(f))
    for k in ['serviceDescription','description','copyrightText','name','documentInfo']:
        if k in d: print(f,k,':',str(d[k])[:500])
    if 'fields' in d: print('fields',[x['name'] for x in d['fields']])
E
grep -o -i 'duncansteel[^"]*' post.html | sort -u | head; grep -o -i 'href="[^"]*\.\(zip\|xlsx\|xls\)"' post.html | sort -u