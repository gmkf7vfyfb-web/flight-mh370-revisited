"""Independent arithmetic and coordinate checks for the retained spatial result."""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,re,urllib.request
import numpy as np
B=Path(__file__).resolve().parent;R=Path('/jackbox/home/MH370')
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--state',type=Path,default=B/'spatial-comparison-status.json');p.add_argument('--suffix',default='');p.add_argument('--record',type=Path,default=B/'spatial-independent-verification.json');args=p.parse_args()
state=json.loads(args.state.read_text());assert state['status']=='completed'
# Recalculate one nine-episode case independently, using a vectorized haversine
# and the supplied source scores, not the runner's query implementation.
entry=next(e for e in state['completed'] if e['terminal_family']=='openap26-positive-lift-3-targets' and e['contact_case']=='r600-no-startup-offset' and e['evidence_model']=='cmems-nine-episodes')
j=json.loads((Path(entry['output'])/'conditional-spatial-sensitivity.json').read_text());cells=json.loads((R/'inputs/evidence/ocean-drift-cmems-full-domain.json').read_text())['families'][0]['cells'];rows=j['particle_values'];p=np.radians([[x['latitude_deg'],x['longitude_deg']] for x in rows]);c=np.radians([[x['latitude_deg'],x['longitude_deg']] for x in cells]);dlat=p[:,0,None]-c[None,:,0];dlon=p[:,1,None]-c[None,:,1];a=np.sin(dlat/2)**2+np.cos(p[:,0,None])*np.cos(c[None,:,0])*np.sin(dlon/2)**2
# Canonical shared domain uses the documented nautical-mile sphere radius.
text=(R/'crates/domain/src/geodesy.rs').read_text();radius=float(re.search(r'LEGACY_SPHERE_RADIUS_NM: f64 = ([0-9_.]+)',text)[1].replace('_',''));dist=2*radius*np.arcsin(np.sqrt(np.clip(a,0,1)));nearest=np.argmin(dist,axis=1);supported=dist[np.arange(len(rows)),nearest]<=75
w=np.array([x['baseline_weight'] for x in rows]);ll=np.array([cells[i]['relative_log_likelihood'] for i in nearest]);z=np.sum(w[supported]*np.exp(ll[supported]));updated=np.where(supported,w*np.exp(ll)/z,0);saved=np.array([x['conditional_weight'] for x in rows]);assert np.max(np.abs(updated-saved))<1e-10
checked=0
for category in ['drift','pleiades']:
 summary=json.loads((B/(category+args.suffix+'-comparison')/'summary.json').read_text())
 for entry in summary['comparisons']:
  stem=entry['terminal_family']+'--'+entry['contact_case']+'--'+entry['evidence_model'];grid=np.load(B/(category+args.suffix+'-comparison')/(stem+'.npz'))['probability_given_computed_impact_and_surface_support'];assert abs(grid.sum()-1)<1e-12;checked+=1
browser_errors={}
for category in ['drift','stokes','pleiades']:
 path=R/('mh370-'+category+'-comparison.html');doc=path.read_text();packed=re.search(r'const packed="([^"]+)"',doc)[1];data=json.loads(gzip.decompress(base64.b64decode(packed)));err=max(abs(sum(x[2] for x in v['cells'])-1) for v in data);assert err<1e-6;browser_errors[category]=err
 web=Path('/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/overnight-analysis/web')/path.name;web.write_bytes(path.read_bytes());assert urllib.request.urlopen('http://127.0.0.1:8771/overnight/'+path.name).read()==path.read_bytes();Path('/tmp/spatial-'+category+'-ui.js').write_text(doc.split('<script>')[1].split('</script>')[0])
result=dict(checked_normalized_grids=checked,independent_max_weight_error=float(np.max(np.abs(updated-saved))),browser_mass_rounding_error=browser_errors,served_byte_matches=True)
args.record.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
