"""Independent source-term, spatial-query, weight and reported-metric checks."""
from pathlib import Path
import csv,datetime as dt,hashlib,json,math,time
import numpy as np

B=Path(__file__).resolve().parent;R=Path('/jackbox/home/MH370')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
start=time.monotonic()
state=json.loads((B/'drift-evidence-attribution-status.json').read_text());assert state['status']=='completed'
extra_path=B/'drift-source-sampling-status.json'
if extra_path.exists():
    extra=json.loads(extra_path.read_text());assert extra['status']=='completed'
    state['completed']+=extra['completed'];state['variants']+=extra['variants']
report=json.loads((B/'flight-drift-comparison/summary.json').read_text())
source=json.loads(Path(state['source_path']).read_text());assert sha(state['source_path'])==state['source_sha256']
surface=json.loads((R/'inputs/evidence/ocean-drift-cmems-full-domain.json').read_text())['families'][0]
base_cells={c['id']:c for c in source['cells']};nodes=surface['cells'];source_cache={}
coordinates=np.deg2rad([[c['latitude_deg'],c['longitude_deg']] for c in nodes])
arrays=[]
for item in report['cruise_sources']:
    p=Path(item['source'])/'posterior.csv';assert sha(p)==item['posterior_sha256']
    with p.open() as f:arrays.append(np.array([(float(r['latitude_deg']),float(r['longitude_deg']),int(r['root'])) for r in csv.DictReader(f)]))
queried={};checks=[]
for job in state['completed']:
    variant=next(v for v in state['variants'] if v['id']==job['evidence_variant'])
    assert sha(variant['handoff'])==variant['handoff_sha256']
    derived=json.loads(Path(variant['handoff']).read_text())['families'][0]
    if 'drift_source' in variant:
        identity=variant['drift_source'];source_path=identity['path']
        if source_path not in source_cache:
            assert sha(source_path)==identity['sha256']
            source_cache[source_path]={c['id']:c for c in json.loads(Path(source_path).read_text())['cells']}
        cells=source_cache[source_path]
    else:cells=base_cells
    raw=[]
    for node in nodes:
        c=cells[node['id']]
        terms=[r['log_compatibility'] for r in c['recoveries'] if r['event_id'] in variant['events']]
        if variant['non_recovery']:terms += [r['log_compatibility'] for r in c['non_recoveries']]
        if variant['isotope']:terms += [c['conditional_isotope_log_compatibility'] or 0.]
        raw.append(math.fsum(terms) if node['relative_log_likelihood'] is not None else -np.inf)
    ell=np.array(raw);ell-=np.max(ell)
    for i,c in enumerate(derived['cells']):
        assert c['id']==nodes[i]['id'] and c['status']==cells[c['id']]['status']
        assert (c['latitude_deg'],c['longitude_deg'])==(nodes[i]['latitude_deg'],nodes[i]['longitude_deg'])
        assert (c['relative_log_likelihood'] is None)==(nodes[i]['relative_log_likelihood'] is None)
        if c['relative_log_likelihood'] is not None:assert abs(c['relative_log_likelihood']-ell[i])<5e-13
    p=Path(job['output'])/'conditional-spatial-sensitivity.json';assert sha(p)==job['output_sha256']
    data=json.loads(p.read_text());rows=data['particle_values'];key=(job['terminal_family'],job['numerical_run'])
    baseline=np.array([r['baseline_weight'] for r in rows]);impact=np.array([[r['latitude_deg'],r['longitude_deg']] for r in rows])
    if key not in queried:
        position=np.deg2rad(impact)
        # Independent haversine query with the documented 3440.065 NM sphere.
        dlat=position[:,None,0]-coordinates[None,:,0];dlon=position[:,None,1]-coordinates[None,:,1]
        hav=np.sin(dlat/2)**2+np.cos(position[:,None,0])*np.cos(coordinates[None,:,0])*np.sin(dlon/2)**2
        distances=2*np.arcsin(np.sqrt(np.clip(hav,0,1)))*3440.065
        nearest=np.argmin(distances,axis=1);distance=distances[np.arange(len(rows)),nearest]
        offsets=np.array([r['impact_time_unix_s']-1394237940 for r in rows])
        supported=(distance<=75)&(np.abs(offsets)<=7200)&np.isfinite(ell[nearest])
        for i,r in enumerate(rows):
            assert (r['support_status']=='supported')==bool(supported[i])
            if supported[i]:
                assert r['surface_cell_id']==nodes[nearest[i]]['id']
                assert abs(r['nearest_surface_distance_nm']-distance[i])<2e-8
        cruise=np.array([arrays[r['identity']['source_index']][r['identity']['parent_slot'],:2] for r in rows])
        identities=[r['identity'] for r in rows]
        for r in rows:assert arrays[r['identity']['source_index']][r['identity']['parent_slot'],2]==r['identity']['root_id']
        queried[key]=dict(nearest=nearest,supported=supported,baseline=baseline,impact=impact,cruise=cruise,identities=identities)
    q=queried[key]
    assert np.array_equal(baseline,q['baseline']) and np.array_equal(impact,q['impact'])
    assert [r['identity'] for r in rows]==q['identities']
    log_factor=np.where(q['supported'],ell[q['nearest']],-np.inf)
    expected=baseline*np.exp(log_factor-np.max(log_factor));expected/=expected.sum()
    actual=np.array([r['conditional_weight'] for r in rows])
    assert np.allclose(actual,expected,atol=2e-13,rtol=2e-11)
    assert abs(data['supported_baseline_mass']-baseline[q['supported']].sum())<1e-12
    shown=next(c for c in report['evidence_attribution']['cases'] if (c['terminal_family'],c['numerical_run'],c['evidence_variant'])==(*key,variant['id']))
    for phase,points in [('impact',impact),('0011',q['cruise'])]:
        m=shown['phases'][phase];latitude=points[:,0]
        assert abs(m['north_of_35S']-actual[latitude>-35].sum())<1e-12
        bins=np.array(m['latitude_bin_centers_deg']);mass=np.histogram(latitude,np.r_[bins-1.25,bins[-1]+1.25],weights=actual)[0]
        assert np.allclose(mass,m['latitude_bin_probabilities'],atol=1e-12,rtol=0)
        for axis in [0,1]:
            order=np.argsort(points[:,axis]);cdf=np.cumsum(actual[order]);quantile=points[order[np.searchsorted(cdf,[.05,.5,.95])],axis]
            assert np.array_equal(quantile,m['quantiles_05_50_95_deg'][axis])
        roots={}
        for r,w in zip(rows,actual):
            identity=r['identity'];root=(identity['source_index'],identity['root_id']);roots[root]=roots.get(root,0.)+w
        ess=1/math.fsum(w*w for w in roots.values())
        assert abs(ess-m['effective_ancestor_count'])<1e-8
    checks.append(dict(terminal_family=key[0],numerical_run=key[1],evidence_variant=variant['id'],rows=len(rows),maximum_weight_error=float(np.max(np.abs(actual-expected)))))
result=dict(status='passed',checked_utc=dt.datetime.now(dt.timezone.utc).isoformat(),script_sha256=sha(__file__),
    report_sha256=sha(B/'flight-drift-comparison/summary.json'),source_sha256=state['source_sha256'],
    scope=f"{len(checks)} source factor reconstructions, independent nearest-cell geometry and temporal support, exact once-only factor normalization, common retained identities, ancestry joins, {2*len(checks)} phase metric checks.",
    checks=checks,elapsed_seconds=time.monotonic()-start)
(B/'drift-evidence-attribution-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
