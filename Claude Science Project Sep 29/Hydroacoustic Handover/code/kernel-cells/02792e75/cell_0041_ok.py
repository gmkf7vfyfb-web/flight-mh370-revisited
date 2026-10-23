names=["WORLDVIEW-1","WORLDVIEW-2","WORLDVIEW-3","GEOEYE 1","QUICKBIRD 2","IKONOS 2","PLEIADES 1A","PLEIADES 1B","SPOT 5","SPOT 6","SPOT 7","THEOS","GAOFEN-1","ZIYUAN 3","TERRASAR-X","TANDEM-X","COSMO-SKYMED 1","COSMO-SKYMED 2","COSMO-SKYMED 3","COSMO-SKYMED 4","RADARSAT-2","RISAT-1","SENTINEL-1A","LANDSAT 7","LANDSAT 8","TERRA","AQUA","SUOMI NPP","ALOS-2","KOMPSAT-2","KOMPSAT-3","KOMPSAT-5","DEIMOS-1","UK-DMC 2","RESURS-P1","YAOGAN 21","GAOFEN-2"]
sat={}
for n in names:
    try:
        r=requests.get("https://celestrak.org/satcat/records.php",params={"NAME":n,"FORMAT":"json"},timeout=40)
        j=r.json() if r.ok and r.text.strip().startswith("[") else []
        j=[x for x in j if x.get("OBJECT_TYPE")=="PAY"]
        sat[n]=[(x["OBJECT_NAME"],x["NORAD_CAT_ID"],x["OBJECT_ID"],x["LAUNCH_DATE"],x.get("DECAY_DATE"),x.get("INCLINATION"),x.get("APOGEE"),x.get("PERIGEE")) for x in j][:3]
    except Exception as e: sat[n]=str(e)[:80]
for k,v in sat.items(): print(k,v)