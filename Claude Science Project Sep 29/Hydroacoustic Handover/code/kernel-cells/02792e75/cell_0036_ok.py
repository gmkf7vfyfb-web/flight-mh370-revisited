for k,c in [("S1A GRD high","C1214470533-ASF"),("S1A SLC","C1214470488-ASF"),("S1A OCN","C1214472977-ASF")]:
    print(k,gran_b(c,"-180,-90,180,90","2014-04-01T00:00:00Z,2014-12-31T23:59:59Z"))
sc,v=cdse("SENTINEL-1","2014-04-01T00:00:00.000Z","2014-12-31T00:00:00.000Z","POLYGON((-180 -89,180 -89,180 89,-180 89,-180 -89))")
print("CDSE S1 2014 first",sc,len(v),[ (x["Name"][:30],x["ContentDate"]["Start"][:10]) for x in v[:3]])
# MODIS/VIIRS times
mod={k:[e["time_start"] for e in gr[k]] for k in gr if ("MODIS" in k or "VNP02" in k)}
for k,t in mod.items(): print(k,len(t),t[:2],t[-1:])