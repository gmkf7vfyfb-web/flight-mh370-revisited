"""Freeze recoverable MH371 inputs and construct a dated WMM-2010 grid.
No calibration uses the withheld (post-03:59:01) states or observations.
"""
from pathlib import Path
import json, shutil
import numpy as np
import pandas as pd
from pygeomag import GeoMag
import pygeomag
from scipy.interpolate import RegularGridInterpolator
from core import *

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'inputs';OUT.mkdir(exist_ok=True)
BUNDLE=Path('/Users/pete/Downloads/MH370_particle_filter_validation_bundle')

def main():
    inventory=[]
    for name in ['data/processed/mh371_truth.csv','data/processed/mh371_observations.csv',
                 'data/raw/i3f1_ecef_stk_sgp4_15_g7iCSAsigKXoYSIs9Gk8wSQEpXFD3K.xlsx',
                 'data/raw/inmarsat_figure11_pilot_error_1rN7Hz5Kybnn-dIYbdV5vF4KhrcRsseRE.xlsx']:
        src=BUNDLE/name;dst=OUT/src.name
        if not dst.exists():shutil.copyfile(src,dst)
        inventory.append({'path':dst.name,'source':str(src),'sha256':sha256(dst)})
    cof=Path(pygeomag.__file__).parent/'wmm/WMM_2010.COF'
    shutil.copyfile(cof,OUT/'WMM_2010.COF')
    gridpath=OUT/'wmm2010_grid.npz'
    if not gridpath.exists():
        model=GeoMag(coefficients_file=str(cof));la=np.arange(-65.,66.);lo=np.arange(35.,166.)
        values=np.array([[model.calculate(float(a),float(b),10.,2014+65/365).d for b in lo] for a in la])
        np.savez_compressed(gridpath,lat=la,lon=lo,declination=values)
        f=RegularGridInterpolator((la,lo),values)
        rng=np.random.default_rng(370);pts=np.column_stack((rng.uniform(-60,60,300),rng.uniform(40,160,300)))
        err=np.array([f([p])[0]-model.calculate(*p,10.,2014+65/365).d for p in pts])
        (OUT/'magnetic_grid_audit.json').write_text(json.dumps({'model':'WMM-2010','decimal_year':2014+65/365,'altitude_km':10,'grid_step_deg':1,'rms_error_deg':float(np.sqrt(np.mean(err**2))),'max_abs_error_deg':float(abs(err).max()),'note':'Fixed 10-km grid; altitude dependence not modeled. 300 held-out locations.'},indent=2))
    truth=pd.read_csv(OUT/'mh371_truth.csv')
    obs=pd.read_csv(OUT/'mh371_observations.csv')
    midnight=pd.Timestamp('2014-03-07T00:00:00Z').timestamp()
    times=truth.time_s.to_numpy()-midnight
    wind_angle=np.radians(truth.wind_direction_deg_true.to_numpy())
    wn=-truth.wind_speed_kt.to_numpy()*np.cos(wind_angle);we=-truth.wind_speed_kt.to_numpy()*np.sin(wind_angle)
    temp=truth.sat_c.to_numpy()+273.15
    np.savez_compressed(OUT/'oracle_weather.npz',time=times,north=wn,east=we,temperature=temp)
    orbital=OUT/'orbit.npz'
    if not orbital.exists():
        frame=pd.read_excel(OUT/'i3f1_ecef_stk_sgp4_15_g7iCSAsigKXoYSIs9Gk8wSQEpXFD3K.xlsx',header=None,usecols='B:H')
        a=frame.apply(pd.to_numeric,errors='coerce').dropna().to_numpy(float)
        assert a.shape[0]>=86401 and np.allclose(np.diff(a[:,0]),1)
        np.savez_compressed(orbital,time=a[:,0],position=a[:,1:4],velocity=a[:,4:7])
    with np.load(orbital) as z:ot=z['time'];op=z['position'];ov=z['velocity']
    frame=pd.read_excel(OUT/'inmarsat_figure11_pilot_error_1rN7Hz5Kybnn-dIYbdV5vF4KhrcRsseRE.xlsx',sheet_name='Figure11')
    fg=frame[['Hours UTC','Hz']].apply(pd.to_numeric,errors='coerce').dropna().sort_values('Hours UTC').to_numpy(float)
    def state(t):
        if t<ot[0] or t>ot[-1]:raise ValueError('Orbit outside support')
        return np.array([np.interp(t,ot,op[:,i]) for i in range(3)]),np.array([np.interp(t,ot,ov[:,i]) for i in range(3)])
    def afc(t,s,v):
        if not fg[0,0]<=t/3600<=fg[-1,0]:raise ValueError('Pilot error outside support')
        pilot=np.interp(t/3600,fg[:,0],fg[:,1])
        burum=ecef(53.284722,6.215333,0.)
        return float(pilot+F_UP/C*np.dot(v,unit(s-burum))-F_DOWN/C*np.dot(v,unit(PERTH-s)))
    def known(t):
        lat=np.interp(t,times,truth.latitude_deg);lon=np.interp(t,times,truth.longitude_deg);alt=np.interp(t,times,truth.altitude_ft)
        m=np.interp(t,times,truth.mach);h=np.interp(t,times,np.unwrap(np.radians(truth.heading_deg_true)))
        tas=m*np.sqrt(1.4*287.05287*np.interp(t,times,temp))/.5144444444
        return lat,lon,alt,m,np.degrees(h),tas*np.cos(h)+np.interp(t,times,wn),tas*np.sin(h)+np.interp(t,times,we)
    t0=3*3600+59*60+1
    valid=obs[(obs.is_r1200==True)&(obs.is_ior==True)&(obs.measurement_valid==True)&(obs.bto_us.between(13000,30000))].copy()
    valid['t']=valid.time_s-midnight
    pre=valid[(valid.t>=3*3600+29*60)&(valid.t<=t0)].drop_duplicates(['timestamp_utc','bto_us','bfo_hz'])
    calibration=[]
    for row in pre.itertuples():
        s,v=state(row.t);a=afc(row.t,s,v);lat,lon,alt,m,h,n,e=known(row.t)
        calibration.append({'time':row.t,'channel':row.channel_name,'bto_delay_us':float(row.bto_us-predict_bto(lat,lon,alt,s,0)),'bfo_bias_hz':float(row.bfo_hz-predict_bfo(lat,lon,alt,n,e,s,v,a))})
    delay=float(np.median([a['bto_delay_us'] for a in calibration]));bias=float(np.median([a['bfo_bias_hz'] for a in calibration]))
    pd.DataFrame(calibration).to_csv(OUT/'pre_holdout_calibration.csv',index=False)
    lat,lon,alt,m,h,n,e=known(t0)
    prior={'time':t0,'lat':lat,'lon':lon,'alt':alt,'mach':m,'heading':h,'bias':bias}
    # Freeze representative nearest message to each historical dense epoch.
    targets=[(4,4),(4,29),(4,55),(5,10),(5,29),(6,9),(6,48),(6,49)]
    selected=[];audit=[]
    for hr,mi in targets:
        target=hr*3600+mi*60
        pool=valid[(valid.t>t0)&(abs(valid.t-target)<60)]
        if pool.empty:raise ValueError(f'Missing dense epoch {hr}:{mi}')
        row=pool.iloc[np.argmin(abs(pool.t-target))];t=float(row.t);s,v=state(t);a=afc(t,s,v)
        selected.append({'time':t,'timestamp':row.timestamp_utc,'bto':float(row.bto_us),'bfo':float(row.bfo_hz),'bto_sd':29.,'delay_us':delay,'satellite':s.tolist(),'sat_velocity':v.tolist(),'afc':a,'channel':row.channel_name,'source_row':int(row.source_row)})
        lat,lon,alt,m,h,n,e=known(t)
        audit.append({'time':t,'channel':row.channel_name,'bto_residual_us':float(row.bto_us-predict_bto(lat,lon,alt,s,delay)),'bfo_residual_hz':float(row.bfo_hz-predict_bfo(lat,lon,alt,n,e,s,v,a)-bias),'truth_lat':lat,'truth_lon':lon})
    pd.DataFrame(audit).to_csv(OUT/'withheld_known_state_diagnostic.csv',index=False)
    (OUT/'mh371_dense.json').write_text(json.dumps({'classification':'reconstructed dense oracle implementation control; independent calibration differs from historical v12','prior':prior,'observations':selected,'weather':'oracle_weather.npz','magnetic':'wmm2010_grid.npz','calibration_cutoff_s':t0,'calibration_n':len(calibration),'bto_delay_us':delay,'bfo_bias_hz':bias},indent=2))
    inventory += [{'path':p.name,'sha256':sha256(p)} for p in OUT.iterdir() if p.suffix in ['.npz','.json','.csv','.COF'] and p.name!='input_manifest.json']
    (OUT/'input_manifest.json').write_text(json.dumps(inventory,indent=2))
    print(json.dumps({'delay_us':delay,'bias_hz':bias,'preholdout_n':len(calibration),'withheld':audit},indent=2),flush=True)

if __name__=='__main__':main()
