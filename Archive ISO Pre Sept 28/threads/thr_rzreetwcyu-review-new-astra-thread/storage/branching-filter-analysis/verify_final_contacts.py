"""Independent dense-Gaussian check of saved final-contact likelihood updates."""
import csv,datetime as dt,hashlib,json,math,os,sys,time
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
B=Path(__file__).parent;D=Path(sys.argv[1]) if len(sys.argv)>1 else B/'final-contact-comparison'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def readcsv(p):return list(csv.DictReader(p.open()))
state=json.loads((D/'progress.json').read_text());assert state['status']=='conditioned'
result=dict(status='running',started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),checks=[],method='Independent joint Gaussian covariance, not the product sequential bias-update routine; NumPy Gauss–Legendre nodes for the separately declared warm-up mixture. All normalized weights, support masks and identities checked. No trajectory simulation.')
started=time.perf_counter()
for run in state['runs']:
 src=Path(run['source']);out=Path(run['conditioned']);summary=json.loads((out/'summary.json').read_text());assert sha(out/'summary.json')==run['summary_sha256']
 fams={f['name']:[] for f in summary['families']}
 for line in (src/'continuations.jsonl').open():
  r=json.loads(line);cs={c['id']:c for c in r.get('contacts',[])};imp=(r.get('transition') or {}).get('impact');bias=r['source_bfo_bias'];base=r['base_draw_weight']*r['fuel_condition_ratio']*math.exp(r.get('control_log_prior_over_proposal',0))
  row=[r['source_index'],r['draw'],r['parent_slot'],r['root_id'],base,bias['mean_hz'],bias['variance_hz2'],imp['point']['time'] if imp else math.inf]
  for obs in summary['source_summary']['contacts']:
   contact=cs.get(obs['id']);fit=contact['fit_against_0011_bias'] if contact else {}
   row += [contact is not None,fit.get('bto_residual_us',math.nan),fit.get('predicted_bfo_without_bias_hz',math.nan)]
  for family in (fams if r['status']=='zero_fuel_compatibility' else [r['family']]):fams[family].append(row)
 for family in summary['families']:
  x=np.asarray(fams[family['name']],dtype=float);base=x[:,4];n=len(x);obs=summary['source_summary']['contacts'];available=x[:,[8,11]].astype(bool);bt=x[:,[9,12]];pred=x[:,[10,13]];res=np.asarray([o['measurement']['bfo'] for o in obs])[None,:]-pred-x[:,5,None];var=x[:,6];times=np.asarray([o['measurement']['time'] for o in obs]);sd=np.asarray([o['measurement']['bfo_sd'] for o in obs]);positive=base>0
  for c in family['cases']:
   case=c['configuration'];used=np.logical_or(case['bto'],case['bfo']);absent=np.any(used[None,:]&~available&(x[:,7,None]<times),axis=1)&positive;unknown=np.any(used[None,:]&~available,axis=1)&positive&~absent;supported=~unknown
   log=np.full(n,-np.inf);ok=positive&~unknown&~absent;ix=np.flatnonzero(ok);log[ix]=np.log(base[ix])
   for j,on in enumerate(case['bto']):
    if on:
     s=obs[j]['measurement']['bto_sd'];log[ix]+=-.5*(bt[ix,j]/s)**2-math.log(s*math.sqrt(2*math.pi))
   sel=np.flatnonzero(case['bfo'])
   if len(sel)==1:
    j=sel[0];v=sd[j]**2+var[ix];log[ix]+=-.5*(np.log(2*math.pi*v)+res[ix,j]**2/v)
   elif len(sel)==2:
    v=var[ix];a=sd[0]**2+v;z=sd[1]**2+v;det=a*z-v*v
    if case['startup']['kind']=='no_offset':
     r=res[ix];log[ix]+=-math.log(2*math.pi)-.5*np.log(det)-.5*(z*r[:,0]**2-2*v*r[:,0]*r[:,1]+a*r[:,1]**2)/det
    else:
     spec=case['startup'];nodes=[]
     for bounds,num in zip([spec['second_offset_hz'],spec['first_minus_second_hz']],spec['quadrature_points']):
      q,w=np.polynomial.legendre.leggauss(num);nodes.append(((bounds[0]+bounds[1])/2+q*(bounds[1]-bounds[0])/2,w/2))
     sec,dec=np.meshgrid(nodes[0][0],nodes[1][0],indexing='ij');o1=(sec+dec).ravel();o2=sec.ravel();lw=np.log(np.outer(nodes[0][1],nodes[1][1]).ravel())
     for start in range(0,len(ix),512):
      k=ix[start:start+512];vv=var[k,None];aa=sd[0]**2+vv;zz=sd[1]**2+vv;dd=aa*zz-vv*vv;r1=res[k,0,None]-o1;r2=res[k,1,None]-o2
      terms=-math.log(2*math.pi)-.5*np.log(dd)-.5*(zz*r1*r1-2*vv*r1*r2+aa*r2*r2)/dd+lw
      log[k]+=logsumexp(terms,axis=1)
   rows=readcsv(out/c['weights_file']);assert sha(out/c['weights_file'])==c['weights_sha256'];ids=np.asarray([[int(r[k]) for k in ['source_index','draw','parent_slot','root_id']] for r in rows]);assert np.array_equal(ids,x[:,:4])
   recorded_support=np.asarray([r['likelihood_supported']=='true' for r in rows]);assert np.array_equal(recorded_support,supported)
   savedlog=np.asarray([float(r['log_unnormalized_weight']) if r['log_unnormalized_weight'] else -np.inf for r in rows]);assert np.array_equal(np.isfinite(log),np.isfinite(savedlog));finite=np.isfinite(log)
   np.testing.assert_allclose(log[finite],savedlog[finite],rtol=2e-12,atol=2e-9)
   w=np.exp(log-logsumexp(log));actual=np.asarray([float(r['conditional_weight']) for r in rows]);np.testing.assert_allclose(w,actual,rtol=2e-9,atol=2e-12)
   check=dict(seed=run['seed'],family=family['name'],case=c['name'],rows=n,max_abs_log_weight_error=float(np.max(np.abs(log[finite]-savedlog[finite]))),max_abs_normalized_weight_error=float(np.max(np.abs(w-actual))),uncomputed_incoming_mass=float(base[unknown].sum()/base.sum()),identity_and_support_masks_equal=True)
   if c['name']=='r600-no-startup-offset' and (B/f"mixed-terminal-sampling/terminal-seed-{run['seed']}-conditioned").exists():
    old=B/f"mixed-terminal-sampling/terminal-seed-{run['seed']}-conditioned"/c['weights_file'];check['original_r600_csv_byte_identical']=sha(old)==sha(out/c['weights_file']);assert check['original_r600_csv_byte_identical']
   result['checks'].append(check);print(run['label'],family['name'],c['name'],check['max_abs_normalized_weight_error'],flush=True)
result.update(status='passed',elapsed_seconds=time.perf_counter()-started,completed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),script_sha256=sha(__file__),conditioning_run_summary_sha256={str(Path(r['conditioned'])/'summary.json'):r['summary_sha256'] for r in state['runs']})
(D/'independent-verification.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
