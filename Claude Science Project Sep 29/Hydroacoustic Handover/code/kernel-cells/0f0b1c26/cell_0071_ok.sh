cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; grep -n "01:2\|01:3" data/imos/recordings.csv | grep -E "^3(315|376)|3376|3315" | head; python - <<'EOF'
import re
t=open('prepare/imos_noise.py').read()
for name in ['read_volts','gain_db']:
    i=t.find('def '+name); print(t[i:i+1500]); print('-----')
t=open('prepare/run_j_levels_charts.py').read()
i=t.find('read_volts'); print(t[max(0,i-1500):i+1800])
EOF