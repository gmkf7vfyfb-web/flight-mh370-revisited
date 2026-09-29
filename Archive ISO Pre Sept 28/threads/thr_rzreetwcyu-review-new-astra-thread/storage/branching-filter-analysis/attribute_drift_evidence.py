"""Compose frozen source likelihood terms with saved flight/impact populations.

This artifact preparation is outside the product. The canonical runner receives
ordinary, hashed likelihood inputs and never imports a source recreation.
"""
from pathlib import Path
import copy,datetime as dt,hashlib,json,math,os,resource,subprocess,time

B=Path(__file__).resolve().parent
R=Path('/jackbox/home/MH370')
STATE=B/'drift-evidence-attribution-status.json'
OUT=B/'drift-evidence-attribution'
EXE=B/'spatial-composition-executable'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:dt.datetime.now(dt.timezone.utc).isoformat()

def write(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def main():
    if STATE.exists() or OUT.exists():
        raise RuntimeError('Inspect existing attribution artifacts; do not repeat automatically')
    started=time.monotonic()
    original_input=R/'inputs/evidence/ocean-drift-cmems-full-domain.json'
    handoff=json.loads(original_input.read_text())
    parent=handoff['families'][0]
    source_path=R/parent['source_result']['path']
    assert sha(source_path)==parent['source_result']['sha256']
    source=json.loads(source_path.read_text())
    atlas_path=R/'.sources/ocean-drift-input-preparation/outputs/seventh-arc-drift-sensitivity/summary.json'
    atlas=json.loads(atlas_path.read_text())
    exterior=next(v for v in atlas['variants'] if len(v['included_recovery_event_ids'])==7)
    assert exterior['source_result_sha256']==sha(source_path)
    events=[r['event_id'] for r in source['cells'][0]['recoveries']]
    variants=[
        dict(id='full-declared',label='9 recoveries + isotope + Australian non-recovery conditions',events=events,isotope=True,non_recovery=True),
        dict(id='recoveries-only',label='9 recovered objects only',events=events,isotope=False,non_recovery=False),
        dict(id='recoveries-plus-isotope',label='9 recoveries + isotope condition',events=events,isotope=True,non_recovery=False),
        dict(id='recoveries-plus-non-recovery',label='9 recoveries + Australian non-recovery conditions',events=events,isotope=False,non_recovery=True),
        dict(id='exterior-recoveries-only',label='7 exterior recovered objects only',events=exterior['included_recovery_event_ids'],isotope=False,non_recovery=False),
    ]
    for event in events:
        variants.append(dict(id='omit-'+event,label='Omit '+event.removesuffix('-recovery').replace('-',' '),
            events=[e for e in events if e!=event],isotope=False,non_recovery=False))
    OUT.mkdir()
    cells={c['id']:c for c in source['cells']}
    reconstruction=[]
    for old in parent['cells']:
        cell=cells[old['id']]
        assert {r['event_id'] for r in cell['recoveries']}==set(events)
        debris=math.fsum(r['log_compatibility'] for r in cell['recoveries'])+math.fsum(r['log_compatibility'] for r in cell['non_recoveries'])
        full=debris+(cell['conditional_isotope_log_compatibility'] or 0.)
        assert abs(debris-cell['debris_log_compatibility'])<1e-10
        assert abs(full+math.log(cell['prior_weight'])-cell['combined_log_weight'])<1e-10
        if old['evidence_log_likelihood'] is not None:
            assert abs(full-old['evidence_log_likelihood'])<1e-10
        assert old['source_prior_weight_removed']==cell['prior_weight']
        reconstruction.append(dict(id=old['id'],error=full-old['evidence_log_likelihood']))
    notes=[
        'This is a diagnostic conditional sensitivity, not an admitted or calibrated crash-location posterior.',
        'Recovery terms retain the source model\'s evidence powers, numerical floors and profiled object-response assumptions. No new floor or debris transport simulation is introduced.',
        'All evidence subsets use the same source-cell support and numerical-status mask. Unsupported likelihoods remain uncomputed, not neutral likelihood or physical exclusions.',
        'Source prior weights are removed. The per-cell sum of selected log compatibility terms is applied exactly once to the saved flight/impact weights.',
        'The recovery-only and leave-one-out cases exclude isotope and Australian coastal non-recovery terms. Australian coastal debris non-recovery is distinct from seabed search non-detection.',
        'The exterior-only comparison removes the two interior panels; it does not change the windage or Stokes response of the retained objects.',
        'Source stability and calibration limitations are inherited; no source acceptance check is newly passed by removing evidence.',
        'Leave-one-recovery-out changes show sensitivity within this fixed model. They are not independent validation, additive causal contributions, or evidence that a recovered object is wrongly identified.',
    ]
    for variant in variants:
        derived=copy.deepcopy(handoff)
        family={k:copy.deepcopy(v) for k,v in parent.items() if k not in ['cells','surface_summary','diagnostics','evidence_scope','conditions']}
        family.update(id=parent['id']+'--'+variant['id'],label=variant['label'],admitted=False,decision='diagnostic_only',
            conditions=notes+[f"Selected recovery events: {', '.join(variant['events'])}; isotope={variant['isotope']}; Australian non-recovery={variant['non_recovery']}."],
            limitations=parent['limitations']+notes,
            source_diagnostics=parent['diagnostics'],
            evidence_scope=dict(recoveries=variant['events'],isotope=variant['isotope'],australian_non_recovery=variant['non_recovery']),cells=[])
        if variant['isotope']:
            assert 'reunion-flaperon-recovery' in variant['events']
        for old in parent['cells']:
            cell=cells[old['id']]
            recovered=math.fsum(r['log_compatibility'] for r in cell['recoveries'] if r['event_id'] in variant['events'])
            non_recovery=math.fsum(r['log_compatibility'] for r in cell['non_recoveries']) if variant['non_recovery'] else 0.
            isotope=(cell['conditional_isotope_log_compatibility'] or 0.) if variant['isotope'] else 0.
            new=copy.deepcopy(old)
            new.update(evidence_log_likelihood=recovered+non_recovery+isotope if old['relative_log_likelihood'] is not None else None,
                conditional_isotope_log_compatibility=isotope,
                selected_log_terms=dict(recovered=recovered,non_recovery=non_recovery,isotope=isotope),
                event_effective_sample_size={e:v for e,v in old['event_effective_sample_size'].items() if e in variant['events']})
            family['cells'].append(new)
        maximum=max(c['evidence_log_likelihood'] for c in family['cells'] if c['evidence_log_likelihood'] is not None)
        total=math.fsum(math.exp(c['evidence_log_likelihood']-maximum) for c in family['cells'] if c['evidence_log_likelihood'] is not None)
        for cell in family['cells']:
            ell=cell['evidence_log_likelihood']
            cell.update(relative_log_likelihood=ell-maximum if ell is not None else None,
                relative_likelihood=math.exp(ell-maximum) if ell is not None else None,
                diagnostic_uniform_cell_mass=math.exp(ell-maximum)/total if ell is not None else None)
        derived.update(title='Explicit evidence subsets of the frozen CMEMS conditional drift surface',families=[family],
            derivation=dict(source=parent['source_result'],original_handoff=str(original_input),original_handoff_sha256=sha(original_input),
                script=str(Path(__file__).resolve()),script_sha256=sha(__file__),variant=variant,
                normalization='Sum selected source log-compatibility terms, exclude source prior, subtract maximum over computed common support.'))
        path=OUT/(variant['id']+'.json')
        write(path,derived)
        variant.update(handoff=str(path),handoff_sha256=sha(path),family_id=family['id'])
    write(OUT/'source-term-reconstruction.json',dict(status='passed',source_sha256=sha(source_path),cells=reconstruction,
        maximum_absolute_error=max(abs(c['error']) for c in reconstruction)))
    runs=[dict(label='Original',directory=str(B/'terminal-million-extended-weather-conditioned'))]
    reps=json.loads((B/'joint-terminal-replication-status.json').read_text())
    assert reps['status']=='completed'
    runs += [dict(label=f'Repeat {i+1}',directory=r['conditional_output']) for i,r in enumerate(reps['runs'])]
    families=['openap26-positive-lift-3-targets','openap2020-positive-lift-3-targets']
    queue=[]
    for run in runs:
        summary=Path(run['directory'])/'summary.json'
        seed=json.loads(summary.read_text())['source_summary']['seed']
        for family in families:
            for variant in variants:
                name=f'{seed}--{family}--{variant["id"]}'
                cfg=OUT/(name+'.toml')
                text=f'''schema_version = 1
name = "{name}"
code_revision = "frozen-executable-and-source-hashes"
branch_id = "{name}"
relative_likelihood_floor = 0.0
maximum_source_time_offset_s = 7200.0

[terminal_conditioned_source]
directory = "{run['directory']}"
terminal_family = "{family}"
contact_case = "r600-no-startup-offset"

[model]
kind = "ocean_drift"
handoff = "{variant['handoff']}"
family_id = "{variant['family_id']}"
source_time_unix_s = 1394237940.0
maximum_nearest_cell_distance_nm = 75.0
allow_diagnostic_family = true
'''
                cfg.write_text(text)
                queue.append(dict(name=name,seed=seed,numerical_run=run['label'],terminal_family=family,contact_case='r600-no-startup-offset',
                    evidence_variant=variant['id'],config=str(cfg),config_sha256=sha(cfg),output=str(OUT/name),
                    parent_summary=str(summary),parent_summary_sha256=sha(summary)))
    state=dict(status='running',started_utc=now(),driver_pid=os.getpid(),purpose=__doc__,executable=str(EXE),executable_sha256=sha(EXE),
        script_sha256=sha(__file__),source_path=str(source_path),source_sha256=sha(source_path),
        variants=variants,limitations=notes,queue=queue,completed=[])
    def save():
        state['updated_utc']=now();p=STATE.with_suffix('.tmp');write(p,state);p.replace(STATE)
    save()
    try:
        for job in queue:
            assert sha(job['config'])==job['config_sha256'] and sha(job['parent_summary'])==job['parent_summary_sha256']
            variant=next(v for v in variants if v['id']==job['evidence_variant'])
            assert sha(variant['handoff'])==variant['handoff_sha256']
            t=time.monotonic()
            with Path(job['output']).with_suffix('.log').open('x') as log:
                child=subprocess.Popen([str(EXE),'apply-conditional-surface','--config',job['config'],'--output',job['output']],cwd=R,stdout=log,stderr=subprocess.STDOUT)
                state['current']=dict(job,pid=child.pid);save()
                if child.wait():raise RuntimeError('Conditional composition failed: '+job['name'])
            path=Path(job['output'])/'conditional-spatial-sensitivity.json'
            result=json.loads(path.read_text())
            assert abs(math.fsum(p['conditional_weight'] for p in result['particle_values'])-1)<1e-10
            state['completed'].append(dict(job,elapsed_seconds=time.monotonic()-t,output_sha256=sha(path)))
            del state['current'];save()
        state.update(status='completed',finished_utc=now(),elapsed_seconds=time.monotonic()-started,
            peak_child_rss_kb=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
        save()
        print(json.dumps(dict(status=state['status'],comparisons=len(queue),elapsed_seconds=state['elapsed_seconds'])))
    except Exception as error:
        state.update(status='needs_inspection',error=str(error));save();raise

if __name__=='__main__':main()
