cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j/primary-tau-eof
cat README.txt | head -60; ls _parts | head -5; ls _parts | wc -l
echo --- tl grid raw; ls ../../run-j-tl-grid/raw | head; ls ../../run-j-tl-grid/raw | wc -l
cd "$OLDPWD/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"
echo --- imos_tl; cat stageB/imos_tl.csv | head -20; echo --- ramcorr; cat ram_check/imos_tl_ramcorr.csv | head -30; echo --- h11; head -5 ram_check/h11_tl_ramcorr.csv; echo --- eta cal; cat ram_check/eta_cal_ramcorr.csv
echo --- blackman; python -c "
import json,numpy as np
print(json.dumps(json.load(open('blackman_noise/blackman_noise_summary.json')))[:1500])
z=np.load('blackman_noise/blackman_noise_curves.npz'); print({k:z[k].shape for k in z.files})
"; head -5 blackman_noise/blackman_noise_panels.csv