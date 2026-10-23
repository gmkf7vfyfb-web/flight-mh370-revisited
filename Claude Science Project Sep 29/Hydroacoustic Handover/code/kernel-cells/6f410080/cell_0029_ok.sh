python - <<'EOF'
import requests,json
cids={'Terra MODIS MOD021KM C6.1':'C1378227407-LAADS','Aqua MODIS MYD021KM C6.1':'C1379758607-LAADS','Suomi-NPP VIIRS VNP02IMG v2':'C2105091501-LAADS'}
out={}
for k,cid in cids.items():
    g=requests.get('https://cmr.earthdata.nasa.gov/search/granules.json',params={'collection_concept_id':cid,'temporal':'2014-03-07T16:00:00Z,2014-03-08T06:00:00Z','bounding_box':'80,-45,110,0','page_size':200,'sort_key':'start_date'},timeout=60)
    es=g.json()['feed']['entry']
    out[k]=[(e['producer_granule_id'],e['time_start'],e['time_end'],e.get('day_night_flag'),(e.get('polygons') or [[None]])[0][0][:120] if e.get('polygons') else e.get('boxes')) for e in es]
    print('##',k,len(es))
    for x in out[k]: print(x[0],x[1],x[2],x[3])
json.dump(out,open('handoff/cmr_granules.json','w'),indent=1)
EOF