for u in "https://mh370.radiantphysics.com/2017/11/25/possible-mh370-debris-seen-in-aerial-search-in-spring-2014/" "https://www.duncansteel.com/archives/2154" "https://www.duncansteel.com/" "https://services1.arcgis.com/wfNKYeHsOyaFyPw3/arcgis/rest/services/Search_And_Rescue_Search_Area2014/FeatureServer?f=json" "https://services1.arcgis.com/wfNKYeHsOyaFyPw3/arcgis/rest/services/Search_And_Rescue_Search_Area2014/FeatureServer/0?f=json"; do echo "$u -> $(curl -s -o /tmp/x -m 25 -w '%{http_code} %{size_download}' "$u")"; done; python3 - <<'E'
import json
d=json.load(open('/tmp/x'))
for k in ['name','description','copyrightText','serviceDescription','fields']:
    v=d.get(k); print(k,':',(str(v)[:400] if k!='fields' else [f['name'] for f in v]))
E