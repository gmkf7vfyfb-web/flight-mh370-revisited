cd /tmp && python - <<'EOF'
import requests
r=requests.get('https://cmr.earthdata.nasa.gov/search/granules.json',params={'short_name':'MOD021KM','temporal':'2014-03-07T18:00:00Z,2014-03-08T01:00:00Z','bounding_box':'80,-45,110,0','page_size':200},timeout=60)
print(r.status_code)
j=r.json(); es=j['feed']['entry']; print(len(es))
for e in es[:5]: print(e['producer_granule_id'],e['time_start'],e.get('day_night_flag'))
EOF