"""Reuse two archived drift calculations; no new ocean or flight sampling."""
from pathlib import Path
import copy,datetime as dt,hashlib,json,math,os,resource,subprocess,time
B=Path(__file__).resolve().parent;R=Path('/jackbox/home/MH370')
S=B/'drift-source-sampling-status.json';OUT=B/'drift-source-sampling';EXE=B/'spatial-composition-executable'
now=lambda:dt.datetime.now(dt.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')

if S.exists() or OUT.exists():raise RuntimeError('Inspect existing source-sampling comparison; no automatic repeat')
t=time.monotonic();OUT.mkdir()
atlas_path=R/'.sources/ocean-drift-input-preparation/outputs/cmems-full-domain-stringent-stability/stability-summary.json'
atlas=json.loads(atlas_path.read_text())
reference=Path(atlas['runs'][0]['output'])
reference_manifest=json.loads((reference/'run-manifest.json').read_text())
reference_source=json.loads((reference/'source-area.json').read_text())
attribution=json.loads((B/'drift-evidence-attribution-status.json').read_text());assert attribution['status']=='completed'
variants=[];sources=[]
for run in atlas['runs'][1:]:
    directory=Path(run['output']);directory=directory if directory.is_absolute() else R/directory
    path=directory/'source-area.json';manifest=json.loads((directory/'run-manifest.json').read_text())
    assert sha(path)==manifest['outputs']['source-area.json']
    permitted={'executable_sha256','config_path','config_sha256','seed','particles_per_cell','outputs'}
    differences=[k for k in reference_manifest if reference_manifest[k]!=manifest[k]]
    assert set(differences)<=permitted,(run['name'],differences)
    source=json.loads(path.read_text())
    assert [(c['id'],c['position'],c['prior_weight']) for c in source['cells']]==[(c['id'],c['position'],c['prior_weight']) for c in reference_source['cells']]
    source_identity=dict(label=run['name'],path=str(path),sha256=sha(path),manifest_sha256=sha(directory/'run-manifest.json'),
        seed=source['seed'],particles_per_cell=source['particles_per_cell'],executable_sha256=manifest['executable_sha256'],
        differences_from_reference_manifest=differences)
    sources.append(source_identity)
    for kind in ['full-declared','recoveries-only']:
        template=next(v for v in attribution['variants'] if v['id']==kind)
        h=json.loads(Path(template['handoff']).read_text());f=h['families'][0]
        suffix='alternate drift seed' if run['name']=='alternate' else 'doubled drift sample'
        name=kind+'--drift-'+run['name'];label=('9 recoveries + extra conditions' if kind=='full-declared' else '9 recoveries only')+' · '+suffix
        f.update(id=f['id']+'--'+run['name'],label=label,source_result=source_identity)
        f['source_diagnostics_reference_only']=f.pop('source_diagnostics')
        f['conditions'] += ['The archived source calculation changes sampling; its source prior is removed before reuse.']
        f['limitations'] += [
            'The alternate and doubled drift calculations share one executable hash and all declared physical inputs. The reference drift calculation used a different executable hash; full source equivalence across those executables is not established here.',
            'The doubled drift calculation uses the original seed with twice the particle count and is not statistically independent of the reference. No averaging of these drift surfaces is performed.',
        ]
        old={c['id']:c for c in f['cells']};new=[]
        for c in source['cells']:
            assert {r['event_id'] for r in c['recoveries']}==set(template['events'])
            recovered=math.fsum(r['log_compatibility'] for r in c['recoveries'])
            negative=math.fsum(r['log_compatibility'] for r in c['non_recoveries']) if kind=='full-declared' else 0.
            isotope=(c['conditional_isotope_log_compatibility'] or 0.) if kind=='full-declared' else 0.
            if kind=='full-declared':assert abs(recovered+negative+isotope+math.log(c['prior_weight'])-c['combined_log_weight'])<1e-10
            node=copy.deepcopy(old[c['id']]);node.update(evidence_log_likelihood=recovered+negative+isotope,
                status=c['status'],termination_reason_fractions=c['termination_reason_fractions'],
                event_effective_sample_size={r['event_id']:r['effective_sample_size'] for r in c['recoveries']},
                conditional_isotope_log_compatibility=isotope,selected_log_terms=dict(recovered=recovered,non_recovery=negative,isotope=isotope))
            assert math.isfinite(node['evidence_log_likelihood'])
            new.append(node)
        maximum=max(c['evidence_log_likelihood'] for c in new);total=math.fsum(math.exp(c['evidence_log_likelihood']-maximum) for c in new)
        for node in new:node.update(relative_log_likelihood=node['evidence_log_likelihood']-maximum,
            relative_likelihood=math.exp(node['evidence_log_likelihood']-maximum),diagnostic_uniform_cell_mass=math.exp(node['evidence_log_likelihood']-maximum)/total)
        f['cells']=new
        h.update(title='Archived numerical drift-source sensitivity; '+label,
            derivation=dict(source=source_identity,template_sha256=sha(template['handoff']),script_sha256=sha(__file__),source_prior_removed=True))
        frozen=OUT/(name+'.json');write(frozen,h)
        variants.append(dict(id=name,label=label,events=template['events'],isotope=template['isotope'],non_recovery=template['non_recovery'],
            handoff=str(frozen),handoff_sha256=sha(frozen),family_id=f['id'],drift_source=source_identity))
assert sources[0]['executable_sha256']==sources[1]['executable_sha256']
queue=[]
for job in attribution['completed']:
    if job['evidence_variant']!='recoveries-only':continue
    for variant in variants:
        name=f'{job["seed"]}--{job["terminal_family"]}--{variant["id"]}'
        cfg=OUT/(name+'.toml');template=next(v for v in attribution['variants'] if v['id']=='recoveries-only')
        text=Path(job['config']).read_text().replace(job['name'],name).replace(template['handoff'],variant['handoff']).replace(template['family_id'],variant['family_id'])
        cfg.write_text(text)
        queue.append(dict(job,name=name,evidence_variant=variant['id'],config=str(cfg),config_sha256=sha(cfg),output=str(OUT/name)))
state=dict(status='running',started_utc=now(),driver_pid=os.getpid(),executable=str(EXE),executable_sha256=sha(EXE),
    script_sha256=sha(__file__),source_atlas=str(atlas_path),source_atlas_sha256=sha(atlas_path),sources=sources,
    variants=variants,queue=queue,completed=[],limitations=f['limitations'][-2:])
def save():
    state['updated_utc']=now();p=S.with_suffix('.tmp');write(p,state);p.replace(S)
save()
try:
    for job in queue:
        assert sha(job['config'])==job['config_sha256'] and sha(job['parent_summary'])==job['parent_summary_sha256']
        start=time.monotonic()
        with Path(job['output']).with_suffix('.log').open('x') as log:
            child=subprocess.Popen([str(EXE),'apply-conditional-surface','--config',job['config'],'--output',job['output']],cwd=R,stdout=log,stderr=subprocess.STDOUT)
            state['current']=dict(job,pid=child.pid);save()
            if child.wait():raise RuntimeError('Saved-source composition failed: '+job['name'])
        p=Path(job['output'])/'conditional-spatial-sensitivity.json'
        state['completed'].append(dict(job,elapsed_seconds=time.monotonic()-start,output_sha256=sha(p)))
        del state['current'];save()
    state.update(status='completed',finished_utc=now(),elapsed_seconds=time.monotonic()-t,peak_child_rss_kb=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss);save()
    print(json.dumps(dict(status=state['status'],comparisons=len(queue),elapsed_seconds=state['elapsed_seconds'])))
except Exception as error:state.update(status='needs_inspection',error=str(error));save();raise
