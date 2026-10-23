cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
echo "=== h08s_shot_outliers: defs + load ==="; grep -n "^def \|^FS\|^PANEL\|^def load" h08s_shot_outliers.py; sed -n '/^def load/,/^def /p' h08s_shot_outliers.py | head -40
echo "=== h08s_pulse_energy defs ==="; grep -n "^def \|^FS\|^[A-Z_]* =" h08s_pulse_energy.py | head -30
echo "=== imos_detectors defs ==="; grep -n "^def \|^[A-Z_]* = " imos_detectors.py | head -40
echo "=== imos_noise read_volts/decimate ==="; grep -n "^def " imos_noise.py | head -20
echo "=== template main/CLI ==="; sed -n 120,208p h08s_shot_template.py