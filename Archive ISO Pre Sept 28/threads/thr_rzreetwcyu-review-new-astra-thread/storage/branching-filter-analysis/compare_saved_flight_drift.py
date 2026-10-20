"""Apply existing drift surfaces to completed independent terminal repetitions."""
from pathlib import Path
import datetime as dt,hashlib,json,os,resource,subprocess,time
B=Path(__file__).resolve().parent;R=Path('/jackbox/home/MH370')
S=B/'flight-drift-composition-status.json';EXE=B/'spatial-composition-executable'
now=lambda:dt.datetime.now(dt.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not S.exists()
source_state=json.loads((B/'joint-terminal-replication-status.json').read_text());assert source_state['status']=='completed'
families=['openap26-positive-lift-3-targets','openap2020-positive-lift-3-targets']
contacts=['r600-no-startup-offset','neither-final-contact']
models=['cmems-nine-episodes','cmems-flaperon-stokes-0p5','cmems-flaperon-stokes-1p0','cmems-flaperon-stokes-1p5']
out=B/'joint-terminal-spatial-comparisons';out.mkdir(exist_ok=False)
queue=[]
for run in source_state['runs']:
    seed=json.loads(Path(run['config']).read_text())['seed']
    parent=Path(run['conditional_output'])
    for family in families:
        for contact in contacts:
            for model in models:
                template=B/f'spatial-million-comparisons/{family}--{contact}--{model}.toml'
                name=f'seed-{seed}--{family}--{contact}--{model}'
                text=template.read_text().replace('directory = "'+str(B/'terminal-million-extended-weather-conditioned')+'"','directory = "'+str(parent)+'"')
                original=f'{family}--{contact}--{model}'
                text=text.replace('name = "'+original+'"','name = "'+name+'"').replace('branch_id = "'+original+'"','branch_id = "'+name+'"')
                cfg=out/(name+'.toml');cfg.write_text(text)
                queue.append(dict(name=name,seed=seed,terminal_family=family,contact_case=contact,evidence_model=model,
                    config=str(cfg),config_sha256=sha(cfg),output=str(out/name),
                    parent_summary=str(parent/'summary.json'),parent_summary_sha256=sha(parent/'summary.json'),
                    template_sha256=sha(template)))
state=dict(status='running',started_utc=now(),driver_pid=os.getpid(),executable=str(EXE),executable_sha256=sha(EXE),
    purpose='Compare existing relaxed-flight/drift densities across independent terminal runs; no new trajectory sampling.',queue=queue,completed=[])
def save():
    state['updated_utc']=now();tmp=S.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(S)
save()
try:
    # A metadata correction must preserve the already-recorded numerical values.
    cfg=B/'spatial-million-comparisons/openap26-positive-lift-3-targets--r600-no-startup-offset--cmems-nine-episodes.toml'
    control=B/'spatial-source-count-control';assert not control.exists()
    subprocess.run([str(EXE),'apply-conditional-surface','--config',str(cfg),'--output',str(control)],check=True,stdout=subprocess.DEVNULL)
    a=json.loads((B/'spatial-million-comparisons'/cfg.stem/'conditional-spatial-sensitivity.json').read_text())
    c=json.loads((control/'conditional-spatial-sensitivity.json').read_text())
    assert {k:v for k,v in a.items() if k!='limitations'}=={k:v for k,v in c.items() if k!='limitations'}
    changes=[(x,y) for x,y in zip(a['limitations'],c['limitations']) if x!=y]
    assert len(changes)==1 and 'four cruise source' in changes[0][0] and '6 cruise source' in changes[0][1]
    (B/'spatial-source-count-verification.json').write_text(json.dumps(dict(checked_utc=now(),status='passed',
        original_sha256=sha(B/'spatial-million-comparisons'/cfg.stem/'conditional-spatial-sensitivity.json'),
        corrected_sha256=sha(control/'conditional-spatial-sensitivity.json'),all_numerical_values_identical=True,changed_text=changes),indent=2)+'\n')
    for job in queue:
        assert sha(job['config'])==job['config_sha256'] and sha(job['parent_summary'])==job['parent_summary_sha256']
        output=Path(job['output']);assert not output.exists()
        command=[str(EXE),'apply-conditional-surface','--config',job['config'],'--output',str(output)]
        state['current']=dict(job,started_utc=now());start=time.monotonic()
        with output.with_suffix('.log').open('x') as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,cwd=R);state['current']['pid']=child.pid;save();code=child.wait()
        if code:raise RuntimeError(f'Conditional surface failed, no automatic repeat: {job["name"]}')
        result=json.loads((output/'conditional-spatial-sensitivity.json').read_text())
        assert abs(sum(r['conditional_weight'] for r in result['particle_values'])-1)<1e-10
        state['completed'].append(dict(job,elapsed_seconds=time.monotonic()-start,
            source_summary_sha256=sha(output/'conditional-spatial-sensitivity.json'),
            conditional_effective_rows=result['conditional_effective_sample_size'],supported_baseline_mass=result['supported_baseline_mass']))
        state.pop('current');save()
    state.update(status='completed',finished_utc=now(),peak_child_rss_kb=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss);save()
    with (B/'progress.md').open('a') as f:f.write('\n'+now()+': Applied existing drift surfaces to both saved independent terminal repetitions:32 comparisons, two aerodynamic families, R600 versus neither final contact, nine debris versus three separate flaperon Stokes cases. No new trajectory simulation. Source-count metadata correction independently preserves all original numerical values. Assess peak persistence and ancestry before interpreting.\n')
except Exception as error:
    state.update(status='needs_inspection',error=str(error));save();raise
