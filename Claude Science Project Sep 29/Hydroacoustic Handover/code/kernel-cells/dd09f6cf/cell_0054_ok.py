from geographiclib.geodesic import Geodesic
GG=Geodesic.WGS84
line=GG.Line(-34.8903,114.1426,306.18)
ss=np.arange(1400,1900,0.5)
pts=[line.Position(s*1e3) for s in ss]; la_b=np.array([p['lat2'] for p in pts]); lo_b=np.array([p['lon2'] for p in pts])
oi=cov['ocean-infinity-2018']
def rv(c,la,lo):
    i=np.floor((la-c['s'])/c['st']).astype(int); j=np.floor((lo-c['w'])/c['st']).astype(int)
    ok=(i>=0)&(i<c['R'])&(j>=0)&(j<c['C']); out=np.zeros(la.size); out[ok]=c['a'][i[ok],j[ok]]; return out
cv=rv(oi,la_b,lo_b)
inn=ss[cv>0.5]; print('OI2018 raster along bearing: range %.1f..%.1f km -> relative to R7 %.1f..%.1f km'%(inn.min(),inn.max(),inn.min()-1591.3,inn.max()-1591.3))
poly_oi=make_valid(shape(oi_t['geometry']))
from shapely.geometry import LineString
seg=LineString(list(zip(lo_b,la_b))).intersection(poly_oi)
bth=make_valid(shape(G['bathy150']['features'][0]['geometry'])); bs=make_valid(shape(G['bs30']['features'][0]['geometry']))
def ranges(geom):
    out=[]
    for g in getattr(geom,'geoms',[geom]):
        cs=np.array(g.coords); 
        r=[GG.Inverse(-34.8903,114.1426,y,x)['s12']/1e3 for x,y in cs[[0,-1]]]; out.append((round(min(r)-1591.3,1),round(max(r)-1591.3,1)))
    return out
print('OI tracing polygon along bearing (km rel R7):',ranges(seg))
print('Phase1 bathy along bearing:',ranges(LineString(list(zip(lo_b,la_b))).intersection(bth)))
print('Phase1 30m backscatter along bearing:',ranges(LineString(list(zip(lo_b,la_b))).intersection(bs)))
# Haixun 2 km disc coverage
from shapely.geometry import Point as Pt
th=np.linspace(0,2*np.pi,72); rr=np.sqrt(np.random.default_rng(0).random(400))*2.0; tt=np.random.default_rng(1).random(400)*2*np.pi
hl=-25.975+rr*np.sin(tt)/111.2; ho=101.461+rr*np.cos(tt)/(111.2*np.cos(np.radians(25.975)))
print('OI2018 coverage in Haixun 2 km disc: min %.3f mean %.3f'%(rv(oi,hl,ho).min(),rv(oi,hl,ho).mean()))
print('Haixun in bathy150:',bth.contains(Pt(101.461,-25.975)),'in bs30:',bs.contains(Pt(101.461,-25.975)),'dist bs30 km %.1f'%(bs.distance(Pt(101.461,-25.975))*111*np.cos(np.radians(26))))
print('crossing dist to bathy150 edge km %.2f, to bs30 %.2f'%(bth.distance(Pt(101.369,-25.732))*100, bs.distance(Pt(101.369,-25.732))*100))