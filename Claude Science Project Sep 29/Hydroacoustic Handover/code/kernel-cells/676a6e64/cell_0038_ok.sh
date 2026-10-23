set +e
cd "repo/Claude Science Project Sep 29"
echo "=== evidence sweep files"; ls results/evidence-sweep-2026-10-17/ 2>/dev/null
echo "=== papers dirs"; ls ../"ISO Sept 28 Status"/inputs/papers/hydroacoustics 2>/dev/null | head -30
echo "=== any royer pdf anywhere in Downloads"; find /Users/pete/Downloads -maxdepth 4 -iname '*royer*' -o -maxdepth 4 -iname '*ohasisbio*' -o -maxdepth 4 -iname 'LDO*' 2>/dev/null | head
echo "=== run J strata seed counts + columns"; E=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j; for s in run-j-waypoints run-j-free run-j-descent-climb run-j-repro-radar; do echo "$s $(ls $E/$s | grep -c seed-)"; done; cat $E/run-j-free/seed-1/COLUMNS.txt | head -40
echo "=== tau sidecar keys"; python -c "import numpy as np; z=np.load('$E/run-j-free/seed-1/tau90_v1.npz'); print(list(z.keys())); a=np.load('$E/run-j-free/seed-1/attitude_v1.npz'); print(list(a.keys()))"
echo "=== hydro run-j outputs"; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j/primary-tau-eof | head; cat /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j/primary-tau-eof/README.txt 2>/dev/null | head -30