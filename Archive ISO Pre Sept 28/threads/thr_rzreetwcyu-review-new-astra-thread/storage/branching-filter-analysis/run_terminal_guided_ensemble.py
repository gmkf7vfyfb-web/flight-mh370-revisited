"""Test the corrected control proposal on independent terminal draws."""
from pathlib import Path
import datetime as dt,hashlib,json,os,subprocess
B=Path(__file__).resolve().parent;P=B/'terminal-guided-status.json';assert not P.exists();exe=B/'terminal-proposal-executable'
s=dict(status='running',driver_pid=os.getpid(),seed=37091821,source_initial_candidates=680000,parent_draws=8192,terminal_families=8,maximum_continuations=65536,configuration=str(B/'terminal-guided-ensemble.json'),output=str(B/'terminal-guided-ensemble'),executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),physical_control_prior_unchanged=True,proposal_bank_sha256=hashlib.sha256((B/'terminal-control-proposal.json').read_bytes()).hexdigest(),total_compute_cap=None)
def save():
 s['updated_utc']=dt.datetime.now(dt.timezone.utc).isoformat();q=P.with_suffix('.tmp');q.write_text(json.dumps(s,indent=2)+'\n');q.replace(P)
save()
try:
 subprocess.run(['python3',str(B/'run_cruise_impact.py'),s['configuration'],s['output'],str(exe)],check=True)
 done=json.loads((B/'terminal-guided-ensemble-status.json').read_text());assert done['status']=='completed',done
 s.update(status='conditioning',sampling_elapsed_seconds=done['elapsed_seconds'],peak_child_rss_kb=done['peak_child_rss_kb']);save()
 subprocess.run([str(exe),'condition-cruise-impacts','--config',str(B/'terminal-guided-conditions.json'),'--output',str(B/'terminal-guided-conditioned')],check=True)
 s.update(status='completed',conditional_output=str(B/'terminal-guided-conditioned'));save()
 with (B/'progress.md').open('a') as f:f.write('\n'+s['updated_utc']+': Corrected-control-proposal ensemble and80contact cases completed. Compare numerical support and weight concentration with the prior-sampled ensemble before choosing further terminal work.\n')
except Exception as e:s.update(status='needs_inspection',error=str(e));save();raise
