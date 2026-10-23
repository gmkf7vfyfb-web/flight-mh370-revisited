cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6; du -sh tools; X=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a; mkdir -p $X/at; cp -R tools/Kraken tools/KrakenField $X/at/; ls $X/at/Kraken | head -3
rm -rf $X/step2
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
nohup python "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a/step2_tl.py" $X/step2 $X/at 4 > step2.log 2>&1 &
sleep 60; cat step2.log; ls $X/step2/work/*