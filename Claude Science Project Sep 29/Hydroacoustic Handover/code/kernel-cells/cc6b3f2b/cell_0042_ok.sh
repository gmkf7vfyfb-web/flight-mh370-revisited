cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n 87,100p h08s_shot_outliers.py; echo ----; python - <<'EOF'
import re
s=open("h08s_pulse_energy.py").read(); i=s.find("def pulses"); print(s[i:i+1500])
EOF
echo ---- ; python - <<'EOF'
s=open("exploratory/off_cadence.py").read(); i=s.find("def off"); print(s[i:i+1200])
EOF