cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
cat /Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026.json; echo
ls -la /Users/pete/Downloads/mh370-ocean-data/gebco/grid/ | head
cat /Users/pete/Downloads/mh370-ocean-data/woa23/soundspeed/woa23_95A4_m01.json | head -c 1500; echo
ls /Users/pete/Downloads/mh370-ocean-data/woa23/soundspeed/
echo ==== exports; ls /Users/pete/Downloads/mh370-exchange/ocean-transport/paths-calibration/ | head; 
E=/Users/pete/Downloads/mh370-exchange/ocean-transport/paths-calibration
f=$(ls $E/*_bathymetry.csv | head -1); head -3 "$f"; f=$(ls $E/*_soundspeed.csv | head -1); head -3 "$f"
echo ==== arc in kadri_predictions; grep -n -i "arc\|7th\|bto\|lon.*lat" prepare/kadri_predictions.py | head -20
grep -n -i "def receiver_depth" -A8 prepare/f35a_eta_calibration.py
echo ==== search_windows arc; grep -n -i "arc" prepare/search_windows.py | head