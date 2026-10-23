cd /tmp && python - <<'EOF'
import requests,json
out={}
for sn in ['MOD021KM','MYD021KM','VNP02IMG','VNP02MOD','MOD03','MYD03','VNP03IMG']:
    r=requests.get('https://cmr.earthdata.nasa.gov/search/collections.json',params={'short_name':sn},timeout=60)
    cols=[(c['id'],c.get('version_id'),c.get('data_center')) for c in r.json()['feed']['entry']]
    print(sn,cols)
    for cid,ver,dc in cols:
        g=requests.get('https://cmr.earthdata.nasa.gov/search/granules.json',params={'collection_concept_id':cid,'temporal':'2014-03-07T18:00:00Z,2014-03-08T01:00:00Z','bounding_box':'80,-45,110,0','page_size':200,'sort_key':'start_date'},timeout=60)
        es=g.json()['feed']['entry']
        out[f'{sn} v{ver}']=[(e['producer_granule_id'],e['time_start'],e['time_end'],e.get('day_night_flag'),e.get('boxes') or e.get('polygons')) for e in es]
        print('  ',ver,len(es))
json.dump(out,open('/tmp/cmr_granules.json','w'))
EOF
cp /tmp/cmr_granules.json handoff/ 2>/dev/null; ls -la handoff/cmr_granules.json