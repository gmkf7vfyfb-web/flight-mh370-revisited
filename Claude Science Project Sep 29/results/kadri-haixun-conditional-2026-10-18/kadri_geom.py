import numpy as np, json
from geographiclib.geodesic import Geodesic
G=Geodesic.WGS84
C=299792.458
GES=np.array([-2368.8,4881.1,-3342.0]); OFF=499962.0-4283.0
SAT={'m0019a':np.array([18178.3537,38050.8487,393.0782]),'m0019b':np.array([18178.3656,38050.8362,392.4131])}
a=6378.137; f=1/298.257223563; e2=f*(2-f)
def ecef(lat,lon,h):
    la,lo=np.radians(lat),np.radians(lon); N=a/np.sqrt(1-e2*np.sin(la)**2)
    return np.array([(N+h)*np.cos(la)*np.cos(lo),(N+h)*np.cos(la)*np.sin(lo),(N*(1-e2)+h)*np.sin(la)])
def bto(lat,lon,h,ep='m0019a'):
    s=SAT[ep]; return 2*(np.linalg.norm(s-ecef(lat,lon,h))+np.linalg.norm(s-GES))/C*1e6-OFF
H01=(-34.8903,114.1426); AZ=306.18
line=G.Line(H01[0],H01[1],AZ)
def pos(s): p=line.Position(s*1e3); return p['lat2'],p['lon2']
def cross(target,h=0.0,ep='m0019a',az=AZ):
    L=G.Line(H01[0],H01[1],az)
    f=lambda s: bto(*[L.Position(s*1e3)[k] for k in('lat2','lon2')],h,ep)-target
    lo,hi=1200.,1900.
    for _ in range(60):
        m=(lo+hi)/2
        if f(lo)*f(m)<=0: hi=m
        else: lo=m
    p=L.Position(m*1e3); return m,p['lat2'],p['lon2']
out={}
for lab,tg,ep,h in [('sea level R600 18400',18400,'m0019a',0),('R600 +1sigma 18463',18463,'m0019a',0),('R600 -1sigma 18337',18337,'m0019a',0),('sea level R1200 18380',18380,'m0019b',0),('FL350 R600',18400,'m0019a',35000*0.0003048)]:
    s,la,lo=cross(tg,h,ep); out[lab]=(round(s,1),round(la,3),round(lo,3)); print(f"{lab:26s} R={s:7.1f} km  {la:8.3f} {lo:8.3f}")
for daz in (-1.0,-0.5,0.5,1.0):
    s,la,lo=cross(18400,0,'m0019a',AZ+daz); print(f"az {AZ+daz:.2f}: R={s:.1f} {la:.3f} {lo:.3f}")
# Kadri's R7=1586 position and its BTO
la,lo=pos(1586); print("Kadri R7 1586 km point",round(la,3),round(lo,3),"BTO there",round(bto(la,lo,0),1),"us (obs 18400)")
hx=(-25.975,101.461); print("Haixun BTO at sea level",round(bto(*hx,0),1))
R7=out['sea level R600 18400'][0]
# Kadri timing check
t7=19*60+29
for name,trec in [('text 00:52:03',52*60+3),('caption 00:54:30',54*60+30),('Kadri used 00:54:00',54*60)]:
  for c in (1.48,1.50):
    for R in (R7,1586.0):
        dt=(trec-t7)-R/c   # extra time beyond direct arc-time propagation, s
        print(f"{name:18s} c={c} R7={R:.0f}: arc-to-H01W {R/c/60:.2f} min, total {(trec-t7)/60:.2f} min, extra dt {dt/60:.2f} min")
# Impact solutions along bearing: impact at range R7+dr, time t7+dT, with dr=v*dT  (Kadri eq 4)
print("\nimpact along bearing (sea-level arc, c=1.48): v m/s -> dT min, dr km, impact time, lat lon")
for name,trec in [('text',52*60+3),('caption',54*60+30)]:
  dt=(trec-t7)-R7/1.48
  for v in (0.0,100,150,200,250):
    vk=v/1000; dT=dt/(1+vk/1.48); dr=vk*dT
    la,lo=pos(R7+dr); ti=t7+dT
    print(f"  {name:7s} v={v:5.0f}: dT={dT/60:5.2f} min dr={dr:6.1f} km impact 00:{int(ti//60):02d}:{int(ti%60):02d} at {la:.3f} {lo:.3f}")
# Haixun as source: required source time
dH=G.Inverse(H01[0],H01[1],*hx)['s12']/1e3
for name,trec in [('text',52*60+3),('caption',54*60+30)]:
  for c in (1.47,1.48,1.49):
    ts=trec-dH/c; print(f"Haixun-as-source {name} c={c}: source time 00:{int(ts//60):02d}:{int(ts%60):02d}, {(ts-t7)/60:.1f} min after 00:19:29, dist from arc crossing {G.Inverse(*pos(R7),*hx)['s12']/1e3:.1f} km")
json.dump(out,open('kadri_geom.json','w'),indent=1)
