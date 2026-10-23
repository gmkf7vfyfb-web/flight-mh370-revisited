import os
W="/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6"
os.chdir(W)
MOD=W+"/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
X="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a"
OUT=W+"/charts"
exec(open(MOD+"/prepare/metz_f35a/charts.py").read())