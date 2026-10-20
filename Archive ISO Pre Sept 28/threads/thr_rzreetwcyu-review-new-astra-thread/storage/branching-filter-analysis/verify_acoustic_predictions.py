"""Independent spherical vector geometry and energy checks for retained output."""
from pathlib import Path
import argparse,hashlib, json, math, re
import numpy as np
B=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=B/'impact-acoustic-predictions');p.add_argument('--record',type=Path,default=B/'acoustic-independent-verification.json');args=p.parse_args()
S=args.source
cfg=json.loads((S/'resolved-config.json').read_text())
summary=json.loads((S/'summary.json').read_text())
assert hashlib.sha256((S/'predictions.jsonl').read_bytes()).hexdigest()==summary['predictions_sha256']
# Same declared radius, independent cross/dot central angle rather than haversine.
radius=3440.065*1.852
def unit(lat,lon):
 a,b=np.radians([lat,lon]);return np.array([math.cos(a)*math.cos(b),math.cos(a)*math.sin(b),math.sin(a)])
receivers={s['name']:s['position'] for s in cfg['stations']}
maximum_range_error=maximum_time_error=maximum_bearing_error=0.
counts={};checked=0
for line in (S/'predictions.jsonl').open():
 p=json.loads(line);u=unit(p['latitude_deg'],p['longitude_deg']);assert p['body_attitude'] is None
 assert not p['likelihood_evaluated'] and p['log_weight_increment']==0
 assert 0<=p['vertical_kinetic_energy_j']<=p['ground_frame_kinetic_energy_j']*(1+1e-12)
 compatible=False
 for s in p['stations']:
  r=receivers[s['station']];v=unit(r['latitude'],r['longitude'])
  angle=math.atan2(np.linalg.norm(np.cross(v,u)),np.dot(v,u));distance=radius*angle
  maximum_range_error=max(maximum_range_error,abs(distance-s['prediction']['distance_km']))
  a,b=np.radians([r['latitude'],r['longitude']]);east=np.array([-math.sin(b),math.cos(b),0]);north=np.array([-math.sin(a)*math.cos(b),-math.sin(a)*math.sin(b),math.cos(a)])
  bearing=math.degrees(math.atan2(np.dot(u,east),np.dot(u,north)))%360
  maximum_bearing_error=max(maximum_bearing_error,abs((bearing-s['source_bearing_true_deg']+180)%360-180))
  lo=p['impact_time_unix_s']+distance/cfg['celerity_km_s']['maximum'];hi=p['impact_time_unix_s']+distance/cfg['celerity_km_s']['minimum']
  maximum_time_error=max(maximum_time_error,abs(lo-s['prediction']['arrival_time_s']['minimum']),abs(hi-s['prediction']['arrival_time_s']['maximum']))
  event=cfg['conditional_event']
  if s['station']==event['station']:
   compatible=abs((bearing-event['bearing_true_deg']+180)%360-180)<=event['bearing_tolerance_deg'] and lo<=event['arrival_time_unix_s']<=hi
 assert compatible==p['event_geometrically_compatible']
 if compatible:counts[p['family']]=counts.get(p['family'],0)+1
 for v in p['coupling_reference_scenarios']:
  assert v['from_total_ground_frame_energy_j']==p['ground_frame_kinetic_energy_j']*v['efficiency']
  assert v['from_vertical_energy_j']==p['vertical_kinetic_energy_j']*v['efficiency']
 checked+=1
assert counts==summary['event_geometry_compatible_counts'] and checked==summary['impacts']
assert maximum_range_error<1e-8 and maximum_time_error<1e-6 and maximum_bearing_error<1e-9
result=dict(checked_impacts=checked,checked_station_predictions=checked*len(receivers),maximum_range_error_km=maximum_range_error,
 maximum_arrival_time_error_s=maximum_time_error,maximum_bearing_error_deg=maximum_bearing_error,compatible_counts=counts,
 energy_reference_arithmetic_exact=True,body_attitude_uncomputed=True,acoustic_likelihood_absent=True)
args.record.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
