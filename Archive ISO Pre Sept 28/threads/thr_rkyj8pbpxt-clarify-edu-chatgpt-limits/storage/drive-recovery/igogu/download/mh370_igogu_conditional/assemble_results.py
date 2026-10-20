#!/usr/bin/env python3
"""Pool independent fixed-proposal importance measures and trace display samples."""
from pathlib import Path
import json,sys,time
import numpy as np
from scipy.special import logsumexp
from model import ROOT,Engine,OBS,decode,T0

def quantile(x,w,q):
 order=np.argsort(x);return np.interp(q,np.cumsum(w[order])/w.sum(),x[order])

def main():
 names=sys.argv[1:] or ['refined_a','refined_b'];records=[]
 for name in names:
  for k in range(5):
   for alt in [0,1]:
    meta=json.loads((ROOT/'output'/name/f'cell_{k}_{alt}.json').read_text())
    if not meta.get('complete'):raise ValueError('Incomplete run')
    records.append((name,k,alt,meta))
 logs=np.array([r[3]['log_evidence'] if r[3].get('supported') else -np.inf for r in records])
 if not np.isfinite(logs).any():raise ValueError('No supported conditional posterior; do not paint a density')
 component_weights=np.exp(logs-logsumexp(logs));engine=Engine(threads=4)
 values=[];weights=[];tags=[];arcs=[];arc_residuals=[];paths=[];flat_params=[];stats=[]
 ix=np.flatnonzero(OBS.kind.eq('arc'));rng=np.random.default_rng(370202609)
 replicate_summaries=[];fine=[];start=time.monotonic()
 for ci,((name,k,alt,meta),weight) in enumerate(zip(records,component_weights)):
  if weight==0:continue
  data=np.load(ROOT/'output'/name/f'cell_{k}_{alt}.npz');u=data['u'];v=data['values'];n=len(v)
  coords=np.zeros((n,len(ix),6),np.float32);residuals=np.zeros((n,len(ix),2),np.float32)
  p=decode(u,k,alt)
  for j,uj in enumerate(u):
   vv,tr,path=engine.trace(uj,k,alt)
   if not np.allclose(vv[[0,1,6,7]],v[j,[0,1,6,7]],atol=1e-7,rtol=0):raise ValueError('Saved state differs from frozen forward model')
   coords[j]=tr[ix,:6];residuals[j,:,0]=tr[ix,6]-OBS.bto_us.to_numpy()[ix];residuals[j,:,1]=tr[ix,7]-OBS.bfo_hz.to_numpy()[ix]
  for j in rng.choice(n,min(n,24),replace=False):
   vf,tf,pf=engine.trace(u[j],k,alt,30)
   if vf[1]>-1e50:
    vv,tc,pc=engine.trace(u[j],k,alt)
    fine.append(dict(component=ci,delta_log_likelihood=float(vf[0]-vv[0]),
       max_BTO_change_us=float(np.max(np.abs(tf[ix,6]-tc[ix,6]))),max_BFO_change_hz=float(np.max(np.abs(tf[:,7]-tc[:,7]))),
       max_endpoint_change_deg=float(np.max(np.abs(vf[6:8]-vv[6:8]))),passes_at_30s=bool(vf[18]),component_weight=float(weight)))
   else:fine.append(dict(component=ci,passes_at_30s=False,physics_at_30s=False,component_weight=float(weight)))
  for j in rng.choice(n,round(300*weight),replace=False):
   vv,tr,path=engine.trace(u[j],k,alt);paths.append(dict(component=ci,turns=k,altitude_class=alt,points=path.tolist()))
  values.append(v);weights.append(np.full(n,weight/n));tags.append(np.tile([ci,k,alt,names.index(name)],(n,1)));arcs.append(coords);arc_residuals.append(residuals);flat_params.append(p)
  stats.append(dict(run=name,turns=k,altitude_class=alt,pooled_component_weight=float(weight),**{z:meta.get(z) for z in ['log_evidence','prior_draws','prior_valid','initial_base_ess','gaussian_to_hard_gate_fraction','distinct_initial_families','largest_initial_family_fraction','unique_parameter_vectors','total_trajectory_evaluations','proposal_draws','importance_ess','relative_evidence_se','largest_importance_weight']}))
  print(json.dumps({'traced_component':[name,k,alt],'weight':float(weight),'samples':n,'elapsed_s':time.monotonic()-start}),flush=True)
 v=np.concatenate(values);w=np.concatenate(weights);tag=np.concatenate(tags);ar=np.concatenate(arcs);res=np.concatenate(arc_residuals);p=np.concatenate(flat_params);w/=w.sum()
 summary={'run_names':names,'prior_probability_per_cell':.1,'posterior_samples':len(v),
          'total_trajectory_evaluations':sum(r[3]['total_trajectory_evaluations'] for r in records),
          'total_prior_draws':sum(r[3]['prior_draws'] for r in records),
          'model_weights':[], 'replicates':[], 'fine_resolution_validation':fine,
          'endpoint_latitude_quantiles':quantile(v[:,6],w,[.025,.5,.975]).tolist(),
          'endpoint_longitude_quantiles':quantile(v[:,7],w,[.025,.5,.975]).tolist(),
          'arrival_seconds_since_182212_quantiles':quantile(p[:,0],w,[.025,.5,.975]).tolist(),
          'fuel_exhaustion_seconds_since_182212_quantiles':quantile(p[:,7],w,[.025,.5,.975]).tolist(),
          'initial_altitude_ft_quantiles':quantile(p[:,1]/.3048,w,[.025,.5,.975]).tolist(),
          'anchor_fuel_kg_quantiles':quantile(v[:,5],w,[.025,.5,.975]).tolist(),
          'maximum_retained_BTO_sigmas':float(v[:,2].max()),'maximum_retained_BFO_error_hz':float(v[:,3].max()),
          'minimum_stall_margin_relative_to_declared_1p2':float(v[:,15].min()),'maximum_retained_bank_deg':float(v[:,16].max()),
          'maximum_retained_mach':float(v[:,14].max()),'maximum_thrust_ratio':float(v[:,17].max()),
          'pooled_evidence_method':'Mean unnormalized fixed-proposal importance measures across independent seeds; component masses proportional to estimated evidence, each with equal 0.1 class prior'}
 for k in range(5):
  for a in [0,1]:summary['model_weights'].append(dict(turns=k,altitude_class=a,posterior_weight=float(w[(tag[:,1]==k)&(tag[:,2]==a)].sum())))
 for name in names:
  selected=[i for i,r in enumerate(records) if r[0]==name];lp=logs[selected];rw=np.exp(lp-logsumexp(lp))
  mass=np.zeros(5);amass=np.zeros(2)
  for ci,mass_i in zip(selected,rw):mass[records[ci][1]]+=mass_i;amass[records[ci][2]]+=mass_i
  chosen=tag[:,3]==names.index(name);ww=w[chosen];ww/=ww.sum()
  summary['replicates'].append(dict(name=name,turn_count_weights=mass.tolist(),altitude_class_weights=amass.tolist(),
       endpoint_latitude_quantiles=quantile(v[chosen,6],ww,[.025,.5,.975]).tolist(),endpoint_longitude_quantiles=quantile(v[chosen,7],ww,[.025,.5,.975]).tolist(),
       model_log_evidence=float(logsumexp(lp)-np.log(10))))
 # Diagnostics use the original independent importance draws, before any
 # stratified display resampling. Conditioning on the frozen learned proposal
 # makes these ordinary independent importance estimates.
 measures=[];measure_tags=[];measure_logw=[];crossings=[]
 for ci,(name,k,a,meta) in enumerate(records):
  f=ROOT/'output'/name/f'importance_measure_{k}_{a}.npz'
  if not f.exists() or not meta.get('supported'):continue
  q=np.load(f);measures.append(q['endpoints']);measure_tags.append(np.full(len(q['log_weights']),ci))
  measure_logw.append(q['log_weights']-np.log(int(q['proposal_count'])))
  crossings.append(q['nominal_crossing_error_s'] if 'nominal_crossing_error_s' in q.files else np.full(len(q['log_weights']),np.nan))
 if measures:
  ep=np.concatenate(measures);et=np.concatenate(measure_tags);elw=np.concatenate(measure_logw)
  ew=np.exp(elw-logsumexp(elw))
  summary.update(independent_importance_ess=float(1/(ew@ew)),largest_individual_importance_weight=float(ew.max()),
       total_independent_proposal_draws=sum(r[3].get('proposal_draws',0) for r in records),
       endpoint_latitude_quantiles=quantile(ep[:,0],ew,[.025,.5,.975]).tolist(),
       endpoint_longitude_quantiles=quantile(ep[:,1],ew,[.025,.5,.975]).tolist())
  variance=sum(cw*cw*r[3].get('relative_evidence_se',0.)**2 for r,cw in zip(records,component_weights) if cw>0)
  summary['pooled_relative_evidence_se']=float(np.sqrt(variance))
  for rep in summary['replicates']:
   selected=[i for i,r in enumerate(records) if r[0]==rep['name']];sel=np.isin(et,selected);ww=ew[sel];ww/=ww.sum()
   rep.update(importance_ess=float(1/(ww@ww)),largest_individual_weight=float(ww.max()),
       endpoint_latitude_quantiles=quantile(ep[sel,0],ww,[.025,.5,.975]).tolist(),
       endpoint_longitude_quantiles=quantile(ep[sel,1],ww,[.025,.5,.975]).tolist())
   mass=component_weights[selected];mass/=mass.sum()
   rep['relative_evidence_se']=float(np.sqrt(sum(mm*mm*records[ci][3].get('relative_evidence_se',0.)**2 for ci,mm in zip(selected,mass) if mm>0)))
  crossing=np.concatenate(crossings);strict=crossing<=60.;strictmass=float(ew[strict].sum())
  summary['legacy_nominal_crossing_test']=dict(maximum_offset_s=60,weighted_retention_fraction=strictmass,
      effective_sample_size=float(strictmass**2/(ew[strict]@ew[strict])) if strictmass else 0,
      raw_positive_weight_survivors=int(strict.sum()),missing_diagnostic=int(np.isnan(crossing).sum()),
      interpretation='Sensitivity only: additional nominal-centre crossings within +/-60s, beyond BTO likelihood at exact logged epoch; not part of primary posterior')
  if strictmass:
   summary['legacy_nominal_crossing_test'].update(endpoint_latitude_quantiles=quantile(ep[strict,0],ew[strict],[.025,.5,.975]).tolist(),
          endpoint_longitude_quantiles=quantile(ep[strict,1],ew[strict],[.025,.5,.975]).tolist())
  np.savez_compressed(ROOT/'output/exact_endpoint_measure.npz',endpoints=ep,weights=ew,component=et,nominal_crossing_error_s=crossing)
  if len(summary['replicates'])==2:
   aa,bb=summary['replicates'];ratio=np.exp(aa['model_log_evidence']-bb['model_log_evidence'])
   summary['replicate_evidence_difference_standard_errors']=float(abs(ratio-1)/np.sqrt((ratio*aa['relative_evidence_se'])**2+bb['relative_evidence_se']**2))
   summary['replicate_turn_weight_maximum_difference']=float(np.max(np.abs(np.array(aa['turn_count_weights'])-bb['turn_count_weights'])))
   group=np.array([names.index(records[ci][0]) for ci in et]);pa=ew[group==0].sum();pb=ew[group==1].sum()
   distances=[]
   for dim in [0,1]:
    order=np.argsort(ep[:,dim]);increments=np.where(group[order]==0,ew[order]/pa,-ew[order]/pb)
    distances.append(float(np.max(np.abs(np.cumsum(increments)))))
   summary['replicate_endpoint_latitude_longitude_cdf_distances']=distances
  # This is a diagnostic status, never a proof that remote modes do not exist.
  summary['sampling_status']='provisional' if (summary['independent_importance_ess']<1000 or summary['largest_individual_importance_weight']>.01 or summary.get('replicate_evidence_difference_standard_errors',0)>3 or summary.get('replicate_turn_weight_maximum_difference',0)>.05 or max(summary.get('replicate_endpoint_latitude_longitude_cdf_distances',[0]))>.05) else 'passes_reported_monte_carlo_checks'
 exploration=[]
 for name in ['run_a','run_b','importance_a','importance_b','refined_pilot']+[f'proposal_training_{i}' for i in range(4)]:
  for fn in (ROOT/'output'/name).glob('cell_*.json'):
   q=json.loads(fn.read_text());exploration.append(q.get('total_trajectory_evaluations',0))
 summary['exploration_and_proposal_training_trajectory_evaluations']=sum(exploration)
 summary['fine_resolution_selected_weighted_pass_fraction']=float(sum(q['component_weight']*q['passes_at_30s'] for q in fine)/sum(q['component_weight'] for q in fine)) if fine else None
 np.savez_compressed(ROOT/'output/posterior_samples.npz',values=v,weights=w,tags=tag,arc_states=ar,arc_residuals=res,physical_parameters=p)
 (ROOT/'output/summary.json').write_text(json.dumps(summary,indent=2)+'\n');(ROOT/'output/component_diagnostics.json').write_text(json.dumps(stats,indent=2)+'\n')
 (ROOT/'output/representative_paths.json').write_text(json.dumps(paths,separators=(',',':')))
 print(json.dumps({k:v for k,v in summary.items() if k!='fine_resolution_validation'},indent=2))
if __name__=='__main__':main()
