"""Build exact-contact input and explicit terminal pilot from attributed local inputs."""
import csv,datetime as dt,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent
P=Path('/jackbox/home/MH370')
source=P/'inputs/accident/final-satcom-bursts.json'
ephemeris=P/'inputs/accident/satellite-ephemeris.csv'
afc_table=P/'inputs/accident/satcom-observations.csv'
raw=json.loads(source.read_text())
ephem={r['epoch_id']:r for r in csv.DictReader(ephemeris.open())}
afc={r['epoch_id']:r['satellite_afc_hz'] for r in csv.DictReader(afc_table.open())}
origin=dt.datetime.fromisoformat('2014-03-07T18:01:49+00:00')
relative=lambda t:(dt.datetime.fromisoformat(t.replace('Z','+00:00'))-origin).total_seconds()
observations=[];epochs=[]
for i,burst in enumerate(raw['bursts']):
 e=ephem[burst['epoch_id']]
 observations.append(dict(id=burst['epoch_id'],time_utc=burst['recorded_time_utc'],satellite_afc_hz=float(afc[burst['epoch_id']]),measurement=dict(
  time=relative(burst['recorded_time_utc']),satellite_position_km={a:float(e[a+'_km']) for a in 'xyz'},
  satellite_velocity_km_s={a:float(e['v'+a+'_km_s']) for a in 'xyz'},ground_station_position_km=dict(x=-2368.8,y=4881.1,z=-3342.0),
  bto=burst['raw_bto_us']-raw['model_choices']['r600_bto_correction_us'] if i==0 else None,
  bto_sd=raw['model_choices']['r600_bto_sd_us'] if i==0 else None,bfo=burst['observed_bfo_hz'],bfo_sd=7.0)))
 epochs.append(relative(e['time_utc']))
contacts=dict(observations=observations,ephemeris_reference_times_s=epochs,provenance=dict(
 source=raw,files_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,ephemeris,afc_table]},
 time_origin_utc=origin.isoformat(),satellite_fractional_epoch='Runner uses bounded constant-velocity ECEF propagation from the whole-second source epoch.',
 bfo_sd='7 Hz inherited conditional likelihood; Holland startup offsets are handled in separately named cases, not changed measurements.',
 anomalous_r1200_bto='Excluded: raw 49,660 microseconds has no ordinary channel-bias correction that is asserted here. Legacy 18,380 row is not consumed.'))
(B/'terminal-final-contacts.json').write_text(json.dumps(contacts,indent=2)+'\n')
families=[]
for polar in ['openap_v2_6_0_attached_flow','openap_published2020_attached_flow']:
 short='openap26' if 'v2_6' in polar else 'openap2020'
 controls=[('initial-trim',dict(kind='fixed_initial_trim')),('best-glide',dict(kind='best_glide',maximum_lift_coefficient_rate_per_s=.05,maximum_roll_rate_deg_s=3.0,step_s=.5))]
 for n in [1,3,6]:
  controls.append((f'positive-lift-{n}-targets',dict(kind='rate_limited_targets',segments=n,lift_coefficient_bounds=[.05,1.2],bank_angle_bounds_deg=[-60,60],change_time_bounds_s=[10,900],maximum_lift_coefficient_rate_per_s=.05,maximum_roll_rate_deg_s=3.0,step_s=.5)))
 controls.append(('signed-lift-6-targets',dict(kind='rate_limited_targets',segments=6,lift_coefficient_bounds=[-.3,1.2],bank_angle_bounds_deg=[-60,60],change_time_bounds_s=[10,900],maximum_lift_coefficient_rate_per_s=.05,maximum_roll_rate_deg_s=3.0,step_s=.5)))
 for name,control in controls:families.append(dict(name=short+'-'+name,aerodynamics=polar,control=control))
config=dict(schema_version=1,name='Cruise-to-impact composition and timing pilot',seed=37091801,
 source_runs=[str(B/'runs/turns16-mach8-altitude8-vertical-bfo-seed-37091631')],draws_per_source=32,powered_step_s=1.0,
 final_contacts=str(B/'terminal-final-contacts.json'),kernel=dict(families=families,
 environment=dict(minimum_pressure_altitude_ft=500.,maximum_pressure_altitude_ft=43000.,below_minimum_policy='clamp_to_grid',above_maximum_policy='reject'),
 fallback_atmosphere=dict(nodes=[dict(altitude=0.,density=1.225,wind_north=0.,wind_east=0.),dict(altitude=43000.,density=.25,wind_north=0.,wind_east=0.)]),
 integration=dict(time_step=1.0,maximum_duration=3600.,sea_surface_altitude=0.,maximum_steps=12000),
 apu_start_policy=dict(mode='disabled'),apu_accessible_reserved_fuel_kg=0.0))
(B/'terminal-pilot.json').write_text(json.dumps(config,indent=2)+'\n')
print('Two exact contacts; R600 corrected BTO18,400; R1200 BTOexcluded;',len(families),'separate terminal families')
