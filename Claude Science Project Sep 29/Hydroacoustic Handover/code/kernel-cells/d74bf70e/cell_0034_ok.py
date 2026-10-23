from geographiclib.geodesic import Geodesic
import geographiclib, obspy, scipy
G = Geodesic.WGS84
cent = {"H01W":(-34.890303,114.142637),"H08S":(-7.639380,72.483828),"H08N":(-6.337533,71.002077),"H11N":(19.720514,166.899582)}
src = (-34.9167, 92.0472)
for k,(la,lo) in cent.items():
    g = G.Inverse(src[0],src[1],la,lo); b = G.Inverse(la,lo,src[0],src[1])
    print(k, f"s_km={g['s12']/1000:.4f} az_src={g['azi1']:.5f} backaz_at_station={b['azi1']:.5f}")
# core median point on arc for the composer test, near -37.225
g=G.Inverse(-37.225,88.9, *cent["H01W"]); print("core-ish", g['s12']/1000)
print(geographiclib.__version__, obspy.__version__, scipy.__version__)
