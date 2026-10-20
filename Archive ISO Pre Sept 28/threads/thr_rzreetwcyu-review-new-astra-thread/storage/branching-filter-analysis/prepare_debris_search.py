"""Compose declared debris subsets and unsuccessful-search sensitivities.

Uses saved, hash-checked likelihood terms; no flight or ocean resimulation.
The central Rust runner applies both the spatial and search likelihoods.
"""
import argparse,copy,datetime as dt,hashlib,json,math,os,subprocess,time
from pathlib import Path
import numpy as np

B=Path(__file__).resolve().parent
R=Path('/jackbox/home/MH370')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
now=lambda:dt.datetime.now(dt.timezone.utc).isoformat()
COW='mossel-bay-engine-cowling-recovery'
PAI='paindane-flap-fairing-recovery'
REU='reunion-flaperon-recovery'
INTERIOR={'antsiraka-cabin-panel-recovery','rodrigues-door-panel-recovery'}
def write(p,v):
    t=p.with_suffix('.tmp');t.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');t.replace(p)

def main(out):
    if out.exists():raise RuntimeError('Inspect existing outputs; refusing an unchanged repeat')
    out.mkdir(parents=True);started=time.monotonic()
    old=read(B/'drift-evidence-attribution-status.json');new=read(B/'cowling-drift-composition-status.json')
    assert old['status']==new['status']=='completed'
    src=Path(old['source_path']);assert sha(src)==old['source_sha256'];cells={c['id']:c for c in read(src)['cells']}
    verified=[]
    # Independent multiplicative update of the already normalized older weights.
    for j in new['completed']:
        oldid=j['evidence_variant'].split('--cowling-seed-')[0]
        reference=next(k for k in old['completed'] if (k['seed'],k['terminal_family'],k['evidence_variant'])==(j['seed'],j['terminal_family'],oldid))
        a=read(Path(reference['output'])/'conditional-spatial-sensitivity.json')['particle_values']
        path=Path(j['output'])/'conditional-spatial-sensitivity.json';assert sha(path)==j['output_sha256']
        b=read(path)['particle_values'];assert [r['identity'] for r in a]==[r['identity'] for r in b]
        variant=next(v for v in new['variants'] if v['id']==j['evidence_variant'])
        assert sha(variant['handoff'])==variant['handoff_sha256']
        changes={c['id']:c['cowling_log_change'] for c in read(variant['handoff'])['families'][0]['cells']}
        delta=np.array([changes[r['surface_cell_id']] if r['surface_cell_id'] else 0 for r in b])
        expected=np.array([r['conditional_weight'] for r in a])*np.exp(delta-delta.max());expected/=expected.sum()
        actual=np.array([r['conditional_weight'] for r in b])
        assert np.allclose(expected,actual,atol=2e-13,rtol=2e-11)
        assert all((x['latitude_deg'],x['longitude_deg'],x['baseline_weight'],x['surface_cell_id'])==(y['latitude_deg'],y['longitude_deg'],y['baseline_weight'],y['surface_cell_id']) for x,y in zip(a,b))
        verified.append(dict(name=j['name'],max_weight_difference=float(abs(expected-actual).max())))
    write(out/'cowling-independent-verification.json',dict(status='passed',cases=verified,method='Old normalized joint weights multiplied by exp(new minus old cowling log likelihood), then normalized. All particle identities, positions, baseline weights and queried source cells preserved.'))
    variants=[];jobs=[];populations=[]
    def population(job,variant,seed,field='conditional_weight'):
        path=Path(job['output'])/'conditional-spatial-sensitivity.json'
        suffix='' if seed is None else '--cowling-'+str(seed)
        id=str(job['seed'])+'--'+job['terminal_family']+'--'+variant+suffix
        if any(p['id']==id for p in populations):return
        populations.append(dict(id=id,path=str(path),sha256=sha(path),weight_field=field,
            metadata=dict(terminal_family=job['terminal_family'],numerical_run=job['numerical_run'],terminal_seed=job['seed'],evidence_variant=variant,cowling_seed=seed)))
    for j in old['completed']:
        if j['evidence_variant']=='recoveries-only':population(j,'flight-only',None,'baseline_weight')
        if j['evidence_variant']=='omit-'+COW:population(j,'omit-cowling',None)
    for v in new['variants']:
        if v['base_variant']!='recoveries-only':continue
        for j in new['completed']:
            if j['evidence_variant']==v['id']:population(j,'nine-recoveries',v['cowling_seed'])
        for kind in ['omit-paindane','exterior-only','reunion-only']:
            if kind=='reunion-only' and v['cowling_seed']!=37093011:continue
            keep=({REU} if kind=='reunion-only' else set(v['events'])-({PAI} if kind=='omit-paindane' else INTERIOR))
            seed=None if kind=='reunion-only' else v['cowling_seed']
            id=kind+('' if seed is None else '--cowling-'+str(seed))
            hand=read(v['handoff']);family=hand['families'][0];family['id']=id;family['label']=kind
            family['evidence_scope']=dict(events=sorted(keep),isotope=False,non_recovery=False)
            for c in family['cells']:
                removed=[r['log_compatibility'] for r in cells[c['id']]['recoveries'] if r['event_id'] not in keep]
                recovered=c['selected_log_terms']['recovered']-math.fsum(removed)
                if COW not in keep:recovered-=c['cowling_log_change']
                c['selected_log_terms']={'recovered':recovered,'isotope':0.,'non_recovery':0.}
                if c['evidence_log_likelihood'] is not None:c['evidence_log_likelihood']=recovered
            maximum=max(c['evidence_log_likelihood'] for c in family['cells'] if c['evidence_log_likelihood'] is not None)
            z=math.fsum(math.exp(c['evidence_log_likelihood']-maximum) for c in family['cells'] if c['evidence_log_likelihood'] is not None)
            for c in family['cells']:
                ell=c['evidence_log_likelihood'];c['relative_log_likelihood']=None if ell is None else ell-maximum
                c['relative_likelihood']=None if ell is None else math.exp(ell-maximum)
                c['diagnostic_uniform_cell_mass']=None if ell is None else math.exp(ell-maximum)/z
                c['event_effective_sample_size']={k:w for k,w in c['event_effective_sample_size'].items() if k in keep}
            family['limitations']+=['Only the listed recovered objects are included. No isotope or Australian coastal non-recovery condition.']
            hand['derivation']=dict(script_sha256=sha(__file__),parent_sha256=v['handoff_sha256'],events=sorted(keep),cowling_seed=seed,source_prior_removed=True)
            hp=out/(id+'.json');write(hp,hand);variants.append(dict(id=id,events=sorted(keep),path=str(hp),sha256=sha(hp)))
            for j in new['completed']:
                if j['evidence_variant']!=v['id']:continue
                name=str(j['seed'])+'--'+j['terminal_family']+'--'+id
                cfg=out/(name+'.toml');text=Path(j['config']).read_text()
                text=text.replace(j['name'],name).replace(v['handoff'],str(hp)).replace(v['family_id'],id);cfg.write_text(text)
                jobs.append(dict(j,name=name,config=str(cfg),output=str(out/name),evidence_variant=kind,cowling_seed=seed))
    state=dict(status='running',started_utc=now(),driver_pid=os.getpid(),script_sha256=sha(__file__),new_samples=0,planned_compositions=len(jobs),completed=[])
    live=B.parent/'overnight-analysis/web/mh370-running-status.json'
    def status(title,child=None,done=False):
        state['checked_utc']=now();write(out/'progress.json',state)
        write(live,dict(checked_utc=now(),comparison_finished=done,jobs=[dict(title=title,driver_alive=not done,driver_pid=os.getpid(),worker_pid=child,worker_alive=child is not None,recorded_status=state['status'],completed_runs=len(state['completed']),planned_runs=len(jobs),candidates_per_run=0,sample_unit='saved population compositions; no new paths')]))
    status('Compose matched debris subsets')
    for j in jobs:
        command=[str(B/'spatial-composition-executable'),'apply-conditional-surface','--config',j['config'],'--output',j['output']]
        with Path(j['output']).with_suffix('.log').open('x') as log:
            child=subprocess.Popen(command,cwd=R,stdout=log,stderr=subprocess.STDOUT);status('Compose matched debris subsets',child.pid)
            if child.wait():raise RuntimeError('Composition failed: '+j['name'])
        population(j,j['evidence_variant'],j['cowling_seed']);state['completed'].append(dict(name=j['name'],path=j['output']));status('Compose matched debris subsets')
    geometry=B/'impact-context-inputs/search.geojson'
    scenario=lambda id,label,d,oi=None,dependence='shared_misses':dict(id=id,label=label,dependence=dependence,campaigns=([dict(footprint='atsb-detailed',effective_detection_probability=d)] if d else [])+([] if oi is None else [dict(footprint='oi2018-outline',effective_detection_probability=oi)]))
    scenarios=[scenario('before-search','Before seabed-search evidence',0),scenario('atsb-d50','ATSB footprint: 50% effective detection',.5),scenario('atsb-d80','ATSB footprint: 80% effective detection',.8),scenario('atsb-d94','ATSB footprint: 94% reference',.94),scenario('atsb-oi-shared','ATSB 94% + 2018 outline 60%; shared misses',.94,.6),scenario('atsb-oi-independent','ATSB 94% + 2018 outline 60%; independent misses',.94,.6,'independent')]
    conditions=[
        'Every distribution is conditional on the retained relaxed cruise, fuel, positive-lift terminal controls, R600 BTO/BFO, computed impacts and selected drift support. Underlying numerical and physical validation remains incomplete.',
        'ATSB detailed L0 data footprint is used as a geographic coverage assumption, preserving every interior hole. It is not a verified pointwise usable-sonar mask. Coarse catalogue extents and bounding rectangles are not used.',
        'The reference 0.94 is calculated as 0.974*0.95 + 0.021*0.70 using ATSB (2017), Figure 73, printed p.96 (PDF p.105). Applying that area-averaged assessment uniformly to this footprint is a conditional approximation. The 50% and 80% values are sensitivity settings, not measured probabilities or confidence limits.',
        'Detection values are effective averages including unresolved coverage and target-detectability effects. Known polygon holes are left unassessed; the aggregate 94% reference already discounts reported gaps, so it is not an exact accounting for this different geographic mask.',
        'The 2018 outline is approximate (about 149,000 km2), larger than the operator-reported 112,000 km2 surveyed. Its optional 60% effective detection is a declared scenario, approximately 80% detection times 112/149 area coverage with unknown gaps distributed uniformly. It is not a measured 2018 detection probability.',
        'Multiple shapes within each campaign form a union, with no double counting. Across campaigns, shared misses uses nested detection outcomes; the independent case separately assumes conditionally independent detection. Neither is an estimated dependence law.',
        'No spatial exclusion is assigned from the recent campaign area total because its actual coverage swaths are unavailable here. Planned areas and vessel AIS tracks are not treated as searched seabed.',
        'No binary exclusion, hidden probability floor, resampling, new flight/drift samples or extra multiplication of fuel/drift evidence. These scenarios do not change the archive metadata that marks the footprints ineligible for a calibrated negative-search likelihood.',
    ]
    sources=[dict(citation='ATSB (2017), The Operational Search for MH370, Figure 73 and accompanying text, printed p.96; PDF p.105',url='https://www.atsb.gov.au/sites/default/files/media/5773565/operational-search-for-mh370_final_3oct2017.pdf',pdf_sha256='bb6ccea27d83d42caeaea2dfaad9c8b0b8e9e12c7e75c103fbf0e09628509bf3',area_fractions=dict(high=.974,lower=.021,gaps=.005),reference_detection=dict(high_lower_reference=.95,lower_average=.70,gaps=0),calculated_area_average=.94),dict(citation='Geoscience Australia / AusSeabed, Phase 2 Deep Tow L0 footprint; see retained feature provenance and search evidence register',local_register='/jackbox/home/MH370/.sources/mh370-seabed-search-coverage/data/evidence-register.json')]
    config=dict(schema_version=1,code_revision='explicit executable and input hashes; source files retained in snapshot',geometry=str(geometry),geometry_sha256=sha(geometry),footprints=[dict(id='atsb-detailed',feature_ids=['phase2-deep-tow-l0'],geographic_condition=conditions[1]),dict(id='oi2018-outline',feature_ids=['oi2018_total_outline_approx'],geographic_condition=conditions[4])],populations=populations,scenarios=scenarios,conditions=conditions,sources=sources)
    cfg=out/'search-configuration.json';write(cfg,config)
    command=[str(R/'target/iteration/mh370'),'apply-searched-area-evidence','--config',str(cfg),'--output',str(out/'search-conditioned')]
    with (out/'search-composition.log').open('x') as log:
        child=subprocess.Popen(command,cwd=R,stdout=log,stderr=subprocess.STDOUT);status('Apply searched-area evidence to matched mixed populations',child.pid)
        if child.wait():raise RuntimeError('Search composition failed; inspect log')
    state.update(status='completed',completed_utc=now(),elapsed_seconds=time.monotonic()-started,populations=len(populations),search_conditions=len(scenarios),search_manifest=str(out/'search-conditioned/manifest.json'))
    write(out/'debris-variants.json',variants);status('Debris and search compositions complete',done=True)
    print(json.dumps({k:state[k] for k in ['status','elapsed_seconds','populations','search_conditions']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=B/'debris-search');main(p.parse_args().output)
