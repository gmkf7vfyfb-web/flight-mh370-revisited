def dm(s):
    s=s.replace("°"," ").replace("'","").split(); return float(s[0])+float(s[1])/60
def hav(lat1,lon1,lat2,lon2,R=6371.0):
    import math
    p1,p2=math.radians(lat1),math.radians(lat2); dl=math.radians(lon2-lon1); dp=p2-p1
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2; return 2*R*math.asin(math.sqrt(a))
# approximate external station positions (NOT from report)
stn_ext={"H01":(-34.89,114.15),"H08S":(-7.65,72.47),"H08N":(-6.34,71.01)}
A3=(-dm("31 49.640"),dm("52 36.594")); A4s=(-dm("30 52.227"),dm("56 19.051")); ev=(-dm("30 52.227"),dm("56 19.046"))
print("A3-A4 separation km %.1f; event-to-A4sph5 km %.3f; event-to-A3 km %.1f"%(hav(*A3,*A4s),hav(*ev,*A4s),hav(*ev,*A3)))
for k,(la,lo) in stn_ext.items():
    dA4=hav(*A4s,la,lo); dA3=hav(*A3,la,lo); print(k,"dA4 %.0f dA3 %.0f  shift if at A3: %+.0f s"%(dA4,dA3,(dA3-dA4)/1.485))
def tsec(t):
    h,m,s=t.split(":"); return int(h)*3600+int(m)*60+float(s)
print(tsec("10:54:57.77")-tsec("10:23:11.56"), tsec("10:59:49.04")-tsec("10:54:57.77"))