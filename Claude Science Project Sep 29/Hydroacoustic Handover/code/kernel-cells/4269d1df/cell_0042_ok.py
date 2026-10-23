from geographiclib.geodesic import Geodesic
Gd=Geodesic.WGS84
g5=dict(lat0=-40.75,lon0=84.45028696120215,dlat=1/12,dlon=0.09760538279989782,nlat=226,nlon=210)
def snap(la,lo):
    i=int(round((la-g5['lat0'])/g5['dlat'])); j=int(round((lo-g5['lon0'])/g5['dlon']))
    nla=g5['lat0']+i*g5['dlat']; nlo=g5['lon0']+j*g5['dlon']
    return i*g5['nlon']+j, nla, nlo, Gd.Inverse(la,lo,nla,nlo)['s12']/1e3
# anchors: run J mode, and track points at 35 S and 30 S from the arclat release list
arcl=pd.read_csv(R+'arc-latitude-scan/arclat-release-points.csv')
print(arcl[(arcl.position=='track')&(arcl.arc_lat.isin([-37.0,-35.0,-30.0]))].to_string())
cr=json.load(open(host.artifact_path('ea1a2d8b-6009-4834-ad87-905df3643df4')))
print(list(cr)[:10] if isinstance(cr,dict) else cr[:2])
