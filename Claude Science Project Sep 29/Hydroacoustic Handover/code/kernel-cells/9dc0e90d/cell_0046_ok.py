eph = pd.read_csv("repo/r/Claude Science Project Sep 29/engine/data/satellite-ephemeris-inmarsat.csv")
print(eph.columns.tolist()); print(eph.tail(3).to_string())
import numpy as np
a_=6378.137; f=1/298.257223563; e2=f*(2-f)
def ecef(lat,lon,h=0):
    la,lo=np.radians(lat),np.radians(lon); N=a_/np.sqrt(1-e2*np.sin(la)**2)
    return np.array([(N+h)*np.cos(la)*np.cos(lo),(N+h)*np.cos(la)*np.sin(lo),(N*(1-e2)+h)*np.sin(la)]).T