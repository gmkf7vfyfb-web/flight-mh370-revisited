"""Fixed numerical-resolution controls; stop on failures and preserve status."""
from pathlib import Path
import datetime as dt,hashlib,json,subprocess,sys,os
B=Path(__file__).resolve().parent
names=['terminal-parallel-control','terminal-complete-time-refinement','terminal-quarter-control-refinement','terminal-eighth-control-refinement','terminal-sixteenth-control-refinement','terminal-thirtysecond-control-refinement']
p=B/'terminal-resolution-status.json';assert not p.exists()
s=dict(status='running',driver_pid=os.getpid(),runs=[])
def save():
 s['updated_utc']=dt.datetime.now(dt.timezone.utc).isoformat();p.write_text(json.dumps(s,indent=2)+'\n')
save()
try:
 for name in names:
  subprocess.run(['python3',str(B/'run_cruise_impact.py'),str(B/(name+'.json')),str(B/name)],check=True)
  result=json.loads((B/(name+'-status.json')).read_text());s['runs'].append(dict(name=name,**result));save()
  if result['status']!='completed':raise RuntimeError(name+' needs inspection')
  if name=='terminal-parallel-control':
   same=(B/name/'continuations.jsonl').read_bytes()==(B/'terminal-support-control/continuations.jsonl').read_bytes()
   s['serial_parallel_continuations_byte_identical']=same;save()
   if not same:raise RuntimeError('serial/parallel control mismatch')
 s['status']='completed';save()
except Exception as e:
 s.update(status='needs_inspection',error=str(e));save();raise
