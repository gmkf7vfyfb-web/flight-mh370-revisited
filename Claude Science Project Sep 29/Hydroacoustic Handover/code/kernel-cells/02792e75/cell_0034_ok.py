def gran_b(cid,bb,temporal):
    r=requests.get(CMR+"/granules.json",params={"bounding_box":bb,"temporal":temporal,"page_size":5,"collection_concept_id":cid,"sort_key":"start_date"},timeout=120)
    e=r.json()["feed"]["entry"]; return int(r.headers.get("CMR-Hits",-1)), [x.get("time_start") for x in e[:3]]
print("L8 Perth control",gran_b("C3442493460-USGS_EROS","115,-33,117,-31",tq))
print("L8 locality any time 2013-2026",gran_b("C3442493460-USGS_EROS",bbox,"2013-03-01T00:00:00Z,2026-10-01T00:00:00Z"))
print("S1A GRD world Apr 2014",gran_b("C1214470533-ASF","-180,-90,180,90","2014-04-03T00:00:00Z,2014-04-30T23:59:59Z"))
print("S1A OCN world Apr-May 2014",gran_b("C1214472977-ASF","-180,-90,180,90","2014-04-03T00:00:00Z,2014-05-31T23:59:59Z"))
print("S1A OCN locality to 2015",gran_b("C1214472977-ASF",bbox,"2014-04-03T00:00:00Z,2015-12-31T23:59:59Z"))
print("ASTER locality any",gran_b("C3306888411-LPCLOUD",bbox,"2000-01-01T00:00:00Z,2026-10-01T00:00:00Z"))