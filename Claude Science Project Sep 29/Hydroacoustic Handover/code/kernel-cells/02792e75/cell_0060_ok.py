for t in fig.texts:
    if t.get_text().startswith("Technical:"): t.set_text(t.get_text().replace("bar placed","marker placed"))
fig.savefig("out/fig-locality-imagery-timeline.png",dpi=300)
cat={"run_utc":"2026-10-18","aoi":"25-26.5 S, 100-102.5 E","window":"2014-03-08/2014-04-30 (CDSE and CSDA to 2014-05-31)",
 "results":{
  "NASA CMR MOD02QKM v6.1 (Terra MODIS 250 m)":len(mod["MODIS Terra 250m (MOD02QKM 6.1)"]),
  "NASA CMR MYD02QKM v6.1 (Aqua MODIS 250 m)":len(mod["MODIS Aqua 250m (MYD02QKM 6.1)"]),
  "NASA CMR VNP02IMG (Suomi NPP VIIRS 375 m)":len(mod["VIIRS VNP02IMG"]),
  "USGS Landsat STAC landsat-c2l1 (L7/L8)":0,"USGS Landsat STAC, locality 2013-2026":0,"USGS Landsat STAC 95-108E 20-32S Mar-Apr 2014":0,
  "USGS Landsat STAC Perth control Mar-Apr 2014":50,
  "NASA CSDA Maxar L1B (WV01, WV02, GE01, QB02, IKONOS, WV03)":0,"NASA CSDA Perth control WV02_Pan_L1B":225,
  "NASA CSDA 16 Mar 2014 WV-2 sighting scene (positive control)":0,
  "NASA CSDA WV01/WV02 records 85-110E 18-47S, 8 Mar-31 May 2014":int(len(df)),
  "ASF Sentinel-1A GRD/SLC/OCN/RAW (CMR)":0,"ASF Sentinel-1A earliest public GRD/SLC globally":"2014-06-15",
  "Copernicus Data Space SENTINEL-1":0,"Copernicus Data Space SENTINEL-1 earliest 2014 product globally":"2014-10-03",
  "Sentinel-1 first product over locality (CDSE)":"2015-05-29 (WV OCN)",
  "ASTER L1T":0,"EO-1 ALI":0,"EO-1 Hyperion":0},
 "csda_nearest_strip_km_to_first_contact":{k:float(v) for k,v in df.groupby("date")["d_haixun_km"].min().round(0).items()},
 "modis_times_utc":{k:v for k,v in mod.items()}}
json.dump(cat,open("out/catalogue_queries_2026-10-18.json","w"),indent=1,default=str)
json.dump({k:(list(v) if isinstance(v,tuple) else float(v)) for k,v in geo.items()},open("out/contact_geometry.json","w"),indent=1)
print("saved")