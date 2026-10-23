cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -n -i "arc" prepare/core_set_windows.py prepare/kadri_northern_conditional.py prepare/search_windows_mixture.py | head -20
echo ==== exchange; ls /Users/pete/Downloads/mh370-exchange/; ls /Users/pete/Downloads/mh370-exchange/end-of-flight/ ; ls /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/ ; ls /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary 2>/dev/null | head
find /Users/pete/Downloads/mh370-exchange -maxdepth 3 -iname "*arc*" | head
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/
echo ==== stations; cat data/stations.csv
echo ==== imos recordings; head -3 data/imos/recordings.csv
ls /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/reduced/