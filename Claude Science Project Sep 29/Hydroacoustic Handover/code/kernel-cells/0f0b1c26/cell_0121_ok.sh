python - <<'EOF'
s=open('fig3.py').read()
s=s.replace("ax.axvspan(-60,60,","ax.axvspan(-1,1,")
s=s.replace("bottom=0.36","bottom=0.42").replace("figsize=(7.2,4.6)","figsize=(7.2,5.0)")
s=s.replace("bbox_to_anchor=(-0.38,-0.14)","bbox_to_anchor=(-0.38,-0.12)")
s=s.replace("Two Yemenia panels and one Transair panel are also 4 to 9 minutes late","The two Yemenia and the two Transair panels are also 4 to 9 minutes late")
s=s.replace("'Only some of the published crash signals arrive when sound from the crash site can arrive'","'Four of ten published crash signals arrive when sound from the crash site can arrive'")
open('fig3.py','w').write(s)
EOF
python -c "
import pandas as pd; T=pd.read_csv('hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/calibration_events/stage1b/kadri_crash_timing_EXPLORATORY.csv'); print((T.obs_minus_pred_s.abs()<=60).sum())"