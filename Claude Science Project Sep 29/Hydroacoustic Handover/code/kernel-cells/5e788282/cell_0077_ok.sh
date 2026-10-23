cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6
X=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
nohup python "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a/step3_real_arrival.py" /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection $X/step3 4 > step3.log 2>&1 &
echo ok