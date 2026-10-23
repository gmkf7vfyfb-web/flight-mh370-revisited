cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
import json
st=open('../data/stations.csv').read().splitlines()[:3]; print(st)
EOF
python -c "
import imos_ram_grid as I, inspect; print(inspect.getsource(I.fg_db_per_km))"; grep -n "^SRC\|^BANDS" f35a_eta_calibration.py; grep -n "BOTTOMS\|^FG" air9_tl_validation.py | head -5