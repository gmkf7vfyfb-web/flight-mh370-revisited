"""Independently score saved spatial weights and their actual 00:11 parents."""
from pathlib import Path
import csv,datetime as dt,hashlib,json,math,time
import numpy as np
B=Path(__file__).resolve().parent;start=time.monotonic();O=B/'flight-drift-comparison'
s=json.loads((O/'summary.json').read_text());arrays=[]
for source in s['cruise_sources']:
 with (Path(source['source'])/'posterior.csv').open() as f:
  arrays.append(np.array([(float(r['latitude_deg']),float(r['longitude_deg']),int(r['root'])) for r in csv.DictReader(f)]))
checked=[]
for c in s['comparisons']:
 path=Path(c['spatial_source']);assert hashlib.sha256(path.read_bytes()).hexdigest()==c['spatial_source_sha256'];source=json.loads(path.read_text());rows=source['particle_values']
 before=np.array([r['baseline_weight'] for r in rows]);after=np.array([r['conditional_weight'] for r in rows])
 score=np.array([r['relative_log_likelihood'] if r['relative_log_likelihood'] is not None else -math.inf for r in rows])
 terms=[w*math.exp(v) for w,v in zip(before,score)];z=math.fsum(terms)
 assert np.max(np.abs(np.array(terms)/z-after))<1e-12
 assert abs(math.log(z)-source['relative_score_log_normalizer'])<1e-11
 identities=[(r['identity']['source_index'],r['identity']['root_id']) for r in rows]
 points={ 'impact':np.array([(r['latitude_deg'],r['longitude_deg']) for r in rows]),
          '0011':np.array([arrays[r['identity']['source_index']][r['identity']['parent_slot'],:2] for r in rows]) }
 for phase,xy in points.items():
  for label,w in [('before',before),('after',after)]:
   m=c['phases'][phase][label];root={}
   for identity,weight in zip(identities,w):root[identity]=root.get(identity,0)+weight
   assert abs(1/math.fsum(v*v for v in root.values())-m['effective_ancestor_count'])<1e-8
   assert abs(max(root.values())-m['largest_ancestor_share'])<1e-12
   assert abs(math.fsum(w[xy[:,0]>-35])-m['north_of_35S'])<1e-12
   assert abs(math.fsum(w[xy[:,0]>-30])-m['north_of_30S'])<1e-12
   for center,probability in zip(m['latitude_bin_centers_deg'],m['latitude_bin_probabilities']):
    assert abs(math.fsum(w[(xy[:,0]>=center-1.25)&(xy[:,0]<center+1.25)])-probability)<1e-12
   # Direct sorted scalar sums at the recorded browser CDF abscissae.
   order=np.argsort(xy[:,0]);cumulative=np.r_[0,np.cumsum(w[order])];grid=np.array(m['cdf']);i=np.searchsorted(xy[order,0],grid[:,0],'right')
   assert np.max(np.abs(cumulative[i]-grid[:,1]))<1e-12
   grid=m['grid'];assert abs(math.fsum(cell[2] for cell in grid['cells'])-1)<1e-10
   ranked=sorted((cell[2] for cell in grid['cells']),reverse=True);cum=np.cumsum(ranked)
   for probability in [.5,.8,.9,.95]:
    count=int(np.searchsorted(cum,probability))+1
    assert count*100==m['cell_ranked_probability_areas']['10'][str(probability)]['area_km2']
 checked.append(dict(family=c['terminal_family'],contacts=c['contact_case'],evidence=c['evidence_model'],run=c['numerical_run'],rows=len(rows)))
result=dict(checked_utc=dt.datetime.now(dt.timezone.utc).isoformat(),status='passed',composed_cases=len(checked),phase_distributions=4*len(checked),
 report_sha256=hashlib.sha256((O/'summary.json').read_bytes()).hexdigest(),verification_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 checks='Raw source identity; normalized drift factor and log normalizer; actual cruise parent coordinates; independent root sums, region/bin probabilities, cumulative curves and10km ranked cell areas.',
 cases=checked,elapsed_seconds=time.monotonic()-start,scope='Verifies composition and reporting arithmetic; not physical likelihood calibration or statistical convergence.')
(B/'flight-drift-numerical-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'}))
