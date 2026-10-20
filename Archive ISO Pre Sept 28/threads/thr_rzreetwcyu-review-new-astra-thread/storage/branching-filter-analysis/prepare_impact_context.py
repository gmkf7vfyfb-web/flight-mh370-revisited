"""Freeze attributed map inputs and select exact existing route witnesses."""
from pathlib import Path
import csv,datetime as dt,hashlib,json,math,os,resource,subprocess,time
import numpy as np
B=Path(__file__).resolve().parent;R=Path('/jackbox/home/MH370');OUT=B/'impact-context-inputs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:dt.datetime.now(dt.timezone.utc).isoformat()
def write(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
if OUT.exists():raise RuntimeError('Inspect the existing context preparation; do not replay automatically')
OUT.mkdir();start=time.monotonic()
paths=dict(candidates=R/'.sources/kadri-2024-hydroacoustics/outputs/potential-signals-summary.csv',
    search=R/'.sources/mh370-seabed-search-coverage/data/map/search-evidence-atlas.geojson',
    arc=R/'.sources/kadri-2024-hydroacoustics/data/seventh_arc_fl400.geojson')
targets=list(csv.DictReader(paths['candidates'].open()))[:6]
for t in targets:
    t['id']=t['label'][0]
    t['position']=[float(t['source_point_latitude_deg']),float(t['source_point_longitude_deg_e'])] if t['source_point_latitude_deg'] else None
    # Historical HPD numbers refer to a superseded PDF, not the current map.
    for k in ['integrated_pdf_hpd','integrated_pdf_hpd_fraction','impact_start_utc','impact_end_utc']:t.pop(k,None)
for key in ['search','arc']:(OUT/(key+'.geojson')).write_bytes(paths[key].read_bytes())
source=json.loads((B/'terminal-million-extended-weather-conditioned/summary.json').read_text());histories={};sources=[]
for i,src in enumerate(source['source_summary']['sources']):
    p=Path(src['source'])/'trajectory-examples.json';data=json.loads(p.read_text());sources.append(dict(path=str(p),sha256=sha(p)))
    for e in data['examples']:histories[(i,e['terminal_slot'])]=e
families=['openap26-signed-lift-6-targets','openap26-positive-lift-3-targets']
contacts=['r600-no-startup-offset','neither-final-contact'];selections=[];requests={};cases=[]
for family in families:
    for contact in contacts:
        name=family+'--'+contact+'--cmems-nine-episodes'
        spatial=B/'spatial-million-comparisons'/name/'conditional-spatial-sensitivity.json'
        data=json.loads(spatial.read_text());rows=data['particle_values']
        retained=[r for r in rows if (r['identity']['source_index'],r['identity']['parent_slot']) in histories and r['baseline_weight']>0]
        p=np.deg2rad([[r['latitude_deg'],r['longitude_deg']] for r in retained]);w=np.array([r['baseline_weight'] for r in retained])
        cases.append(dict(terminal_family=family,contact_case=contact,path=str(spatial),sha256=sha(spatial)))
        for t in targets:
            if t['position'] is None:continue
            lat,lon=np.deg2rad(t['position']);distance=2*6371.00038*np.arcsin(np.sqrt(np.sin((p[:,0]-lat)/2)**2+np.cos(lat)*np.cos(p[:,0])*np.sin((p[:,1]-lon)/2)**2))
            nearby=np.flatnonzero(distance<=150.)
            if not len(nearby):raise RuntimeError('No retained route within the declared illustration neighbourhood')
            best=nearby[np.argmax(w[nearby])];closest=int(np.argmin(distance))
            for role,j in [('Highest flight weight within 150 km',int(best)),('Closest retained geographic neighbour',closest)]:
                row=retained[j];identity=row['identity'];key=(identity['source_index'],identity['parent_slot']);e=histories[key]
                request={k:identity[k] for k in ['source_index','draw']};request['family']=identity['terminal_family'];requests[tuple(request.values())]=request
                record=dict(target_id=t['id'],terminal_family=family,contact_case=contact,role=role,distance_km=float(distance[j]),
                    spatial_particle=row,history_source=sources[key[0]],history_terminal_slot=key[1],history_root=e['root'],
                    counts=e['terminal']['flight']['limited_manoeuvre_counts'],mode=e['terminal']['flight']['initial_mode'])
                selections.append(record)
config=json.loads((B/'flight-drift-selected-terminal-traces.json').read_text());config.update(name='impact-context-selected-terminal-traces',requested_traces=list(requests.values()),threads=1,trace_interval_s=10.)
cfg=OUT/'terminal-traces.json';write(cfg,config)
inputs=dict(created_utc=now(),target_selection='Earlier A–F discussion shortlist, not a statistical ranking; C has no southern-arc intersection. E/F are exploratory associations, not published Kadri locations.',
    targets=targets,cases=cases,search=str(OUT/'search.geojson'),arc=str(OUT/'arc.geojson'),
    source_inputs={k:dict(path=str(p),sha256=sha(p)) for k,p in paths.items()},cruise_sources=source['source_summary']['sources'],
    selections=selections,trace_config=str(cfg),trace_config_sha256=sha(cfg),trace_directory=str(B/'impact-context-selected-terminal-traces'),
    selection_rule='For each mapped target and selected flight/contact model, show the highest-flight-weight retained route within 150 km and the closest retained geographic neighbour. Same endpoint choices are deduplicated in drawings. These are illustrative selections among 213 retained exact histories, not samples from an acoustic-conditioned posterior. Report actual distances and contact weights; geographical proximity alone does not establish a satellite or acoustic match.',
    report_conditions=['Broad cruise source: 1,020,000 initial candidates, caps 16 turn/8 Mach/8 altitude starts after 18:25; stated mode/frequency and fuel priors remain.',
        'The paired maps differ only by the supplied CMEMS nine-recovery, isotope and Australian coastal non-recovery compatibility factors. Gain and acoustic evidence are not multiplied into them.',
        'Seventh arc is the archived official FL400 reference; impact altitude is sea level. No impact is forced onto that reference curve.',
        'Historical 2014–17 survey data extents, Bluefin display footprints and approximate 2018 outline are shown as context. Proposed renewed-search bands and AIS tracks are not labelled as searched seabed.',
        'No calibrated searched-area non-detection likelihood is applied. Current campaign swath completion is not known from these outlines.',
        'Kadri target coordinates are conditional geometric constructions. A/B are catalogue entries without recovered corresponding peaks in the published trace. C is unlocalised on the southern arc. D is the preferred reported candidate. E/F are exploratory timing pairs with periodic interference.',
        'These model-conditioned impact PDFs remain numerically and physically provisional.'])
write(B/'impact-context-inputs.json',inputs)
state=dict(status='running',started_utc=now(),config=str(cfg),config_sha256=sha(cfg),output=inputs['trace_directory'],executable=str(B/'terminal-extended-weather-executable'),
    executable_sha256=sha(B/'terminal-extended-weather-executable'),requested_records=len(requests),new_initial_candidates=0)
status_path=B/'impact-context-traces-status.json';write(status_path,state)
try:
    with (B/'impact-context-traces.log').open('x') as log:
        p=subprocess.Popen([state['executable'],'continue-cruise-to-impact','--config',str(cfg),'--output',state['output']],cwd=R,stdout=log,stderr=subprocess.STDOUT)
        state['pid']=p.pid;write(status_path,state)
        if p.wait():raise RuntimeError('Selected terminal replay failed')
    state.update(status='completed_pending_verification',finished_utc=now(),elapsed_seconds=time.monotonic()-start,peak_child_rss_kb=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss);write(status_path,state)
    print(json.dumps(state))
except Exception as e:state.update(status='needs_inspection',error=str(e));write(status_path,state);raise
