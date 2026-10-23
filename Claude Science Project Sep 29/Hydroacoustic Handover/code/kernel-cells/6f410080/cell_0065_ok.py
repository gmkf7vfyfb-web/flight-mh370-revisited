def gc(a,b):
    la1,lo1,la2,lo2=map(np.radians,[a[0],a[1],b[0],b[1]])
    return 6371.0*2*np.arcsin(np.sqrt(np.sin((la2-la1)/2)**2+np.cos(la1)*np.cos(la2)*np.sin((lo2-lo1)/2)**2))
P={'WV obj1 16Mar':(-(43+58/60+34/3600),90+57/60+37/3600),'WV obj2 16Mar':(-(44+3/60+2/3600),91+13/60+27/3600),
   'GF1 18Mar':(-(44+57/60),90+13/60),'MRSA 23Mar centroid':(-44.680,90.52),'THEOS 24Mar zone2':(-46.505,89.49),
   'IGS 26Mar centre':(-(44+17/60),90+56/60),'Perth':(-31.95,115.86)}
ks=list(P)
for i,a in enumerate(ks):
    print(a, {b:round(gc(P[a],P[b])) for b in ks if b!=a})
lat=np.array([r[3] for r in []])
import pandas as pd
m=pd.read_csv('mrsa_23mar2014_objects.csv'); print(m.lat_deg.mean(),m.lon_deg.mean(), m.lat_deg.min(),m.lat_deg.max(),m.lon_deg.min(),m.lon_deg.max())