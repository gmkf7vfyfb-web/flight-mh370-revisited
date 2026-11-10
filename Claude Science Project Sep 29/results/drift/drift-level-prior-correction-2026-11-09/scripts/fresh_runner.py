
import subprocess, os, sys, time
from concurrent.futures import ThreadPoolExecutor
PY = '/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/9b745c65-d925-4513-bd0c-13910d873e06/.venv/python/bin/python'
jobs = [(p, c) for p in ('prod', 'wide', 'high') for c in ('pain14', 'flap3', 'flap10', 'mb3', 'fresh3all', 'fresh10all')]
def run(j):
    p, c = j; t0 = time.time()
    with open(f'fresh-logs/{p}-{c}.log', 'w') as f:
        r = subprocess.run([PY, f'offline/fresh_stage1_{p}.py', c, '1', '2', '3'], env=dict(os.environ, LEVELS='ramp'), stdout=f, stderr=subprocess.STDOUT)
    open('fresh-logs/status.txt', 'a').write(f'{p} {c} rc={r.returncode} {round(time.time() - t0)}s\n'); return r.returncode
open('fresh-logs/status.txt', 'w').write('start ' + time.ctime() + '\n')
with ThreadPoolExecutor(5) as ex: rcs = list(ex.map(run, jobs))
open('fresh-logs/status.txt', 'a').write('ALL-DONE ' + str(rcs) + ' ' + time.ctime() + '\n')
