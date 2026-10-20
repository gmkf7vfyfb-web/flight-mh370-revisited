"""Check plotted impact data, target provenance and geometric route offsets."""
from pathlib import Path
import csv,datetime as dt,hashlib,json,math,time,xml.etree.ElementTree as ET
import numpy as np
import sys
sys.path.insert(0,"/jackbox/home/MH370/crates/reporting/scripts")
from impact_context_report import contour_grid,CONTOUR_SIGMA_KM
B=Path(__file__).resolve().parent;O=B/'impact-context-comparison';t0=time.monotonic();s=json.loads((O/'summary.json').read_text());inputs=json.loads((B/'impact-context-inputs.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(B/'impact-context-inputs.json')==s['input_sha256']
original_targets=list(csv.DictReader(Path(s['source_inputs']['candidates']['path']).open()))[:6]
assert [r['key'] for r in original_targets]==[r['key'] for r in s['targets']]
for original,shown in zip(original_targets,s['targets']):
    assert shown['trace_assessment']==original['trace_assessment']
    if original['source_point_latitude_deg']:assert shown['position']==[float(original['source_point_latitude_deg']),float(original['source_point_longitude_deg_e'])]
    else:assert shown['position'] is None and shown['id']=='C'
for kind in ['search','arc']:assert sha(inputs[kind])==s['source_inputs'][kind]['sha256']
timings=json.loads(Path(s['timing_source']['path']).read_text());assert sha(s['timing_source']['path'])==s['timing_source']['sha256']
for target in s['targets']:
    timing=target['timing'];assert timing==timings['targets'][target['id']]
    if target['position'] is None:
        assert timing['implied_impact_unix_s'] is None;continue
    lat,lon=map(math.radians,target['position']);v=np.array([math.cos(lat)*math.cos(lon),math.cos(lat)*math.sin(lon),math.sin(lat)])
    intervals=[]
    for arrival in timing['arrivals']:
        station=timings['stations'][arrival['station']];a,b=map(math.radians,[station['latitude'],station['longitude']]);u=np.array([math.cos(a)*math.cos(b),math.cos(a)*math.sin(b),math.sin(a)])
        distance=timings['earth_radius_km']*math.atan2(float(np.linalg.norm(np.cross(u,v))),float(u@v))
        assert abs(distance-arrival['distance_km'])<1e-8
        low,high=timings['celerity_km_s'];observed=arrival['arrival_unix_s']
        expected=[observed-distance/low,observed-distance/high]
        assert np.allclose(expected,arrival['impact_time_unix_s'],rtol=0,atol=1e-6)
        intervals.append(expected)
    assert np.allclose(timing['implied_impact_unix_s'],[max(i[0] for i in intervals),min(i[1] for i in intervals)],rtol=0,atol=1e-6)
assert s['targets'][3]['timing']['display_impact']=='00:36:01–00:37:40'
contour_checks=[]
maps={}
for m in s['maps']:
    assert sha(m['path'])==m['sha256'];raw=json.loads(Path(m['path']).read_text());rows=raw['particle_values'];points=np.array([[r['latitude_deg'],r['longitude_deg']] for r in rows]);d=np.load(O/(m['figure']+'.npz'))
    assert np.array_equal(points[:,0],d['latitude_deg']) and np.array_equal(points[:,1],d['longitude_deg'])
    base=np.array([r['baseline_weight'] for r in rows]);joint=np.array([r['conditional_weight'] for r in rows]);assert np.array_equal(base,d['flight_weight']) and np.array_equal(joint,d['flight_drift_weight'])
    ell=np.array([r['relative_log_likelihood'] if r['relative_log_likelihood'] is not None else -np.inf for r in rows]);q=base*np.exp(ell-ell.max());q/=q.sum();assert np.allclose(q,joint,atol=1e-13,rtol=1e-11)
    for weights,metrics in zip([base,joint],m['metrics']):
        visible=(points[:,1]>=84)&(points[:,1]<=105)&(points[:,0]>=-41.5)&(points[:,0]<=-24)
        assert abs(weights.sum()-1)<1e-11 and abs(weights[visible].sum()-metrics['displayed_probability'])<1e-12
        assert abs(weights[points[:,0]>-35].sum()-metrics['north_of_35S'])<1e-12
    for prefix,metrics in zip(['flight','flight_drift'],m['metrics']):
        mass=d[prefix+'_contour_cell_probability'];area=s['contour_display']['cell_km']**2
        assert abs(mass.sum()-1)<1e-12 and not mass[0,:].any() and not mass[-1,:].any()
        for region in metrics['probability_contours']:
            density=mass/area;selected=density>=region['density_threshold_per_km2'];strict=density>region['density_threshold_per_km2']
            enclosed=float(mass[selected].sum());assert abs(enclosed-region['grid_enclosed_probability'])<1e-12
            assert enclosed>=region['probability']-1e-12 and mass[strict].sum()<region['probability']+1e-12
            assert int(selected.sum())*area==region['grid_area_km2']
            contour_checks.append(dict(figure=m['figure'],distribution=prefix,**region))
    assert '<image' not in (O/(m['figure']+'.svg')).read_text(), 'Contours must export as vectors'
    maps[(m['terminal_family'],m['contact_case'])]={tuple(r['identity'][k] for k in ['source_index','parent_slot','draw']):r for r in rows}
examples=0
for page in s['routes']:
    target=next(t for t in s['targets'] if t['id']==page['target_id']);lat,lon=map(math.radians,target['position'])
    for e in page['examples']:
        r=e['spatial_particle'];i=r['identity'];original=maps[(page['terminal_family'],page['contact_case'])][tuple(i[k] for k in ['source_index','parent_slot','draw'])];assert r==original
        lat2,lon2=map(math.radians,[r['latitude_deg'],r['longitude_deg']]);h=math.sin((lat-lat2)/2)**2+math.cos(lat)*math.cos(lat2)*math.sin((lon-lon2)/2)**2;distance=2*6371.00038*math.asin(math.sqrt(h));assert abs(distance-e['distance_km'])<1e-8
        assert dt.datetime.fromisoformat(e['cruise_start_utc'])>=dt.datetime(2014,3,7,18,25,tzinfo=dt.timezone.utc)
        if e['role'].startswith('Highest'):assert e['distance_km']<=150.
        examples+=1
svgs=list(O.glob('*.svg'));assert len(svgs)==24
for p in svgs:assert ET.parse(p).getroot().tag.endswith('svg')
_,_,gaussian_mass,gaussian_regions=contour_grid(np.array([[-35.,95.]]),np.array([1.]))
gaussian_control=[]
for region in gaussian_regions:
    area=-2*math.pi*CONTOUR_SIGMA_KM**2*math.log1p(-region['probability'])
    error=abs(region['grid_area_km2']/area-1)
    assert error<.06 and region['grid_enclosed_probability']>=region['probability']
    gaussian_control.append(dict(probability=region['probability'],analytic_area_km2=area,discrete_area_km2=region['grid_area_km2'],relative_area_error=error))
assert abs(gaussian_mass.sum()-1)<1e-14
result=dict(status='passed' ,checked_utc=dt.datetime.now(dt.timezone.utc).isoformat(),paired_map_cases=len(s['maps']),route_pages=len(s['routes']),route_examples=examples,
    contour_region_checks=contour_checks,analytic_gaussian_control=gaussian_control,timing_points_checked=5,svg_files=len(svgs),report_sha256=sha(O/'summary.json'),script_sha256=sha(__file__),elapsed_seconds=time.monotonic()-t0,
    scope='Source identities, exact A–F geometry/trace labels, independent factor normalization, map mass statistics, exported weight arrays, original route identities, independently calculated distances and post18:25 start times; all SVG files parse. Also checks all 24 contour probability regions, vector exports and five point-specific timing intervals using independent vector geometry.')
(B/'impact-context-numerical-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='contour_region_checks'}))
