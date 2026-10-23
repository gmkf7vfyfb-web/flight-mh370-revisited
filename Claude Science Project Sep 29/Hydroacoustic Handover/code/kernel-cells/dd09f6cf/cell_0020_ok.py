from shapely.validation import make_valid
for k in ['bathy150','bs30']:
    p=G[k]['features'][0]['properties']
    print(k,{x:p[x] for x in ['TITLE','PLATFORM_N','SENSORS','START_DATE','END_DATE','DATA_URL','META_URL','AREA_KM2','GAID','LEGAL_CONS']})
for f in G['caption']['features']:
    p=f['properties']; print(p['id'],'|',p['name'],'|',p['lat_min'],p['lat_max'],'|',p['area_km2_wgs84_sum_of_rings'],'|',p['source_grade'],'|',p['status'],'|',str(p['note'])[:150])