"""Reconstructed v12 dynamics/SMC; not the recovered historical executable.

Units: degrees clockwise from north, knots, feet, seconds, kelvin; ECEF km.
Source: Davey et al. 2015 chapters 5--8 and archived August 24 v12 discussion.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib, json, os
import numpy as np
from scipy.special import logsumexp
from scipy.interpolate import RegularGridInterpolator
from pyproj import Geod

GEOD = Geod(ellps='WGS84')
C = 299792.458
PERTH = np.array([-2368.8, 4881.1, -3342.0])
F_UP = 1646652500.
F_DOWN = 3615152500.
MODES = ('CMH', 'CTH', 'CMT', 'CTT', 'LNAV')

def wrap(x): return (x + 180.) % 360. - 180.

def ou_parameters(beta, q, dt):
    return np.exp(-beta*np.asarray(dt)), np.sqrt(q * -np.expm1(-2*beta*np.asarray(dt))/(2*beta))

def ou_step(x, beta, q, dt, rng):
    phi, sigma = ou_parameters(beta, q, dt)
    return phi*x + sigma*rng.normal(size=np.shape(x))

def ecef(lat, lon, altitude_ft):
    lat,lon,h=np.broadcast_arrays(np.radians(lat),np.radians(lon),np.asarray(altitude_ft)*.0003048)
    e2=6.6943799901413165e-3; rn=6378.137/np.sqrt(1-e2*np.sin(lat)**2)
    return np.stack(((rn+h)*np.cos(lat)*np.cos(lon),(rn+h)*np.cos(lat)*np.sin(lon),(rn*(1-e2)+h)*np.sin(lat)),axis=-1)

def velocity_ecef(lat,lon,north_kt,east_kt,up_fpm=0.):
    lat,lon,n,e,u=np.broadcast_arrays(np.radians(lat),np.radians(lon),np.asarray(north_kt)*1.852/3600,np.asarray(east_kt)*1.852/3600,np.asarray(up_fpm)*.0003048/60)
    return np.stack((-n*np.sin(lat)*np.cos(lon)-e*np.sin(lon)+u*np.cos(lat)*np.cos(lon),-n*np.sin(lat)*np.sin(lon)+e*np.cos(lon)+u*np.cos(lat)*np.sin(lon),n*np.cos(lat)+u*np.sin(lat)),axis=-1)

def unit(v): return v/np.linalg.norm(v,axis=-1,keepdims=True)

def predict_bto(lat,lon,alt,satellite,delay_us):
    return delay_us + 2e6*(np.linalg.norm(satellite-ecef(lat,lon,alt),axis=-1)+np.linalg.norm(satellite-PERTH))/C

def predict_bfo(lat,lon,alt,north,east,satellite,sat_velocity,afc_hz):
    """Bias-free BFO. Vertical rate intentionally omitted as in Davey p.47.

    AES compensation assumes nominal GEO slot, sea-level position and zero climb.
    """
    pos=ecef(lat,lon,alt);v=velocity_ecef(lat,lon,north,east)
    up=F_UP/C*np.sum((v-sat_velocity)*unit(satellite-pos),axis=-1)
    down=F_DOWN/C*np.dot(sat_velocity,unit(PERTH-satellite))
    nominal=np.array([42164*np.cos(np.radians(64.5)),42164*np.sin(np.radians(64.5)),0.])
    comp=-F_UP/C*np.sum(v*unit(nominal-ecef(lat,lon,0.)),axis=-1)
    return up+down+comp+afc_hz

def bias_update(mean,var,residual,sigma=7.):
    innovation=residual-mean;total=var+sigma*sigma
    ll=-.5*(innovation*innovation/total+np.log(2*np.pi*total))
    gain=var/total
    return mean+gain*innovation, var*(1-gain), ll

class ConstantWeather:
    classification='synthetic/diagnostic constant weather, not ACCESS-G'
    def __init__(self,north=0.,east=0.,temperature=220.):self.values=(north,east,temperature)
    def __call__(self,t,lat,lon,alt):return tuple(np.full(np.shape(lat),v) for v in self.values)

class OracleWeather:
    classification='known-flight ACARS oracle weather; not blind validation'
    def __init__(self,time,north,east,temperature):self.t=np.asarray(time);self.data=(north,east,temperature)
    def __call__(self,t,lat,lon,alt):
        if np.any(t<self.t[0]) or np.any(t>self.t[-1]):raise ValueError('Outside oracle weather support')
        return tuple(np.broadcast_to(np.interp(t,self.t,v),np.shape(lat)) for v in self.data)

class GriddedWeather:
    """Explicit supplied grid, axes time_s/altitude_ft/latitude_deg/longitude_deg.
    Fields north_kt, east_kt, temperature_k. Never extrapolates or assumes calm.
    """
    classification='supplied independent weather grid; provenance in config'
    def __init__(self,path):
        with np.load(path,allow_pickle=False) as z:
            axes=tuple(z[k] for k in ['time_s','altitude_ft','latitude_deg','longitude_deg'])
            self.f=[RegularGridInterpolator(axes,z[k],bounds_error=True) for k in ['north_kt','east_kt','temperature_k']]
    def __call__(self,t,lat,lon,alt):
        coords=np.stack(np.broadcast_arrays(t,alt,lat,lon),axis=-1)
        return tuple(f(coords) for f in self.f)

class MagneticGrid:
    def __init__(self,path):
        with np.load(path,allow_pickle=False) as z:
            self.f=RegularGridInterpolator((z['lat'],z['lon']),z['declination'],bounds_error=True)
    def __call__(self,lat,lon):return self.f(np.stack((lat,lon),axis=-1))

def ground_velocity(tas,angle,mode,decl,north_wind,east_wind):
    true=np.radians(angle+np.where((mode==0)|(mode==2),decl,0.))
    n=tas*np.cos(true)+north_wind;e=tas*np.sin(true)+east_wind
    track_modes=mode>=2
    cross=east_wind*np.cos(true)-north_wind*np.sin(true)
    parallel=east_wind*np.sin(true)+north_wind*np.cos(true)
    valid=tas*tas>=cross*cross
    if not np.all(valid):raise ValueError('Wind exceeds track-hold capability')
    gs=parallel+np.sqrt(tas*tas-cross*cross)
    return np.where(track_modes,gs*np.cos(true),n),np.where(track_modes,gs*np.sin(true),e)

@dataclass
class Config:
    particles:int=100000
    seed:int=101
    dt_s:float=10.
    maneuver_dt_s:float=1.
    ess_fraction:float=.5
    use_bfo:bool=True
    bfo_sigma_hz:float=7.
    bias_prior_sd_hz:float=25.
    position_sd_deg:float=.4/60
    angle_sd_deg:float=1.
    mach_sd:float=.03

class Filter:
    def __init__(self,config,weather,magnetic):
        self.config=config;self.weather=weather;self.magnetic=magnetic
        self.rng=np.random.default_rng(config.seed);self.s={};self.history=[];self.index=0

    def initialize(self,prior):
        n=self.config.particles;r=self.rng;cfg=self.config
        s={};s['lat']=r.normal(prior['lat'],cfg.position_sd_deg,n);s['lon']=r.normal(prior['lon'],cfg.position_sd_deg,n)
        s['alt']=np.full(n,prior['alt']) if 'alt' in prior else r.integers(25,44,n)*1000.
        s['mach']=r.uniform(*prior['mach_uniform'],n) if 'mach_uniform' in prior else r.normal(prior['mach'],cfg.mach_sd,n)
        s['mach_error']=r.normal(0,np.sqrt(2.05e-7/(2*.01058)),n)
        s['angle_error']=r.normal(0,np.degrees(np.sqrt(4.074e-8/(2*.009792))),n)
        s['wind_n']=r.normal(0,np.sqrt(.07021/(2*.001087)),n);s['wind_e']=r.normal(0,np.sqrt(.07021/(2*.001087)),n)
        s['mode']=r.integers(0,5,n);s['tau']=np.exp(r.uniform(np.log(360),np.log(36000),n))
        self.time=float(prior['time']);s['time']=np.full(n,self.time)
        wn,we,temp=self.weather(self.time,s['lat'],s['lon'],s['alt'])
        tas=s['mach']*np.sqrt(1.4*287.05287*temp)/.5144444444
        if 'track' in prior:
            track=r.normal(prior['track'],cfg.angle_sd_deg,n)
            cross=we*np.cos(np.radians(track))-wn*np.sin(np.radians(track))
            heading=track-np.degrees(np.arcsin(cross/tas))
        else:
            heading=r.normal(prior['heading'],cfg.angle_sd_deg,n)
            gn=tas*np.cos(np.radians(heading))+wn;ge=tas*np.sin(np.radians(heading))+we
            track=np.degrees(np.arctan2(ge,gn))
        angle=np.where(s['mode']>=2,track,heading)
        decl=self.magnetic(s['lat'],s['lon'])
        s['angle']=wrap(angle-np.where((s['mode']==0)|(s['mode']==2),decl,0.))
        for event in ['turn','speed','height']:
            s['next_'+event]=self.time+r.exponential(s['tau'])
        s['turn_remaining']=np.zeros(n);s['speed_target']=s['mach'].copy();s['height_target']=s['alt'].copy()
        s['lnav_switch']=np.where(s['mode']==4,self.time+r.exponential(21600/np.log(2),n),np.inf)
        s['bias_mean']=np.full(n,prior['bias']);s['bias_var']=np.full(n,cfg.bias_prior_sd_hz**2)
        s['root']=np.arange(n);s['logw']=np.full(n,-np.log(n))
        for event in ['turn','speed','height']:s['count_'+event]=np.zeros(n,dtype=int)
        self.s=s

    def velocity(self,ids=None):
        s=self.s
        if ids is None:ids=np.arange(len(s['lat']))
        lat,lon,alt,t=[s[k][ids] for k in ['lat','lon','alt','time']]
        wn,we,temp=self.weather(t,lat,lon,alt)
        tas=(s['mach'][ids]+s['mach_error'][ids])*np.sqrt(1.4*287.05287*temp)/.5144444444
        n,e=ground_velocity(tas,s['angle'][ids]+s['angle_error'][ids],s['mode'][ids],self.magnetic(lat,lon),wn+s['wind_n'][ids],we+s['wind_e'][ids])
        return n,e,tas,wn+s['wind_n'][ids],we+s['wind_e'][ids]

    def propagate(self,target):
        """Per-particle exact event boundaries, <=10 s cruise and <=1 s manoeuvre.
        Waiting times restart AFTER completion, not at manoeuvre onset.
        """
        s=self.s;r=self.rng;cfg=self.config
        while True:
            ids=np.flatnonzero(s['time']<target-1e-7)
            if len(ids)==0:break
            t=s['time'][ids]
            for event in ['turn','speed','height']:
                hit=ids[s['next_'+event][ids]<=t+1e-7]
                if len(hit):
                    s['count_'+event][hit]+=1;s['next_'+event][hit]=np.inf
                    if event=='turn':s['turn_remaining'][hit]=r.uniform(-180,180,len(hit))
                    elif event=='speed':s['speed_target'][hit]=r.uniform(.73,.84,len(hit))
                    else:s['height_target'][hit]=r.integers(25,44,len(hit))*1000.
            switched=ids[s['lnav_switch'][ids]<=t+1e-7]
            if len(switched):
                gn,ge,_,wn,we=self.velocity(switched)
                true_heading=np.degrees(np.arctan2(ge-we,gn-wn))
                mode=r.integers(0,2,len(switched));s['mode'][switched]=mode
                s['angle'][switched]=wrap(true_heading-np.where(mode==0,self.magnetic(s['lat'][switched],s['lon'][switched]),0)-s['angle_error'][switched])
                s['lnav_switch'][switched]=np.inf
            gn,ge,tas,_,_=self.velocity(ids)
            rate=np.degrees(9.80665*np.tan(np.radians(15))/(tas*.5144444444))
            turn=s['turn_remaining'][ids];speed=s['speed_target'][ids]-s['mach'][ids];height=s['height_target'][ids]-s['alt'][ids]
            active=(abs(turn)>1e-9)|(abs(speed)>1e-12)|(abs(height)>1e-7)
            dt=np.minimum(target-t,np.where(active,cfg.maneuver_dt_s,cfg.dt_s))
            for event in ['turn','speed','height']:dt=np.minimum(dt,s['next_'+event][ids]-t)
            dt=np.minimum(dt,s['lnav_switch'][ids]-t)
            for rem,velocity in [(abs(turn),rate),(abs(speed),.1/60),(abs(height),4000/60)]:
                dt=np.minimum(dt,np.where(rem>1e-9,rem/velocity,np.inf))
            # Zero-duration manoeuvres (same altitude) complete without advancing time.
            for event,rem in [('turn',turn),('speed',speed),('height',height)]:
                finished=ids[(abs(rem)<1e-9)&np.isinf(s['next_'+event][ids])]
                if len(finished):s['next_'+event][finished]=s['time'][finished]+r.exponential(s['tau'][finished])
            if np.any(dt<=0):raise RuntimeError('Non-positive integration step')
            da=np.sign(turn)*np.minimum(abs(turn),rate*dt)
            dm=np.sign(speed)*np.minimum(abs(speed),(.1/60)*dt)
            dh=np.sign(height)*np.minimum(abs(height),(4000/60)*dt)
            # Midpoint deterministic controls for transport, OU errors sampled at end.
            s['angle'][ids]+=da/2;s['mach'][ids]+=dm/2;s['alt'][ids]+=dh/2
            gn,ge,_,_,_=self.velocity(ids)
            track=np.degrees(np.arctan2(ge,gn));distance=np.hypot(gn,ge)*1852/3600*dt
            lon,lat,back=GEOD.fwd(s['lon'][ids],s['lat'][ids],track,distance)
            lnav=s['mode'][ids]==4
            s['angle'][ids]+=np.where(lnav,wrap(back+180-track),0.)
            s['lon'][ids]=lon;s['lat'][ids]=lat
            s['angle'][ids]=wrap(s['angle'][ids]+da/2);s['mach'][ids]+=dm/2;s['alt'][ids]+=dh/2
            s['turn_remaining'][ids]-=da
            for key,beta,q,factor in [('mach_error',.01058,2.05e-7,1.),('angle_error',.009792,4.074e-8,180/np.pi),('wind_n',.001087,.07021,1.),('wind_e',.001087,.07021,1.)]:
                s[key][ids]=ou_step(s[key][ids]/factor,beta,q,dt,r)*factor
            s['time'][ids]+=dt
            for event,rem in [('turn',s['turn_remaining'][ids]),('speed',s['speed_target'][ids]-s['mach'][ids]),('height',s['height_target'][ids]-s['alt'][ids])]:
                finished=ids[(abs(rem)<1e-8)&np.isinf(s['next_'+event][ids])]
                if len(finished):s['next_'+event][finished]=s['time'][finished]+r.exponential(s['tau'][finished])
        self.time=float(target)

    def observe(self,obs):
        self.propagate(obs['time']);s=self.s
        gn,ge,*_=self.velocity();ll=np.zeros(len(gn))
        sat=np.asarray(obs['satellite']);sv=np.asarray(obs['sat_velocity'])
        if obs.get('bto') is not None:
            residual=obs['bto']-predict_bto(s['lat'],s['lon'],s['alt'],sat,obs['delay_us'])
            sd=obs['bto_sd'];ll+=-.5*(residual/sd)**2-np.log(sd*np.sqrt(2*np.pi))
        if self.config.use_bfo and obs.get('bfo') is not None:
            residual=obs['bfo']-predict_bfo(s['lat'],s['lon'],s['alt'],gn,ge,sat,sv,obs['afc'])
            s['bias_mean'],s['bias_var'],lb=bias_update(s['bias_mean'],s['bias_var'],residual,self.config.bfo_sigma_hz);ll+=lb
        logz=logsumexp(s['logw']+ll)
        if not np.isfinite(logz):raise RuntimeError('All particle likelihoods vanished')
        s['logw']=s['logw']+ll-logz;w=np.exp(s['logw']);ess=1/np.sum(w*w)
        row={'index':self.index,'time':self.time,'ess':float(ess),'root_count':int(len(np.unique(s['root']))),'tau_unique':int(len(np.unique(s['tau']))),'log_predictive':float(logz),'latitude_mean':float(np.sum(w*s['lat']))}
        self.history.append(row);self.index+=1
        return row

    def resample(self):
        s=self.s;n=len(s['lat']);w=np.exp(s['logw'])
        if 1/np.sum(w*w)>=self.config.ess_fraction*n:return False
        c=np.cumsum(w);c[-1]=1.
        ids=np.searchsorted(c,(self.rng.random()+np.arange(n))/n)
        self.s={k:v[ids].copy() for k,v in s.items()};self.s['logw'].fill(-np.log(n));return True

    def checkpoint(self,path,identity):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        meta={'config':asdict(self.config),'rng':self.rng.bit_generator.state,'time':self.time,'index':self.index,'history':self.history,'identity':identity}
        temp=path.with_suffix('.tmp')
        with temp.open('wb') as f:
            np.savez_compressed(f,**self.s,metadata=np.asarray(json.dumps(meta)));f.flush();os.fsync(f.fileno())
        os.replace(temp,path)

    @classmethod
    def resume(cls,path,weather,magnetic,identity):
        with np.load(path,allow_pickle=False) as z:
            meta=json.loads(str(z['metadata']))
            if meta['identity']!=identity:raise ValueError('Checkpoint input/code identity mismatch')
            obj=cls(Config(**meta['config']),weather,magnetic)
            obj.s={k:z[k].copy() for k in z.files if k!='metadata'}
        obj.time=meta['time'];obj.index=meta['index'];obj.history=meta['history'];obj.rng.bit_generator.state=meta['rng']
        return obj

def sha256(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
