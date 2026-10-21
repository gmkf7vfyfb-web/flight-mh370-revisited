"""Exact session code for the geostationary-imager study (7-8 Mar 2014): HRIT and CEReS readers, scan-crossing
solver and crossing-table builder, copied with inspect.getsource from the analysis kernel. Companion of geogeom.py
(imported as gg) and satgeom.py (imported as sg).

Session globals used: SATREC (name -> sgp4 Satrec from space-track element sets nearest 20:00 UTC 7 Mar 2014,
Hugging Face juliensimon/space-track-tle-history tle_2014.parquet), T0 = 2014-03-07 18:01:49 UTC, ALL (148000 x 38 x
[lat, lon] core run J routes, 600 s spacing), tv = 600*arange(38), WT (route weight = family weight / routes in family),
radar_pos(tsec) and rdt (GA radar track 'Data-Cleaned-Estim-Time'), EV (scan-event table), H_FL = 10.668 km,
YN = -8.8, YS = 8.8 (CGMS line angle of north/south disc edge), LPD = 10233128/65536 lines per degree,
spl = 0.57982085 s/line (MTSAT-2 HRIT 17:32 header). solve_event returns tc (s after T0; NaN where the scan
does not cover the aircraft), lat, lon, VZA (deg), slant range (km) and the satellite ECEF position at mid-scan.
read_mtsat_gridded2 reads geo/raw/mt2g/<stamp>.ir.tar.bz2 (CEReS gridded V2.0); read_hrit_tar reads CEReS FY-2D HRIT tars.
"""
import re, struct, tarfile, json
import numpy as np, pandas as pd
import geogeom as gg


YN, YS = -8.8, 8.8
LPD = 10233128/65536
spl = 0.57982085
H_FL = 10.668

def hrit_headers(b):
    # primary header
    assert b[0]==0
    total=struct.unpack('>I',b[4:8])[0]
    hdrs={}; p=0
    while p<total:
        t=b[p]; L=struct.unpack('>H',b[p+1:p+3])[0]
        hdrs.setdefault(t,[]).append(b[p+3:p+L]); p+=L
    return total,hdrs


def mjd2ts(m): return pd.Timestamp('1858-11-17',tz='UTC')+pd.to_timedelta(m,unit='D')


def hrit_file_info(raw):
    total,h=hrit_headers(raw)
    nb,nc,nl=struct.unpack('>BHH',h[1][0][:5])
    nav=h[2][0]; proj=nav[:32].decode().strip(); cfac,lfac,coff,loff=struct.unpack('>iiii',nav[32:48])
    seg = struct.unpack('>BBH',h[128][0][:4]) if 128 in h else None
    ob=[]
    if 131 in h:
        ob=[(int(a),float(b)) for a,b in re.findall(r'LINE:=(\d+)\s*TIME:=([\d.]+)',h[131][0].decode('ascii','ignore'))]
    return dict(total=total,nb=nb,nc=nc,nl=nl,proj=proj,cfac=cfac,lfac=lfac,coff=coff,loff=loff,seg=seg,obs=ob,keys=sorted(h),h=h)


def read_hrit_tar(path):
    tf=tarfile.open(path); segs=[]
    for n in sorted(tf.getnames()):
        if not re.search(r'_\d{3}$',n): continue
        raw=tf.extractfile(n).read(); fi=hrit_file_info(raw)
        data=np.frombuffer(raw[fi['total']:],dtype='>u2' if fi['nb']==16 else 'u1')[:fi['nc']*fi['nl']].reshape(fi['nl'],fi['nc'])
        segs.append((fi,data))
    fi0=segs[0][0]
    img=np.concatenate([d for f,d in segs],0)
    txt=fi0['h'][3][0].decode('ascii','ignore')
    pairs=re.findall(r'(\d+):=([\d.]+)',txt); c=np.array([int(a) for a,b in pairs]); v=np.array([float(b) for a,b in pairs])
    comp=struct.unpack('>BHHB',fi0['h'][1][0][:6])[3] if len(fi0['h'][1][0])>=6 else None
    return img,c,v,fi0,comp


def geos_pix2ll(lines, cols, sub_lon, cfac, lfac, coff, loff):
    """CGMS LRIT/HRIT Global Spec 4.4 inverse navigation (lines/cols 1-based)."""
    x=np.radians((cols-coff)*65536.0/cfac); y=np.radians((lines-loff)*65536.0/lfac)
    h=42164.0; r_eq=6378.169; r_pol=6356.5838
    cx,cy,sx,sy=np.cos(x),np.cos(y),np.sin(x),np.sin(y)
    q=cy**2+(r_eq**2/r_pol**2)*sy**2
    sd2=(h*cx*cy)**2-q*(h**2-r_eq**2)
    sd=np.sqrt(np.where(sd2>=0,sd2,np.nan))
    sn=(h*cx*cy-sd)/q
    s1=h-sn*cx*cy; s2=sn*sx*cy; s3=-sn*sy; sxy=np.hypot(s1,s2)
    lon=np.degrees(np.arctan(s2/s1))+sub_lon
    lat=np.degrees(np.arctan((r_eq**2/r_pol**2)*s3/sxy))
    return lat,lon


def parse_cal(txt):
    blk=txt.split('Data_Definition_Block')[1]
    pairs=re.findall(r'^(\d+):=([\d.]+)',blk,flags=re.M)
    c=np.array([int(a) for a,b in pairs]); v=np.array([float(b) for a,b in pairs]); return c,v


def read_mtsat_gridded2(stamp, chans=('IR1','IR2'), box=(-50,15,80,120)):
    tf=tarfile.open(f'geo/raw/mt2g/{stamp}.ir.tar.bz2'); out={}
    names=tf.getnames(); lat=59.98-0.04*np.arange(3000); lon=80.02+0.04*np.arange(3000)
    iy=np.where((lat>=box[0])&(lat<=box[1]))[0]; ix=np.where((lon>=box[2])&(lon<=box[3]))[0]
    for ch in chans:
        g=[n for n in names if n.endswith('.geoss') and f'{ch}_' in n][0]
        d=np.frombuffer(tf.extractfile(g).read(),dtype='>i2').reshape(3000,3000)
        h=[n for n in names if n.startswith(f'hdr_{ch.lower()}_') and n.endswith('_001.txt')][0]
        c,v=parse_cal(tf.extractfile(h).read().decode())
        sub=d[np.ix_(iy,ix)].astype(float); tb=np.interp(sub,c,v); tb[(sub<=0)|(sub>c.max())]=np.nan
        out[ch]=tb.astype(np.float32); out['sector']=g.split('_')[1]
    return lat[iy],lon[ix],out


def solve_event(e, which):
    s=SATREC[e.sat]; t0s=(e.t_first-T0).total_seconds()
    se=gg.sat_ecef_series(sg,s,pd.DatetimeIndex([e.t_first+pd.Timedelta(seconds=e.dur_s/2)]))[0]
    yc=np.degrees(np.arcsin(se[2]/np.linalg.norm(se)))   # Earth centre line angle (CGMS sign)
    n=len(ALL) if which=='routes' else 1
    tc=np.full(n, t0s)
    for it in range(4):
        if which=='routes':
            tq=np.clip(tc,0,tv[-1]); k=np.minimum((tq//600).astype(int),36); f=(tq-k*600)/600; ii=np.arange(n)
            la=ALL[ii,k,0]*(1-f)+ALL[ii,k+1,0]*f; lo=ALL[ii,k,1]*(1-f)+ALL[ii,k+1,1]*f
        else: la,lo=radar_pos(tc)
        vza,rng,y=gg.view(se,la,lo,H_FL); y=y-yc
        frac=(y-e.y_first)/(e.y_last-e.y_first); tc=t0s+frac*e.dur_s
    ok=(frac>=0)&(frac<=1)&(vza<85)
    return np.where(ok,tc,np.nan), la, lo, vza, rng, se


def build_XR():
    rows=[]; CR={}
    for i,e in EV.iterrows():
        for which in ['radar','routes']:
            tc,la,lo,vza,rng,se=solve_event(e,which)
            if which=='radar':
                if not (np.isfinite(tc[0]) and rdt[0]<=tc[0]<=0): continue
                w=np.array([1.0]); ok=np.isfinite(tc)
            else:
                ok=np.isfinite(tc)&(tc>=0); w=WT
                if w[ok].sum()<1e-6: continue
            cov=w[ok].sum(); alat,alon,shift=gg.apparent_position(se,la,lo,np.full_like(la,H_FL)); ww=w[ok]/w[ok].sum()
            q=lambda v,qs=(0.05,0.5,0.95): gg.weighted_quantile(v[ok][:,None],ww,list(qs))[:,0]
            tq=q(tc); laq=q(la); loq=q(lo); vq=q(vza); aq=q(alat,(0.005,0.5,0.995)); oq=q(alon,(0.005,0.5,0.995)); shq=q(shift)
            jd,fr=sg.jd_from_times(pd.DatetimeIndex([T0+pd.Timedelta(seconds=tq[1])])); sun=sg.sun_elevation(laq[1],loq[1],jd,fr)[0]
            rows.append(dict(sat=e.sat,scan=e.scan,track='radar track' if which=='radar' else 'posterior routes',t_first=e.t_first,dur_min=round(e.dur_s/60,2),timing_grade=e.timing_grade,timing_basis=e.timing_basis,
                covered_weight=cov,t_cross_p05=T0+pd.Timedelta(seconds=tq[0]),t_cross_med=T0+pd.Timedelta(seconds=tq[1]),t_cross_p95=T0+pd.Timedelta(seconds=tq[2]),
                lat_med=laq[1],lon_med=loq[1],lat_p05=laq[0],lat_p95=laq[2],lon_p05=loq[0],lon_p95=loq[2],vza_med=vq[1],vza_p05=vq[0],vza_p95=vq[2],
                app_lat_lo=aq[0],app_lat_hi=aq[2],app_lon_lo=oq[0],app_lon_hi=oq[2],parallax_km_med=shq[1],sun_elev_med=sun,pos_held_after_0011=bool(tq[1]>tv[-1])))
            if which=='routes': CR[(e.sat,e.scan,e.t_first)]=(tc,la,lo,vza,alat,alon,ok)
    return pd.DataFrame(rows),CR


def archive_status(r):
    if r.sat=='MTSAT-2': return 'held, Chiba Univ CEReS anonymous FTP (gridded 0.04 deg and native HRIT); fetched' 
    if r.sat=='FY-2D': return 'held, Chiba Univ CEReS anonymous FTP (re-encoded HRIT); fetched'
    if r.sat=='Meteosat-7':
        return 'listed in EUMETSAT Data Store catalogue (MVIRI L1.5 CDR R2, 57 deg); download needs free account' if r.t_first in m7_slots else 'NOT in EUMETSAT CDR catalogue (slot missing)'
    return 'not verified (archive requires registration)'


def hpd_levels(H,fracs):
    h=np.sort(H.ravel())[::-1]; c=np.cumsum(h)/h.sum()
    return [h[np.searchsorted(c,f)] for f in fracs]


def panel_box(row):
    if row.track=='radar track':
        la0,lo0=row.lat_med,row.lon_med; return [lo0-4,lo0+4,la0-3.5,la0+3.5]
    w,e_,s,n=row.app_lon_lo-1.5,row.app_lon_hi+1.5,row.app_lat_lo-1.5,row.app_lat_hi+1.5
    cx,cy=(w+e_)/2,(s+n)/2; hw=max((e_-w)/2,4); hh=max((n-s)/2,3.5)
    return [cx-hw,cx+hw,cy-hh,cy+hh]
