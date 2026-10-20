"""Independent saved-data controls for debris and unsuccessful-search composition."""
import hashlib,json,math,sys,time
from pathlib import Path
import numpy as np
from matplotlib.path import Path as PolygonPath

B=Path(__file__).resolve().parent;D=B/'debris-search'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
manifest_path=Path(sys.argv[1]) if len(sys.argv)>1 else D/'search-conditioned/manifest.json'
started=time.monotonic();manifest=read(manifest_path);config=read(manifest['configuration'])
assert sha(manifest['configuration'])==manifest['configuration_sha256']
assert sha(config['geometry'])==config['geometry_sha256']
atlas=read(config['geometry']);coverage={};original_cells={c['id']:c for c in read(read(B/'drift-evidence-attribution-status.json')['source_path'])['cells']}
for f in config['footprints']:
    coverage[f['id']]=[next(g['geometry'] for g in atlas['features'] if g['properties']['id']==i) for i in f['feature_ids']]

def membership(points,geometries):
    result=np.zeros(len(points),bool)
    for g in geometries:
        polygons=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
        for rings in polygons:
            inside=PolygonPath(rings[0]).contains_points(points[:,::-1])
            for hole in rings[1:]:inside &= ~PolygonPath(hole).contains_points(points[:,::-1])
            result |= inside
    return result

cache={};checked=[];largest=0.;coordinate_roundtrip=0.;time_roundtrip=0.
for item in manifest['completed']:
    path=Path(item['path']);assert sha(path)==item['sha256'];data=read(path);p=data['population'];assert sha(p['path'])==p['sha256']
    parent=read(p['path']);rows=parent['particle_values'];points=np.array([[r['latitude_deg'],r['longitude_deg']] for r in rows]);key=(p['metadata']['terminal_family'],p['metadata']['numerical_run'],p['metadata'].get('contact_case','r600-no-startup-offset'))
    assert len(rows)==len(data['particles'])
    assert all(x['identity']==y['identity'] for x,y in zip(rows,data['particles']))
    # Rust and Python JSON decimal parsers can differ in their last binary bit.
    # Bound that representation effect in ULPs and report its physical size.
    for field in ['latitude_deg','longitude_deg','impact_time_unix_s']:
        a=np.array([r[field] for r in rows]);b=np.array([r[field] for r in data['particles']])
        np.testing.assert_array_max_ulp(a,b,maxulp=2)
        if field=='impact_time_unix_s':time_roundtrip=max(time_roundtrip,float(abs(a-b).max()))
        else:coordinate_roundtrip=max(coordinate_roundtrip,float(abs(a-b).max()))
    w=np.array([r[p['weight_field']] for r in rows]);np.testing.assert_array_max_ulp(w,np.array(data['input_weights']),maxulp=2)
    if key not in cache:cache[key]=(points,{id:membership(points,g) for id,g in coverage.items()})
    saved_points,inside=cache[key];assert np.array_equal(points,saved_points)
    for id,m in inside.items():
        assert np.array_equal(m,np.array(data['footprint_membership'][id]))
        assert abs(w[m].sum()-data['covered_mass_before'][id])<1e-12
    for case in data['scenarios']:
        s=case['configuration'];factors=np.ones((len(s['campaigns']),len(w)))
        for k,c in enumerate(s['campaigns']):factors[k,inside[c['footprint']]]=1-c['effective_detection_probability']
        miss=np.ones_like(w) if not len(factors) else (factors.min(axis=0) if s['dependence']=='shared_misses' else factors.prod(axis=0))
        assert np.allclose(miss,case['search_miss_likelihood'],atol=1e-15,rtol=0)
        total=math.fsum((w*miss).tolist());expected=w*miss/total;actual=np.array(case['conditional_weights'])
        largest=max(largest,float(abs(expected-actual).max()));assert np.allclose(expected,actual,atol=2e-13,rtol=2e-11)
        assert abs(total-case['normalizer'])<2e-12
        for id,m in inside.items():assert abs(actual[m].sum()-case['covered_mass_after'][id])<1e-12
        checked.append(dict(population=item['id'],scenario=s['id'],north_of_35S=float(actual[points[:,0]>-35].sum())))

# Independently sum the selected object terms, rather than subtract omissions
# from the archived joint log score as the preparation driver did.
variant_checks=[]
for variant in read(D/'debris-variants.json'):
    assert sha(variant['path'])==variant['sha256'];h=read(variant['path']);keep=set(variant['events']);raw=[]
    for c in h['families'][0]['cells']:
        terms=[r['log_compatibility']+(c['cowling_log_change'] if r['event_id']=='mossel-bay-engine-cowling-recovery' else 0.) for r in original_cells[c['id']]['recoveries'] if r['event_id'] in keep]
        expected=math.fsum(terms)
        assert abs(expected-c['selected_log_terms']['recovered'])<1e-12
        if c['evidence_log_likelihood'] is not None:assert abs(expected-c['evidence_log_likelihood'])<1e-12
        raw.append(expected if c['evidence_log_likelihood'] is not None else -np.inf)
    largest_log=max(raw)
    for c,expected in zip(h['families'][0]['cells'],raw):
        if np.isfinite(expected):assert abs(c['relative_log_likelihood']-(expected-largest_log))<1e-12
    variant_checks.append(variant['id'])
result=dict(status='passed',populations=len(manifest['completed']),search_cases=len(checked),independent_geographic_populations=len(cache),matched_footprint_masks=2*len(cache),maximum_absolute_weight_difference=largest,maximum_json_coordinate_roundtrip_deg=coordinate_roundtrip,maximum_json_time_roundtrip_s=time_roundtrip,debris_subset_handoffs=variant_checks,elapsed_seconds=time.monotonic()-started,script_sha256=sha(__file__),manifest_sha256=sha(manifest_path),method='Independent Matplotlib polygon union/hole calculation compared with Rust regional geometry; direct normalized Bayesian reweighting; exact identities, numeric input preservation within two binary ULPs across JSON parsers; independent sum of selected recovery terms.',cases=checked)
output=manifest_path.parent/'independent-verification.json' if len(sys.argv)>1 else D/'independent-verification.json'
output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'}))
