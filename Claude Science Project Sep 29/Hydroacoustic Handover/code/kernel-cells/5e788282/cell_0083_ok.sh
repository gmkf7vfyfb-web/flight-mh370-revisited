cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6
F="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a/step5_pulse.py"
sed -i '' 's/    fs = 128.0; nfft = int(TWIN \* fs)/    fs = 256.0; nfft = int(TWIN * fs)/; s/(block 7 templates.py physics: hard/(block 7 templates.py physics, synthesis at 256 Hz to hold 70 Hz: hard/' "$F"; grep -n "fs = 256" "$F"
X=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
nohup python "$F" $X/step2 $X/at $X/step5 4 > step5.log 2>&1 &
sleep 100; cat step5.log | head