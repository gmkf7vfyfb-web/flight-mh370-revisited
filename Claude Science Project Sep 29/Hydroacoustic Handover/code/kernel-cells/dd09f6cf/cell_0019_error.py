import json
from shapely.geometry import shape, Point
from shapely.ops import unary_union
V={'bathy150':'f93af12c-51a4-47cb-973b-ac74388b2c82','bs30':'09b5799f-8a50-4081-b1d1-b13d51117e00','caption':'aa673b44-07d7-4b27-a9b6-5fc6c81b572d',
   'deeptow':'3df48668-3b61-404b-b5eb-466d13f66ec4','gop':'b4b0d765-6965-4ca0-9da5-adf21500fa06','dhj':'cd9b9199-5fa7-47a2-8400-190dfde657ed'}
G={}
for k,v in V.items():
    d=json.load(open(host.artifact_path(v)))
    G[k]=d
    print(k, len(d['features']), [ (f['properties'] if len(str(f['properties']))<200 else list(f['properties'].keys())) for f in d['features'][:3]])
P={'crossing':Point(101.369,-25.732),'haixun':Point(101.461,-25.975)}
for k in ['bathy150','bs30','deeptow']:
    u=unary_union([shape(f['geometry']) for f in G[k]['features']])
    print(k,'bounds',[round(x,2) for x in u.bounds], {p:u.contains(pt) for p,pt in P.items()}, {p:round(u.exterior.distance(pt) if hasattr(u,'exterior') else u.boundary.distance(pt),3) for p,pt in P.items()})