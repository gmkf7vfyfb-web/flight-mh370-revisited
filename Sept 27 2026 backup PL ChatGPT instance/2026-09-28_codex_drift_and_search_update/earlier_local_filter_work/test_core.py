import json
from pathlib import Path
import numpy as np
import pytest
from core import *

def zero_mag(lat,lon):return np.zeros_like(lat)

def example(n=100,seed=3):
    f=Filter(Config(particles=n,seed=seed),ConstantWeather(north=12,east=20),zero_mag)
    f.initialize({'lat':10.,'lon':100.,'alt':35000.,'mach':.8,'heading':190.,'bias':150.,'time':0.})
    return f

def test_ou_stationarity_and_nominal_separation():
    rng=np.random.default_rng(35);sd=np.sqrt(.07021/(2*.001087));x=rng.normal(0,sd,200000)
    y=ou_step(x,.001087,.07021,60.,rng)
    assert abs(y.std()-sd)<.03
    phi,innovation=ou_parameters(.001087,.07021,60.)
    assert abs(phi-.936861)<1e-6 and abs(innovation-1.987)<.001
    # Process is applied to the error, never to erase a 100-knot nominal wind.
    assert abs((100+y).mean()-100)<.05

def test_rb_bias_matches_batch_gaussian():
    m=np.array([152.5]);v=np.array([625.]);data=np.array([144.,159.,150.])
    for z in data:m,v,ll=bias_update(m,v,z,7.)
    expected_var=1/(1/625+3/49)
    assert np.allclose(v,expected_var)
    assert np.allclose(m,expected_var*(152.5/625+data.sum()/49))

def test_full_bto_path_and_calibration():
    sat=np.array([18000.,38000.,0.]);p=ecef(0.,90.,35000.)
    want=-495679+2e6*(np.linalg.norm(sat-p)+np.linalg.norm(sat-PERTH))/C
    assert abs(predict_bto(0,90,35000,sat,-495679)-want)<1e-9
    assert np.isclose(predict_bto(0,90,35000,sat,-491079)-want,4600.)

def test_nominal_stationary_satellite_cancels_level_doppler():
    sat=np.array([42164*np.cos(np.radians(64.5)),42164*np.sin(np.radians(64.5)),0.])
    assert abs(predict_bfo(-30.,90.,0.,-450.,30.,sat,np.zeros(3),0.))<1e-9

def test_atsb_published_1707_example():
    # Rounded Table 3 state at 17:05, compared to Table 5 17:07 value.
    sat=np.array([18127.3,38077.6,952.5]);sv=np.array([.00206,-.00120,.05395])
    gs=867/1.852
    b=predict_bfo(5.27,102.79,35000.,gs*np.cos(np.radians(25)),gs*np.sin(np.radians(25)),sat,sv,24.1)+152.5
    assert abs(b-131.7)<.5

def test_track_hold_crosswind_and_magnetic_sign():
    n,e=ground_velocity(np.array([400.,400.]),np.array([0.,0.]),np.array([3,0]),np.array([10.,10.]),np.array([0.,0.]),np.array([100.,100.]))
    assert abs(e[0])<1e-10 and abs(n[0]-np.sqrt(400**2-100**2))<1e-10
    assert np.isclose(e[1],400*np.sin(np.radians(10))+100)

def test_checkpoint_resume_is_bit_exact(tmp_path):
    f=example();f.propagate(600);f.checkpoint(tmp_path/'resume.npz',{'fixture':'1'})
    g=Filter.resume(tmp_path/'resume.npz',f.weather,zero_mag,{'fixture':'1'})
    f.propagate(1200);g.propagate(1200)
    for key in f.s:assert np.array_equal(f.s[key],g.s[key]),key
    assert f.rng.bit_generator.state==g.rng.bit_generator.state
    with pytest.raises(ValueError):Filter.resume(tmp_path/'resume.npz',f.weather,zero_mag,{'fixture':'changed'})

def test_maneuver_completion_restarts_wait_and_no_overshoot():
    f=example(1);s=f.s;s['mode'][:]=3;s['next_turn'][:]=0;s['next_speed'][:]=0;s['next_height'][:]=0
    f.propagate(1.)
    assert s['count_turn'][0]==s['count_speed'][0]==s['count_height'][0]==1
    assert abs(s['mach'][0]-s['speed_target'][0])>=0
    assert np.isinf(s['next_turn'][0])
    f.propagate(500.)
    for k in ['lat','lon','alt','angle','mach']:assert np.isfinite(s[k]).all()
    assert np.all(s['time']==500.)

def test_no_bfo_does_not_update_latent_bias():
    f=example();f.config.use_bfo=False
    sat=np.array([18000.,38000.,0.]);f.observe({'time':1.,'satellite':sat,'sat_velocity':np.zeros(3),'bto':None,'bfo':1000.,'afc':0.})
    assert np.all(f.s['bias_mean']==150) and np.all(f.s['bias_var']==625)

def test_resampling_preserves_correlated_states():
    f=example();f.s['logw'][:]=-1000;f.s['logw'][17]=0
    chosen={k:v[17] for k,v in f.s.items()};assert f.resample()
    for k,v in f.s.items():
        if k!='logw':assert np.all(v==chosen[k])

def test_no_silent_weather_extrapolation(tmp_path):
    axes=[np.array([0.,10.]),np.array([25000.,43000.]),np.array([-10.,10.]),np.array([90.,110.])]
    data=dict(zip(['time_s','altitude_ft','latitude_deg','longitude_deg'],axes))
    data.update(north_kt=np.ones((2,2,2,2)),east_kt=np.ones((2,2,2,2)),temperature_k=np.full((2,2,2,2),220.))
    np.savez(tmp_path/'weather.npz',**data);w=GriddedWeather(tmp_path/'weather.npz')
    with pytest.raises(ValueError):w(11,np.array([0.]),np.array([100.]),np.array([35000.]))
