"""Independent raw-CSV checks of conditional selections and equal-area summaries."""
from pathlib import Path
import csv, datetime as dt, hashlib, json, math, time
import numpy as np

B=Path(__file__).resolve().parent
O=B/'coherence-comparison'
started=time.monotonic()
summary=json.loads((O/'summary.json').read_text())
archived=json.loads((B/'broader-arc-density/summary.json').read_text())
for key in ['regions','quantiles_05_50_95_deg','cell_ranked_probability_areas']:
    assert summary['cases'][0][key] == archived[key], key
arrays=[]; constants=[]
for source in summary['source_runs']:
    path=Path(source['path'])
    s=json.loads((path/'summary.json').read_text())
    assert hashlib.sha256((path/'posterior.csv').read_bytes()).hexdigest()==s['posterior_csv_sha256']
    with (path/'posterior.csv').open() as stream:
        rows=[(float(r['latitude_deg']),float(r['longitude_deg']),float(r['weight']),
               int(r['limited_turns']),r['initial_mode']=='ConstantTrueTrack',int(r['root']))
              for r in csv.DictReader(stream)]
    a=np.asarray(rows,dtype=float);a[:,2]/=math.fsum(a[:,2]);arrays.append(a)
    constants.append(math.log(s['initial_particles'])+s['log_evidence'])
alpha=np.exp(np.asarray(constants)-max(constants));alpha/=math.fsum(alpha)
all_rows=np.concatenate(arrays);w=np.concatenate([a[:,2]*f for a,f in zip(arrays,alpha)])
run=np.repeat(np.arange(len(arrays)),[len(a) for a in arrays])
lat,lon=all_rows[:,0],all_rows[:,1]
# Independent scalar formulation of ellipsoidal cylindrical equal-area projection.
f=1/298.257223563;e2=f*(2-f);e=math.sqrt(e2);earth=6378.137
k=math.cos(math.radians(35))/math.sqrt(1-e2*math.sin(math.radians(35))**2)
def authalic(latitude):
    sine=np.sin(np.radians(latitude))
    return (1-e2)*(sine/(1-e2*sine*sine)-np.log((1-e*sine)/(1+e*sine))/(2*e))
x=earth*k*np.radians(lon-90);y=earth*(authalic(lat)-authalic(-35))/(2*k)
checks=[]
for c in summary['cases']:
    select=np.ones(len(w),dtype=bool)
    if c['maximum_turn_starts'] is not None:select&=all_rows[:,3]<=c['maximum_turn_starts']
    if c['initial_navigation_mode'] is not None:
        assert c['initial_navigation_mode']=='constant_true_track';select&=all_rows[:,4]==1
    mass=math.fsum(w[select]);assert abs(mass-c['probability_of_selection_in_source_pool'])<1e-12
    cw=w*select/mass
    assert abs(math.fsum(cw)-1)<1e-12
    for i,a in enumerate(arrays):
        assert abs(math.fsum(a[:,2][select[run==i]])-c['selection_probability_by_run'][i])<1e-12
    assert abs(math.fsum(cw[(lat>=-38)&(lat<=-35)])-c['regions']['between_35S_and_38S'])<1e-12
    ancestors={}
    for i,a in enumerate(arrays):
        rw=cw[run==i]
        for root,total in zip(*[np.unique(a[:,5]),np.bincount(np.unique(a[:,5],return_inverse=True)[1],weights=rw)]):
            ancestors[(i,int(root))]=float(total)
    root_values=list(ancestors.values())
    assert abs(max(root_values)-c['largest_ancestor_share'])<1e-12
    assert abs(1/math.fsum(v*v for v in root_values)-c['effective_ancestor_count'])<1e-8
    gaps=[]
    for values in [lat,lon]:
        first=run<len(arrays)//2
        signed=cw.copy();signed[first]/=math.fsum(cw[first]);signed[~first]/=-math.fsum(cw[~first])
        points,indices=np.unique(values,return_inverse=True)
        steps=np.bincount(indices,weights=signed)
        gaps.append(float(np.max(np.abs(np.cumsum(steps)))))
    assert np.allclose(gaps,c['independent_group_cdf_difference'],rtol=0,atol=2e-12)
    for size in [5,10,20]:
        cell=np.column_stack([np.floor(y/size),np.floor(x/size)]).astype(np.int64)
        occupied,indices=np.unique(cell,axis=0,return_inverse=True)
        cell_mass=np.bincount(indices,weights=cw)
        positive=cell_mass>0; occupied=occupied[positive];cell_mass=cell_mass[positive]
        saved=np.load(O/f"{c['name']}-area-density-{size}km.npz")
        gx=np.rint(saved['x_edges_km'][0]/size).astype(int);gy=np.rint(saved['y_edges_km'][0]/size).astype(int)
        assert np.allclose(saved['probability_mass'][occupied[:,0]-gy,occupied[:,1]-gx],cell_mass,rtol=0,atol=3e-13)
        assert abs(saved['probability_mass'].sum()-1)<1e-12
        assert np.allclose(saved['probability_mass']/(size*size),saved['probability_density_per_km2'],rtol=0,atol=0)
        cumulative=np.cumsum(np.sort(cell_mass)[::-1])
        for probability in [.5,.8,.9,.95]:
            count=int(np.searchsorted(cumulative,probability))+1
            actual=c['cell_ranked_probability_areas'][str(size)][str(probability)]
            assert count*size*size==actual['area_km2']
            assert abs(cumulative[count-1]-actual['probability_in_selected_cells'])<1e-12
    checks.append(dict(condition=c['name'],retained_probability=mass,coordinate_cdf_gaps=gaps,grid_sizes_km=[5,10,20]))
result=dict(checked_utc=dt.datetime.now(dt.timezone.utc).isoformat(),status='passed',
            report_sha256=hashlib.sha256((O/'summary.json').read_bytes()).hexdigest(),
            verification_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            broad_summaries_identical_to_preexisting_report=True,source_rows=len(w),cases=checks,
            elapsed_seconds=time.monotonic()-started,
            limitations='Checks reporting arithmetic and encoded conditions; does not validate sampler convergence or physical priors.')
(B/'coherence-report-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
