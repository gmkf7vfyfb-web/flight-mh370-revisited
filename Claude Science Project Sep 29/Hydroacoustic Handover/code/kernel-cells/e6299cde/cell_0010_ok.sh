cd "hydro/Claude Science Project Sep 29"
echo "== royer/infrasound in module clone"; find . -path '*evidence-sweep*' -maxdepth 4 | head; find . -name '*royer_table5*' -o -name '*infrasound*' | head
cd ../../repo && git ls-tree -r --name-only origin/claude-science-sep29 | grep -i "evidence-sweep\|infrasound-ohasisbio\|royer_table5" | head; cd ..
echo "== weak-signal exchange"; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal/{injection,kadri,templates,h08s}
echo "== windows exchange"; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows/ | head; 
echo "== TL grid exchange"; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/ | head
echo "== run-j module cols"; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j/primary-tau-eof | head -5; cat /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j/primary-tau-eof/COLUMNS.txt 2>/dev/null | head -30
echo "== impacts cols"; cat /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/COLUMNS.txt | head -60
echo "== stageB"; ls "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/stageB" "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/kadri2a" "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/weak_signal" 2>&1 | head -40