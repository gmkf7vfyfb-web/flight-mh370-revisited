ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal/ 2>/dev/null; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal/templates 2>/dev/null | head
python - <<'EOF'
import numpy as np, glob
for f in glob.glob('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal/templates/*.np*')[:3]:
    z=np.load(f); print(f.split('/')[-1], {k:(z[k].shape,str(z[k].dtype)) for k in z.files} if hasattr(z,'files') else z.shape)
EOF
cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics
cat results-data/kadri_fig9_noise/h01w_panel_b_bands_DIGITISED.csv | head -12
python -c "
import json;d=json.load(open('results-data/stageB/pd_samples_summary.json'));print(d['t_eff_s'])
f=json.load(open('results-data/stageA/summary_union.json'))['fits'];print({k:(v['snr50'],v['snr90']) for k,v in f.items() if 'T_C2|or|0.05' in k})"
du -sh /Users/pete/Downloads/mh370-exchange/hydroacoustics/