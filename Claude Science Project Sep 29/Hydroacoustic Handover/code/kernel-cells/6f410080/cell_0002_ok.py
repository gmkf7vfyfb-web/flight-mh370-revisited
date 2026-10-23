import re
kw=re.compile(r'satellite imag|imagery|WorldView|DigitalGlobe|Gaofen|THEOS|Thai|Japan|Pl[eé]iades|PLEIADES|French satellite|Chinese satellite|GISTDA|CRESDA|JAXA|Tomnod|SPOT|COSMO|TerraSAR|RADARSAT|Sentinel|DIGO|AGO|Defence Imagery|Geospatial-Intelligence',re.I)
for k in ['opsearch','amsa','sir','factual','marghany','guardian']:
    t=open(f'handoff/{k}.txt').read()
    hits=[m.start() for m in kw.finditer(t)]
    print(k,len(hits))
