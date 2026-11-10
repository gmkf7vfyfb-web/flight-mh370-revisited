
import subprocess, os, sys, time
from concurrent.futures import ThreadPoolExecutor
PY = '/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/9b745c65-d925-4513-bd0c-13910d873e06/.venv/python/bin/python'
seeds = ['1','2','3','4','5','6','7','8'], ['9','10','11','12','13','14','15','31']
jobs = [(c, i) for c in ('butmb','au025','au025nomb','mar','fresh10','pw1','pwlow') for i in (0, 1)]
def run(j):
    c, i = j; t0 = time.time()
    with open(f'w48-logs/{c}-{i}.log', 'w') as f:
        r = subprocess.run([PY, 'offline/smooth_stage1_w48.py', c] + seeds[i], env=dict(os.environ, LEVELS='ramp'), stdout=f, stderr=subprocess.STDOUT)
    open('w48-logs/status.txt', 'a').write(f'{c} {i} rc={r.returncode} {round(time.time() - t0)}s\n'); return r.returncode
open('w48-logs/status.txt', 'w').write('start ' + time.ctime() + '\n')
with ThreadPoolExecutor(5) as ex: rcs = list(ex.map(run, jobs))
open('w48-logs/status.txt', 'a').write('ALL-DONE ' + str(rcs) + ' ' + time.ctime() + '\n')
