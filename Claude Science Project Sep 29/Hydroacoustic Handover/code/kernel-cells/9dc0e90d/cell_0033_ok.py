import numpy as np
def gc(lat1,lon1,lat2,lon2):
    R=6371.0088; p1,p2=np.radians(lat1),np.radians(lat2); dl=np.radians(lon2-lon1)
    a=np.sin((p2-p1)/2)**2+np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
    return 2*R*np.arcsin(np.sqrt(a))/1.852  # NM
# MEKAR, 18:22 point ~10 NM past MEKAR on 296 deg track, NILAM, IGOGU, ANOKO
mek=(6.5038889,96.4911111)
b=np.radians(296.1); d=10/60
p1822=(mek[0]+d*np.cos(b), mek[1]+d*np.sin(b)/np.cos(np.radians(mek[0])))
pts={'18:22 (10 NM past MEKAR)':p1822,'NILAM':(6.7563889,95.9766667),'ANOKO':(7.1361111,94.4161111),'IGOGU':(7.5169444,94.4166667),'NW tip Sumatra (5.6N 95.0E, approx)':(5.6,95.0)}
sites={'INS Baaz, Campbell Bay':(7.01306,93.92361),'Car Nicobar AFS':(9.1525,92.8196),'Port Blair':(11.64111,92.72972),'INS Kohassa, Diglipur':(13.237982,93.049944),'Lhokseumawe (Indonesia, approx 5.2N 97.1E)':(5.2,97.1),'Sabang (Indonesia, approx 5.9N 95.3E)':(5.9,95.3)}
hor = 1.23*np.sqrt(35000)
print(f"radar horizon FL350, antenna at sea level: {hor:.0f} NM; +100 ft antenna: {1.23*(np.sqrt(35000)+10):.0f} NM")
import pandas as pd
df=pd.DataFrame({s:{p:round(gc(*sv,*pv)) for p,pv in pts.items()} for s,sv in sites.items()}).T
print(df.to_string())