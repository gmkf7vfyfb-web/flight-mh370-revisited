"""Prepare explicit conditional evidence alternatives from pinned data artifacts."""
from pathlib import Path
import argparse,hashlib,json,math,tomllib
B=Path(__file__).resolve().parent;R=Path('/jackbox/home/MH370')
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,default=B/'terminal-conditioned-seed-37091811')
p.add_argument('--output',type=Path,default=B/'spatial-comparisons')
p.add_argument('--state',type=Path,default=B/'spatial-comparison-status.json')
p.add_argument('--executable',type=Path,default=B/'spatial-conditioning-executable')
p.add_argument('--flaperon-handoff',type=Path)
a=p.parse_args();D=a.output
assert not a.state.exists(), 'Existing state must not be overwritten'
D.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Each flaperon surface already contains its own response and isotope conditions.
# Remove its source prior; never reuse normalized source probability as likelihood.
stability=R/'.sources/ocean-drift-input-preparation/outputs/cmems-glorys12-waverys-response-sensitivity/stability-summary.json'
spec=json.loads(stability.read_text()) if a.flaperon_handoff is None else {'runs':[]};families=[]
for run in spec['runs']:
 p=R/run['output']/'source-area.json';j=json.loads(p.read_text());logs=[]
 for c in j['cells']:
  ll=None if c['combined_log_weight'] is None else c['combined_log_weight']-math.log(c['prior_weight'])
  if ll is not None:assert abs(ll-c['debris_log_compatibility']-c['conditional_isotope_log_compatibility'])<1e-10
  logs.append(ll)
 mx=max(x for x in logs if x is not None);fid='cmems-flaperon-stokes-'+str(run['stokes_velocity_scale']).replace('.','p')
 families.append(dict(id=fid,label=f"Flaperon only: GLORYS12/WAVERYS, Stokes ×{run['stokes_velocity_scale']}",decision='diagnostic_only',admitted=False,failed_checks=[],limitations=[
  'This matched Stokes comparison uses the flaperon recovery and conditional isotope screen only, not the nine recovery episodes in the broader CMEMS surface.',
  'Source observation bandwidth, probability floor, transport support and object response are explicit source-model sensitivities, not calibrated measurements.',
  'Surface was released at 00:19; reusing it for later impacts neglects the difference in the first minutes of drift. Nearest-source distance remains a reported approximation.',
 ],source_result=dict(path=str(p),sha256=sha(p)),source_prior_removed=True,stokes_velocity_scale=run['stokes_velocity_scale'],cells=[dict(id=c['id'],latitude_deg=c['position']['latitude'],longitude_deg=c['position']['longitude'],relative_log_likelihood=None if ll is None else ll-mx,status=c.get('status','source_model_diagnostic')) for c,ll in zip(j['cells'],logs)]))
if a.flaperon_handoff:
 hand=a.flaperon_handoff.resolve();families=json.loads(hand.read_text())['families']
else:
 hand=D/'flaperon-stokes-likelihoods.json';hand.write_text(json.dumps(dict(schema='mh370-ocean-drift-family-likelihood-handoff-v1',families=families),indent=2)+'\n')
source=a.source;summary=json.loads((source/'summary.json').read_text());entries=[]
models=[('cmems-nine-episodes',dict(kind='ocean_drift',handoff=str(R/'inputs/evidence/ocean-drift-cmems-full-domain.json'),family_id='cmems-glorys12-waverys-full-domain',source_time_unix_s=1394237940.,maximum_nearest_cell_distance_nm=75.,allow_diagnostic_family=True))]
models += [(f['id'],dict(kind='ocean_drift',handoff=str(hand),family_id=f['id'],source_time_unix_s=1394237940.,maximum_nearest_cell_distance_nm=75.,allow_diagnostic_family=True)) for f in families]
pbase=R/'inputs/evidence/pleiades-conditional-source-surface'
models += [('pleiades-'+x,dict(kind='pleiades',grid=str(pbase/'grid.csv'),surfaces=str(pbase/'surfaces.csv'),manifest=str(pbase/'manifest.json'),surface_id=x,source_time_unix_s=1394237940.,maximum_nearest_node_distance_nm=5.)) for x in ['bran2016','oscar_v2_final','glorys12_waverys']]
def val(x):return str(x).lower() if isinstance(x,bool) else json.dumps(x)
for f in summary['families']:
 for c in f['cases']:
  for model_id,model in models:
   if model_id!='cmems-nine-episodes' and c['name'] not in ['neither-final-contact','r600-no-startup-offset','r600-shared-startup']:continue
   ident=f["name"]+'--'+c['name']+'--'+model_id;cfg=D/(ident+'.toml');output=D/ident
   cfg.write_text('\n'.join(['schema_version = 1','name = '+val(ident),'code_revision = "executable-and-source-manifest"','branch_id = '+val(ident),'relative_likelihood_floor = 0.0','maximum_source_time_offset_s = 7200.0','','[terminal_conditioned_source]','directory = '+val(str(source)),'terminal_family = '+val(f['name']),'contact_case = '+val(c['name']),'','[model]']+[k+' = '+val(v) for k,v in model.items()])+'\n')
   entries.append(dict(name=ident,terminal_family=f['name'],contact_case=c['name'],evidence_model=model_id,config=str(cfg),config_sha256=sha(cfg),output=str(output)))
a.state.write_text(json.dumps(dict(status='prepared',source=str(source),source_summary_sha256=sha(source/'summary.json'),executable=str(a.executable),executable_sha256=sha(a.executable),completed=[],queue=entries),indent=2)+'\n')
print('Prepared',len(entries),'separate comparisons')
