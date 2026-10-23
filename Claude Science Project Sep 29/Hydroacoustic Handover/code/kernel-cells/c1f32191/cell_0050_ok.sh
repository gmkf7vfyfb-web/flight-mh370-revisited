cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
s=open("charts.py").read()
s=s.replace('''        ax.set_title(OPT[o] + f"\\nmedian shift {e.shift_median_deg:+.2f}°, mass north of 33°S {e.mass_north_33S_core:.3f} → {e.mass_north_33S_combined:.3f}", loc="left", fontsize=7)''',
'''        ax.set_title(OPT[o] + f"\\nmedian shift {e.shift_median_deg:+.2f}°; mass north of 33°S {e.mass_north_33S_core:.3f} → {e.mass_north_33S_combined:.3f}", loc="left", fontsize=6.5)''')
s=s.replace('''OPT = {"D0": "00:19 data held out", "D2": "00:19 BTO + BFO as recorded", "D3": "00:19 both BFOs as recorded (Holland H2)", "D4": "00:19 both BFOs, shared start-up offset (Holland H1)"}''',
'''OPT = {"D0": "00:19 data held out", "D2": "00:19 BTO + BFO as recorded", "D3": "00:19 both BFOs as recorded (Holland H2)", "D4": "00:19 both BFOs, shared offset (Holland H1)"}''')
open("charts.py","w").write(s); print("ok")
EOF
S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging; tail -1 $S/driver.log; ls $S/_parts | wc -l; df -k /System/Volumes/Data | tail -1