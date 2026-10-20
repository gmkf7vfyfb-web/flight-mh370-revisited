"""Run one declared terminal experiment and retain status through UI reconnects."""
import datetime as dt,hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path
B=Path(__file__).resolve().parent
cfg=Path(sys.argv[1]);out=Path(sys.argv[2]);state=out.with_name(out.name+'-status.json')
assert not state.exists(), 'Existing run must be inspected, not blindly relaunched'
exe=Path(sys.argv[3]) if len(sys.argv)>3 else B/'cruise-impact-executable'
command=[str(exe),'continue-cruise-to-impact','--config',str(cfg),'--output',str(out)]
s=dict(status='starting',command=command,driver_pid=os.getpid(),configuration_sha256=hashlib.sha256(cfg.read_bytes()).hexdigest(),executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest())
def update():
 s['updated_utc']=dt.datetime.now(dt.timezone.utc).isoformat();temp=state.with_suffix('.tmp');temp.write_text(json.dumps(s,indent=2)+'\n');temp.replace(state)
update();start=time.monotonic()
with out.with_name(out.name+'-execution.log').open('w') as log:
 p=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);s.update(status='running',pid=p.pid);update();code=p.wait()
s.update(status='completed' if code==0 else 'needs_inspection',returncode=code,elapsed_seconds=time.monotonic()-start,peak_child_rss_kb=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss);update()
with (B/'progress.md').open('a') as log:log.write('\n'+s['updated_utc']+f": Terminal run {out.name}: {s['status']}, {s['elapsed_seconds']:.2f}s, peak {s['peak_child_rss_kb']/1024**2:.2f}GiB.\n")
