cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
ls /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/ | head; python -c "import json;print(json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/family-evidence-run-j.json'))['p_core'])"
mkdir -p /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/inputs
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nohup python inputs.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/inputs > /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/inputs/inputs.log 2>&1 &
sleep 20; tail -3 /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/inputs/inputs.log