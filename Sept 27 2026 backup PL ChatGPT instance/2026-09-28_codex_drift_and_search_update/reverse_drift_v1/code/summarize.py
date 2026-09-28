"""Aggregate reproducible source-compatibility scores; never infer object identity."""
from pathlib import Path
import json, itertools, hashlib, platform
import numpy as np
import pandas as pd

B=Path(__file__).resolve().parents[1]
O=B/'results';O.mkdir(exist_ok=True)
MODELS=['bran2016','oscar_v2_final','glorys12_waverys']
SEEDS=[37003801,37003802,37003803]
raw={};checks=[]
for model,day,seed in itertools.product(MODELS,[21,23],SEEDS):
    frames=[pd.DataFrame(json.loads((B/'runs'/f'{prefix}{model}_{day}_{seed}.json').read_text())) for prefix in ['', 'outer_']]
    # The old -100 NM edge becomes an interior cell on the enlarged support.
    frames[0].loc[frames[0].crossNm==-100,'cellAreaKm2']*=2
    df=pd.concat(frames).sort_values(['alongIndex','crossNm']).reset_index(drop=True)
    df['crossIndex']=((df.crossNm+250)/5).astype(int)
    assert len(df)==129*71 and df.id.is_unique
    assert (df.valid_particles==192).all(), 'Invalid trajectories require a missing-mass audit'
    raw[model,day,seed]=df
    if day==23:
        old=pd.read_csv(B/'recovered/outputs/forward-ensemble-primary-seeds.csv')
        old=old[(old.current_model==model)&(old.seed==seed)].set_index('id')
        new=df.set_index('id').loc[old.index]
        err=np.max(np.abs(new.likelihood_pleiades_sigma10_mixture-old.likelihood_all_rating5_sigma10_mixture))
        assert err<1e-12
        checks.append(dict(model=model,seed=seed,max_abs_likelihood_error=err))
pd.DataFrame(checks).to_csv(O/'reproduction_checks.csv',index=False)
grid=next(iter(raw.values()))[['id','alongIndex','crossIndex','alongNm','crossNm','latitude','longitude','cellAreaKm2']]
grid.to_csv(O/'source_grid.csv',index=False)
A=grid.cellAreaKm2.to_numpy();lat=grid.latitude.to_numpy();lon=grid.longitude.to_numpy()
def norm(l):
    assert np.isfinite(l).all() and (l>=0).all()
    p=l*A;return p/p.sum()
def distance(a,b):
    p1,p2=np.radians([a[0],b[0]]);dp=p2-p1;dl=np.radians(b[1]-a[1])
    return 6371.0088*2*np.arcsin(np.sqrt(np.sin(dp/2)**2+np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2))
def metrics(p):
    order=np.argsort(-(p/A));cum=np.cumsum(p[order]);mode=order[0]
    d=dict(mode_lat=lat[mode],mode_lon=lon[mode],mean_lat=p@lat,mean_lon=p@lon,
           mean_cross_nm=p@grid.crossNm,edge_mass=p[(grid.crossNm<=-240)|(grid.crossNm>=90)|(grid.alongIndex<=1)|(grid.alongIndex>=127)].sum(),
           outside_original_strip_mass=p[grid.crossNm < -100].sum())
    for h in [.5,.9,.95]:
        k=np.searchsorted(cum,h);d[f'hpd{int(h*100)}_km2']=A[order[:k+1]].sum();d[f'hpd{int(h*100)}_threshold']=p[order[k]]/A[order[k]]
    for axis,val in [('lat',lat),('lon',lon)]:
        idx=np.argsort(val);cdf=np.cumsum(p[idx]);
        for q in [.025,.5,.975]:d[f'{axis}_q{q}']=np.interp(q,cdf,val[idx])
    return d

pdfs={};likes={};summary=[];seedpdf={};sensitivity=[]
for model in MODELS:
    for day in [21,23]:
        for group in ['pleiades','french4','eastern3','F4']:
            if group=='pleiades' and day==21:continue
            name='pleiades' if group=='pleiades' else f'{group}_{day}'
            for sigma in [5,10,20]:
                key=f'likelihood_{group}_sigma{sigma}_mixture'
                l=np.mean([raw[model,day,s][key].to_numpy() for s in SEEDS],axis=0)
                if sigma==10:
                    likes[model,name]=l;pdfs[model,name]=norm(l)
                    for s in SEEDS:seedpdf[model,name,s]=norm(raw[model,day,s][key].to_numpy())
                else:sensitivity.append(dict(model=model,scenario=name,control=f'kernel_{sigma}km',**metrics(norm(l)),tv_from_primary=.5*np.abs(norm(l)-norm(np.mean([raw[model,day,s][f'likelihood_{group}_sigma10_mixture'].to_numpy() for s in SEEDS],axis=0))).sum()))
            for w in range(3):
                l=np.mean([raw[model,day,s][f'likelihood_{group}_sigma10_windage{w}'].to_numpy() for s in SEEDS],axis=0)
                sensitivity.append(dict(model=model,scenario=name,control=f'windage_{[0,.012,.03][w]}',**metrics(norm(l)),tv_from_primary=.5*np.abs(norm(l)-pdfs[model,name]).sum()))
    for group,number in [('french4',4),('eastern3',3)]:
        for day in [21,23]:
            name=f'{group}_{day}'
            pdfs[model,'combined50_'+name]=.5*(pdfs[model,'pleiades']+pdfs[model,name])
            # Equal prior weight per candidate at the likelihood stage, then normalize.
            pdfs[model,'combined_objects_'+name]=norm((12*likes[model,'pleiades']+number*likes[model,name])/(12+number))
            for s in SEEDS:seedpdf[model,'combined50_'+name,s]=.5*(seedpdf[model,'pleiades',s]+seedpdf[model,name,s])
names=[n for m,n in pdfs if m==MODELS[0]]
for n in names:
    pdfs['equal_models',n]=np.mean([pdfs[m,n] for m in MODELS],axis=0)
    if all((m,n,s) in seedpdf for m in MODELS for s in SEEDS):
        for s in SEEDS:seedpdf['equal_models',n,s]=np.mean([seedpdf[m,n,s] for m in MODELS],axis=0)
for (m,n),p in pdfs.items():
    assert abs(p.sum()-1)<1e-12
    summary.append(dict(model=m,scenario=n,**metrics(p)))
pd.DataFrame(summary).to_csv(O/'summary.csv',index=False)
pd.DataFrame(sensitivity).to_csv(O/'response_sensitivity.csv',index=False)
np.savez_compressed(O/'conditional_pdfs.npz',**{m+'__'+n:p for (m,n),p in pdfs.items()})
pd.DataFrame({m+'__'+n:p for (m,n),p in pdfs.items()},index=grid.id).to_csv(O/'probability_masses.csv.gz')
pd.DataFrame({m+'__'+n:l for (m,n),l in likes.items()},index=grid.id).to_csv(O/'relative_likelihoods.csv.gz')
comparisons=[]
def compare(m,a,b,kind):
    p,q=pdfs[m,a],pdfs[m,b];mp,mq=metrics(p),metrics(q)
    comparisons.append(dict(model=m,first=a,second=b,kind=kind,tv=.5*abs(p-q).sum(),overlap=np.minimum(p,q).sum(),mean_shift_km=distance((mp['mean_lat'],mp['mean_lon']),(mq['mean_lat'],mq['mean_lon'])),mode_shift_km=distance((mp['mode_lat'],mp['mode_lon']),(mq['mode_lat'],mq['mode_lon']))))
for m in MODELS+['equal_models']:
    for g in ['french4','eastern3','combined50_french4','combined50_eastern3']:compare(m,g+'_21',g+'_23','date')
    for d in [21,23]:
        compare(m,f'eastern3_{d}',f'french4_{d}','fourth_object')
        for g in ['french4','eastern3']:
            compare(m,'pleiades',f'{g}_{d}','sensor_overlap')
            compare(m,f'combined50_{g}_{d}',f'combined_objects_{g}_{d}','sensor_weighting')
pd.DataFrame(comparisons).to_csv(O/'sensitivity_comparisons.csv',index=False)
model_comparisons=[]
for n in names:
    for a,b in itertools.combinations(MODELS,2):
        p,q=pdfs[a,n],pdfs[b,n];mp,mq=metrics(p),metrics(q)
        model_comparisons.append(dict(scenario=n,model1=a,model2=b,tv=.5*abs(p-q).sum(),mean_shift_km=distance((mp['mean_lat'],mp['mean_lon']),(mq['mean_lat'],mq['mean_lon'])),mode_shift_km=distance((mp['mode_lat'],mp['mode_lon']),(mq['mode_lat'],mq['mode_lon']))))
pd.DataFrame(model_comparisons).to_csv(O/'model_comparisons.csv',index=False)
edges=np.arange(31.5,40.1,.08)
marginals={'south_latitude_bin_center':(edges[1:]+edges[:-1])/2}
for (m,n),p in pdfs.items():marginals[m+'__'+n]=np.histogram(-lat,bins=edges,weights=p)[0]/.08
pd.DataFrame(marginals).to_csv(O/'latitude_pdf_per_degree.csv',index=False)
convergence=[]
for m,n in {(m,n) for m,n,s in seedpdf}:
    for a,b in itertools.combinations(SEEDS,2):
        p,q=seedpdf[m,n,a],seedpdf[m,n,b];mp,mq=metrics(p),metrics(q)
        convergence.append(dict(model=m,scenario=n,seed1=a,seed2=b,tv=.5*abs(p-q).sum(),mean_shift_km=distance((mp['mean_lat'],mp['mean_lon']),(mq['mean_lat'],mq['mean_lon'])),mode_shift_km=distance((mp['mode_lat'],mp['mode_lon']),(mq['mode_lat'],mq['mode_lon']))))
pd.DataFrame(convergence).to_csv(O/'seed_convergence.csv',index=False)
validation={'all_probabilities_normalized':True,'valid_particles_per_cell_seed':192,'source_cells':len(grid),'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'max_reproduction_absolute_error':max(c['max_abs_likelihood_error'] for c in checks),'max_boundary_mass':max(s['edge_mass'] for s in summary),'source_support_cross_nm':[-250,100],'original_support_cross_nm':[-100,100]}
(O/'validation.json').write_text(json.dumps(validation,indent=2))
print(pd.DataFrame(summary).query('model=="equal_models"')[['scenario','mode_lat','mode_lon','mean_lat','mean_lon','hpd90_km2','edge_mass']].to_string(index=False))
