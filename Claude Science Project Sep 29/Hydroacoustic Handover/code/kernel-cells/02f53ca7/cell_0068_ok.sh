cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
s=open('tl_recal_block9_charts.py').read()
s=s.replace('''        for tag, mk, lab in (("air7off+0_H01W", "^", "straight"), ("air7off+20_H01W", "v", "+20 km"), ("air7off+50_H01W", "<", "+50 km")):
            r = ram[ram.tag == tag].merge(ram[ram.tag == "builder_air9_H01W"][["fc_hz", "tl_ram_db"]], on="fc_hz", suffixes=("", "_a9")).sort_values("fc_hz")
            if len(r):
                ax.plot(r.fc_hz, r.tl_ram_db - r.tl_ram_db_a9, mk, color=GREEN, ms=8, mec="k", ls="none", label=f"coupled-mode (parabolic equation) check, {lab} path")''',
'''        for tag, mk, lab, jit in (("air7off+0_H01W", "^", "straight", 0.955), ("air7off+20_H01W", "v", "+20 km", 1.0), ("air7off+50_H01W", "<", "+50 km", 1.047)):
            r = ram[ram.tag == tag].merge(ram[ram.tag == "builder_air9_H01W"][["fc_hz", "tl_ram_db"]], on="fc_hz", suffixes=("", "_a9")).sort_values("fc_hz")
            if len(r):
                ax.plot(r.fc_hz * jit, r.tl_ram_db - r.tl_ram_db_a9, mk, color=GREEN, ms=7, mec="k", ls="none", label=f"coupled-mode (parabolic equation) check, {lab} path")''')
s=s.replace('ax.set_xlabel("Sideways shift of the path at the ridge (km; + = right of the direction of travel)")','ax.set_xlabel("Sideways shift of the path at the ridge (km; + = right)")')
s=s.replace('''"close the gap; the best path is still 33–41 dB too lossy. (b) Moving 40–50 km to the right clears the ridge, but about 24 dB of extra loss remains. "''',
'''"close the gap; the best path is still 33–41 dB too lossy. A second model that lets sound pass over the ridge more realistically (green) brings the "
                  "straight path to 17–22 dB too lossy. (b) Moving 40–50 km to the right clears the ridge, but about 24 dB of extra loss remains. "''')
s=s.replace('''"(amendment 2 adds +30/+40/+50 km, exploratory). Gap G22. No MH370 posterior enters; C1/C2 stay on every MH370 number.")''',
'''"(amendment 2 adds +30/+40/+50 km; amendment 3 the RAM set; both exploratory). RAM = pyram split-step Padé, dr 2λ, dz λ/20, 9 frequencies per band, no "
                 "absorption in either model for that comparison; RAM medians over 31.5–63 Hz: straight +19.1, +20 km +15.7, +50 km +18.1 dB. Gap G22. No MH370 posterior enters; C1/C2 stay on every MH370 number.")''')
open('tl_recal_block9_charts.py','w').write(s); print('ok')
EOF
RES="$PWD/../../../../../../repo/Claude Science Project Sep 29/results"
python tl_recal_block9_charts.py ../results-data/tl_recal_block9 "$RES" "$RES/hydroacoustics-audit/data/air9_residuals.csv" | tail -1