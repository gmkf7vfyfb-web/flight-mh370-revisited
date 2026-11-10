
import subprocess, os, sys, time
from concurrent.futures import ThreadPoolExecutor
PY = '/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/9b745c65-d925-4513-bd0c-13910d873e06/.venv/python/bin/python'
tags = ['h_m2.4_s0.25', 'h_m3.0_s0.25', 'h_m3.6_s0.25', 'h_m4.5_s0.25', 'h_m2.4_s0.35', 'h_m3.0_s0.35', 'h_m3.6_s0.35', 'h_m4.5_s0.35', 'h_m2.4_s0.50', 'h_m3.0_s0.50', 'h_m3.6_s0.50', 'h_m4.5_s0.50']
def run(t):
    t0 = time.time()
    with open(f'grid-logs/{t}.log', 'w') as f:
        r = subprocess.run([PY, 'offline/grid_one.py', t, '1,2,3,4'], env=dict(os.environ, LEVELS='ramp'), stdout=f, stderr=subprocess.STDOUT)
    open('grid-logs/status-h.txt', 'a').write(f'{t} rc={r.returncode} {round(time.time() - t0)}s\n'); return r.returncode
open('grid-logs/status-h.txt', 'w').write('start ' + time.ctime() + '\n')
with ThreadPoolExecutor(5) as ex: rcs = list(ex.map(run, tags))
open('grid-logs/status-h.txt', 'a').write('ALL-DONE ' + str(rcs) + ' ' + time.ctime() + '\n')
