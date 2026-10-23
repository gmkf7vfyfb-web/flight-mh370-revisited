cd ~/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1; grep -o -iE '"[a-z_]*(t0|epoch|origin|reference_time|time_zero|unix)[a-z_]*": ?[^,}]{0,40}' run.json | sort -u | head -20; grep -o -iE '"[a-z_]*(t0|epoch|origin|unix)[a-z_]*": ?[^,}]{0,40}' terminal.json | sort -u | head
cd ~; python - <<'EOF'
import numpy as np
d=np.load('kadri_box.npz'); S=d['S']; c=list(d['cols'])
for k in ['t_impact_s','t_realised_flameout_s']:
    v=S[:,c.index(k)].astype(float); print(k, np.nanpercentile(v,[1,50,99]))
EOF