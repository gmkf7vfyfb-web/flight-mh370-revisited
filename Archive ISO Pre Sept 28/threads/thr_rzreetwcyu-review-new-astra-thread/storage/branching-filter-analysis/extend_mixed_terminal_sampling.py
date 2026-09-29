"""Fixed fourfold terminal-sampling comparison, followed by checked composition.

No new cruise or ocean model; independent terminal seeds only. The queue stops
after its two runs and the report refresh, or on any error. Status is explicit.
"""
import copy,datetime as dt,hashlib,json,os,subprocess,sys,tarfile,time,tomllib
from pathlib import Path
B=Path(__file__).resolve().parent;R=Path('/jackbox/home/MH370');OUT=B/'mixed-terminal-sampling'
PY='/tmp/mh370-acoustic-venv/bin/python'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:dt.datetime.now(dt.timezone.utc).isoformat()
def write(p,v):
    temp=p.with_suffix('.tmp');temp.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');temp.replace(p)

def main(resume=False):
    retained=read(OUT/'progress.json') if resume else None
    if OUT.exists() and not resume:raise RuntimeError('Inspect retained extension; refusing unchanged repeat')
    if retained:
        try:os.kill(retained['driver_pid'],0)
        except ProcessLookupError:pass
        else:raise RuntimeError('Recorded driver is still alive; no concurrent resume')
    OUT.mkdir(exist_ok=resume);old=read(B/'joint-terminal-replication-status.json');assert old['status']=='completed'
    terminal=Path(old['executable']);assert sha(terminal)==old['executable_sha256']
    compose=B/'spatial-composition-executable';search=R/'target/iteration/mh370'
    template=read(old['runs'][0]['config']);original_condition=read(old['runs'][0]['conditioning'])
    suite=read(B/'debris-search/search-configuration.json')
    parents=[p for p in suite['populations'] if p['metadata']['numerical_run']=='Repeat 2'];assert len(parents)==18
    state=dict(status='prepared',prepared_utc=now(),driver_pid=os.getpid(),completed=[],runs=[],
        reason='New debris/search conditions expose material between-terminal-run variation. Test fourfold numerical effort with independent seeds and unchanged physical models, corrected proposal and source inputs; no arbitrary acceptance threshold.',
        original_draws_per_cruise_source=template['draws_per_source'],draws_per_cruise_source=8192,cruise_sources=len(template['source_runs']),terminal_models=2,
        expected_seconds_per_run=1200,estimate_basis='Four times the earlier approximately293-second 2048-draw/source calculation; 40–50 minutes for the two numerical runs plus conditioning, verification and reporting. Not a runtime cap or convergence promise.',
        executable_sha256={str(p):sha(p) for p in [terminal,compose,search]},script_sha256=sha(__file__),input_search_config_sha256=sha(B/'debris-search/search-configuration.json'))
    for seed,label in [(37094011,'Fourfold A'),(37094012,'Fourfold B')]:
        name='terminal-seed-'+str(seed);cfg=copy.deepcopy(template);cfg.update(name=name,seed=seed,draws_per_source=8192)
        # All physical choices and proposal parameters are identical. The sole
        # sampling changes are count and independent seed.
        assert {k:v for k,v in cfg.items() if k not in ['name','seed','draws_per_source']}=={k:v for k,v in template.items() if k not in ['name','seed','draws_per_source']}
        config=OUT/(name+'.json')
        if retained:assert read(config)==cfg
        else:write(config,cfg)
        source=OUT/name
        condition=copy.deepcopy(original_condition);condition['source']=str(source);condition['cases']=[c for c in condition['cases'] if c['name']=='r600-no-startup-offset'];assert len(condition['cases'])==1
        cp=OUT/(name+'-conditioned.json')
        if retained:assert read(cp)==condition
        else:write(cp,condition)
        state['runs'].append(dict(seed=seed,numerical_run=label,config=str(config),config_sha256=sha(config),source=str(source),condition=str(cp),condition_sha256=sha(cp),conditioned=str(OUT/(name+'-conditioned'))))
    # Archive compact current source and driver identities for this batch.
    files=[p for base in ['crates','configs'] for p in (R/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[R/'Cargo.toml',R/'Cargo.lock']
    if retained:
        assert retained['runs']==state['runs'] and retained['executable_sha256']==state['executable_sha256']
        assert sha(OUT/'source-snapshot.tar.gz')==retained['source_archive_sha256']
        state=retained
        state.setdefault('resumptions',[]).append(dict(utc=now(),previous_driver_pid=state['driver_pid'],driver_sha256=sha(__file__),reason='Previous driver no longer exists; both numerical source summaries are complete. Resume only verified unfinished conditioning/composition/report work.'))
        state['driver_pid']=os.getpid()
    else:
        with tarfile.open(OUT/'source-snapshot.tar.gz','w:gz') as archive:
            for p in files:archive.add(p,arcname=str(p.relative_to(R)),recursive=False)
        state['source_archive_sha256']=sha(OUT/'source-snapshot.tar.gz')
    web=B.parent/'overnight-analysis/web/mh370-running-status.json';started=time.monotonic()
    def save(title,worker=None,finished=False):
        state['checked_utc']=now();write(OUT/'progress.json',state)
        write(web,dict(checked_utc=state['checked_utc'],comparison_finished=finished,jobs=[dict(title=title,recorded_status=state['status'],driver_alive=not finished,driver_pid=os.getpid(),worker_alive=worker is not None,worker_pid=worker,completed_runs=len(state['completed']),planned_runs=2,candidates_per_run=49152,sample_unit='sampled 00:11-to-impact parents, each evaluated under two terminal models; existing 1.02-million cruise pool unchanged',run_started_utc=state.get('run_started_utc'))]))
    def command(args,title,log):
        before=time.monotonic()
        with Path(log).open('x') as stream:
            child=subprocess.Popen(args,cwd=R,stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',MH370_REPORT_PYTHON=PY));save(title,child.pid)
            while child.poll() is None:time.sleep(2);save(title,child.pid if child.poll() is None else None)
            if child.returncode:raise RuntimeError('Command failed; inspect '+str(log))
        return time.monotonic()-before
    try:
        for run in state['runs']:
            completed=next((r for r in state['completed'] if r['seed']==run['seed']),None)
            if completed:
                assert sha(completed['search_manifest'])==completed['search_manifest_sha256']
                assert read(completed['verification'])['status']=='passed'
                continue
            state.update(status='sampling',run_started_utc=now(),active_seed=run['seed']);save('Fourfold terminal ensemble '+run['numerical_run'])
            assert sha(terminal)==state['executable_sha256'][str(terminal)]
            source=Path(run['source'])
            if source.exists():
                summary=read(source/'summary.json')
                assert summary['status']=='conditional_terminal_predictions'
                assert sha(source/'continuations.jsonl')==summary['continuations_sha256']
                resolved=read(source/'resolved-config.json');declared=read(run['config'])
                assert all(resolved[k]==v for k,v in declared.items())
                assert set(resolved)-set(declared)=={'requested_traces','trace_interval_s'}
                assert resolved['requested_traces']==[] and resolved['trace_interval_s'] is None
                elapsed=read(source/'progress.json')['elapsed_seconds']
            else:
                elapsed=command([str(terminal),'continue-cruise-to-impact','--config',run['config'],'--output',run['source']],run['numerical_run']+': sampling unchanged terminal models',OUT/('sample-'+str(run['seed'])+'.log'))
            state['status']='conditioning'
            command([str(terminal),'condition-cruise-impacts','--config',run['condition'],'--output',run['conditioned']],run['numerical_run']+': apply R600 evidence',OUT/('contacts-'+str(run['seed'])+'.log'))
            sys.path.insert(0,str(R/'crates/reporting/scripts'));from cruise_impact_report import validate_numerical_comparison
            validate_numerical_comparison(read(Path(old['runs'][0]['conditional_output'])/'summary.json'),read(Path(run['conditioned'])/'summary.json'))
            newparents=[]
            for p in parents:
                path=Path(p['path']);cfgpath=path.parent.with_suffix('.toml');cfg=tomllib.loads(cfgpath.read_text());meta=p['metadata'];name=str(run['seed'])+'--'+meta['terminal_family']+'--'+meta['evidence_variant']+('' if meta['cowling_seed'] is None else '--cowling-'+str(meta['cowling_seed']))
                newcfg=OUT/(name+'.toml');dest=OUT/name
                text=cfgpath.read_text().replace(cfg['terminal_conditioned_source']['directory'],run['conditioned']).replace(cfg['name'],name)
                newcfg.write_text(text)
                command([str(compose),'apply-conditional-surface','--config',str(newcfg),'--output',str(dest)],run['numerical_run']+': compose the same debris subsets',OUT/(name+'.log'))
                f=dest/'conditional-spatial-sensitivity.json';newparents.append(dict(p,id=name,path=str(f),sha256=sha(f),metadata=dict(meta,numerical_run=run['numerical_run'],terminal_seed=run['seed'])))
            searchcfg=copy.deepcopy(suite);searchcfg['populations']=newparents;sp=OUT/('search-seed-'+str(run['seed'])+'.json');write(sp,searchcfg);so=OUT/('search-seed-'+str(run['seed']))
            command([str(search),'apply-searched-area-evidence','--config',str(sp),'--output',str(so)],run['numerical_run']+': apply the same searched-area conditions',OUT/('search-seed-'+str(run['seed'])+'.log'))
            sm=so/'manifest.json';command([PY,str(B/'verify_debris_search.py'),str(sm)],run['numerical_run']+': independent geometry and weight verification',OUT/('verify-seed-'+str(run['seed'])+'.log'))
            verification=so/'independent-verification.json';assert read(verification)['status']=='passed'
            state['completed'].append(dict(run,terminal_elapsed_seconds=elapsed,search_manifest=str(sm),search_manifest_sha256=sha(sm),verification=str(verification),completed_utc=now()));save('Completed '+run['numerical_run'])
        state['status']='rendering';save('Larger mixed-PDF comparisons complete; rendering browser maps')
        command([str(search),'report-flight-drift','--evidence-only','--analysis',str(B),'--output',str(B/'debris-search-report'),'--inline-output',str(R/'mh370-debris-search.html')],'Render the matched larger-sample comparisons',OUT/'report.log')
        command(['node',str(B/'verify_debris_browser.cjs')],'Check browser selections and all figure links',OUT/'browser-check.log')
        command([PY,str(R/'crates/reporting/scripts/report_index.py'),'--analysis',str(B),'--inline-output',str(R/'mh370-results.html')],'Refresh the current results index',OUT/'index.log')
        state.update(status='completed',completed_utc=now(),continuation_elapsed_seconds=time.monotonic()-started,total_measured_terminal_seconds=sum(r['terminal_elapsed_seconds'] for r in state['completed']));save('Two fourfold terminal comparisons and browser refresh complete',finished=True)
        with (B/'progress.md').open('a') as stream:stream.write('\n'+now()+': Fixed fourfold terminal queue completed two independent runs; all debris/search compositions independently checked and browser refreshed. No new cruise/ocean sampling. No numerical job remains in this queue; next scientific decisions require a new owner turn. See mixed-terminal-sampling/progress.json.\n')
    except Exception as error:
        state.update(status='failed',error=str(error),failed_utc=now());save('Fourfold terminal queue stopped on an error; existing report retained',finished=True)
        with (B/'progress.md').open('a') as stream:stream.write('\n'+now()+': Fourfold terminal queue stopped: '+str(error)+'. No automatic retry; inspect progress and logs.\n')
        raise

if __name__=='__main__':main('--resume' in sys.argv[1:])
