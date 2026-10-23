export HOME=$PWD/home XDG_CONFIG_HOME=$PWD/home/.config
cd repo; git sparse-checkout add "/ISO Sept 28 Status/inputs/search-coverage/" 2>&1|tail -1
ls -la "ISO Sept 28 Status/inputs/search-coverage/"
python3 -c "
import json;d=json.load(open('ISO Sept 28 Status/inputs/search-coverage/ocean-infinity-2018-outline.geojson'))
print({k:v for k,v in d.items() if k!='features'}); 
for f in d['features']: print(f['properties'], f['geometry']['type'])"
grep -n -i 'ocean infinity\|2018\|northern\|25 S\|weekly' "Claude Science Project Sep 29/results/seabed-search-references.md" | cut -c1-400 | head -40