"""Independent scalar force-balance checks on saved diagnostic rows."""
import csv, json, math, hashlib
from pathlib import Path
b=Path(__file__).parent
p=b/'cruise-contact-performance'
summary=json.loads((p/'summary.json').read_text())
rows=list(csv.DictReader((p/'contact-performance.csv').open()))
errors={key:0.0 for key in ['total_tas','gamma','lift','CL','drag','thrust','ratio']}
for row in rows:
    f=lambda key:float(row[key])
    horizontal=f('horizontal_tas_m_s'); vertical=f('vertical_speed_ft_min')*127/25000
    speed=math.sqrt(horizontal*horizontal+vertical*vertical)
    cosine=horizontal/speed; sine=vertical/speed
    qS=f('density_kg_m3')*speed*speed*427.8/2
    # Resolve gravity perpendicular and parallel to the velocity vector.
    lift=f('mass_kg')*9.80665*cosine/math.cos(math.radians(f('bank_deg')))
    cl=lift/qS
    cd0,k=(.024,.047) if row['family']=='OpenapV2_6_0AttachedFlow' else (.034,.051)
    drag=qS*cd0+k*lift*lift/qS
    thrust=drag+f('mass_kg')*9.80665*sine
    calculations={'total_tas':(speed,f('total_tas_m_s')),
      'gamma':(math.degrees(math.asin(sine)),f('gamma_deg')),
      'lift':(lift,f('required_lift_n')),'CL':(cl,f('lift_coefficient')),
      'drag':(drag,f('drag_n')),'thrust':(thrust,f('required_thrust_n')),
      'ratio':(thrust/f('nominal_thrust_n'),f('thrust_ratio'))}
    for key,(expected,actual) in calculations.items():
        error=abs(expected-actual)/max(1,abs(expected))
        errors[key]=max(errors[key],error)
        assert error < 2e-12,(key,row,error)
    assert 174384 <= f('mass_kg') <= 209000
assert len(rows)==summary['records']
result={'rows':len(rows),'maximum_relative_errors':errors,'source_csv_sha256':hashlib.sha256((p/'contact-performance.csv').read_bytes()).hexdigest(),
 'scope':'Independent scalar unit conversion, force decomposition and separate polar checks; not validation of the thrust proxy or aircraft performance envelope.'}
(b/'cruise-contact-performance-independent-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
