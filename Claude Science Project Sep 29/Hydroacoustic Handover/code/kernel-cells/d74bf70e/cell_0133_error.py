from pyproj import Geod
G=Geod(ellps="WGS84")
st={"H01W":(-34.890303,114.142637),"H08S":(-7.639380,72.483828),"H08N":(-6.337533,71.002077)}
for s in ["air9","air8"]:
    r=sl[sl.site==s]; la=r[["start_lat_dd","end_lat_dd"]].values.mean(); lo=r[["start_lon_dd","end_lon_dd"]].values.mean()
    print(s, round(la,4), round(lo,4), {k:round(G.inv(lo,la,v[1],v[0])[2]/1000,1) for k,v in st.items()})