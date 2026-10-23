from geographiclib.geodesic import Geodesic
g=Geodesic.WGS84.Inverse(-6.337533,71.002077,-7.639380,72.483828); print(g["s12"]/1000)