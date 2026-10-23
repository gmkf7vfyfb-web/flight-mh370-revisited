import numpy as np, datetime as dt
def eot_minutes(date):
    # equation of time (apparent - mean), minutes, Spencer approximation
    N=date.timetuple().tm_yday; B=2*np.pi*(N-81)/364
    return 9.87*np.sin(2*B)-7.53*np.cos(B)-1.5*np.sin(B)
def lmt_at_lat(ltdn_h,inc_deg,lat_deg):
    i=np.radians(inc_deg); phi=np.radians(lat_deg)
    x=np.arcsin(np.sin(abs(phi))/np.sin(i))      # arg of latitude from node
    dalpha=np.degrees(np.arctan(abs(np.cos(i))*np.tan(x)))  # RA offset (deg)
    sign=-1 if lat_deg<0 else +1   # descending pass going south: earlier local time
    return ltdn_h+sign*dalpha/15.0, dalpha
cases=[ # name, date, lat, lon, LTDN, inc, alt_km, published UTC (str)
 ('DigitalGlobe 16 Mar obj1',dt.date(2014,3,16),-43.9761,90.9603,10.5,98.47,767,'04:16'),
 ('Gaofen-1 18 Mar',dt.date(2014,3,18),-44.9583,90.2283,10.5,97.9,640,'not stated (\"around noon\" Beijing time = ~04:00)'),
 ('Pleiades-1A 23 Mar PHR4 (GA)',dt.date(2014,3,23),-34.5,91.3,10.5,98.19,698,'~04 (CSIRO Part III)'),
 ('Airbus 23 Mar MRSA 122 objects',dt.date(2014,3,23),-44.68,90.5,10.5,98.19,698,'not stated'),
 ('THEOS 24 Mar zone 2',dt.date(2014,3,24),-46.505,89.49,10.0,98.54,825,'03:07:56'),
 ('Japan IGS 26 Mar',dt.date(2014,3,26),-44.2833,90.9333,None,None,None,'00:00-06:00 window'),
]
out=[]
for nm,d,la,lo,ltdn,inc,alt,pub in cases:
    if ltdn is None: out.append((nm,la,lo,'—','—','—','—',pub)); continue
    lmt,da=lmt_at_lat(ltdn,inc,la)
    utc_nadir=lmt-lo/15.0
    per100=100/(111.32*np.cos(np.radians(la)))/15*60  # minutes per 100 km cross-track
    def hm(h): h%=24; return f"{int(h):02d}:{int(round((h-int(h))*60)):02d}"
    out.append((nm,la,lo,f"{lmt:.2f}",hm(lmt),hm(utc_nadir),f"{per100:.1f}",pub))
for r in out: print(r)
# check implied offset for published times
for nm,d,la,lo,ltdn,inc,alt,pub in cases:
    if pub[:2].isdigit() and ltdn:
        h,m=int(pub[:2]),int(pub[3:5]); s=int(pub[6:8]) if len(pub)>5 and pub[5]==':' else 0
        utc=h+m/60+s/3600; lmt_target=utc+lo/15
        lmt_nadir,_=lmt_at_lat(ltdn,inc,la)
        dlon=(lmt_nadir-lmt_target)*15  # nadir lon - target lon
        print(nm,'target LMT',round(lmt_target,3),'nadir LMT',round(lmt_nadir,3),'nadir-target lon deg',round(dlon,2),'km',round(dlon*111.32*np.cos(np.radians(la))))
print('EoT March 16/24 (min):',round(eot_minutes(dt.date(2014,3,16)),1),round(eot_minutes(dt.date(2014,3,24)),1))
# THEOS off-nadir geometry from incidence angle
Re=6371.0; h=825; inc_ang=np.radians(26.982451)
look=np.arcsin(Re/(Re+h)*np.sin(inc_ang)); central=inc_ang-look
print('THEOS look angle',np.degrees(look),'ground range km',Re*central)