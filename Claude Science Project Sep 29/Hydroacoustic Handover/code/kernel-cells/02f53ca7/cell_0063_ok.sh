cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
s=open('tl_recal_block9_charts.py').read()
s=s.replace('''    ram = pd.read_csv(D / "air7_ram.csv") if (D / "air7_ram.csv").exists() else None''',
'''    ram = pd.concat([pd.read_csv(D / f) for f in ("air7_ram.csv", "air7_ram_ext.csv") if (D / f).exists()], ignore_index=True) if (D / "air7_ram.csv").exists() else None''')
s=s.replace('''        for tag, mk in (("air7off+0_H01W", "^"), ("air7off+20_H01W", "v")):
            r = ram[ram.tag == tag].merge(ram[ram.tag == "builder_air9_H01W"][["fc_hz", "tl_ram_db"]], on="fc_hz", suffixes=("", "_a9"))
            ax.plot(r.fc_hz, r.tl_ram_db - r.tl_ram_db_a9, mk, color=GREEN, ms=8, mec="k", label=f"coupled-mode (parabolic equation) check, {'straight' if '+0' in tag else '+20 km'} path")''',
'''        for tag, mk, lab in (("air7off+0_H01W", "^", "straight"), ("air7off+20_H01W", "v", "+20 km"), ("air7off+50_H01W", "<", "+50 km")):
            r = ram[ram.tag == tag].merge(ram[ram.tag == "builder_air9_H01W"][["fc_hz", "tl_ram_db"]], on="fc_hz", suffixes=("", "_a9")).sort_values("fc_hz")
            if len(r):
                ax.plot(r.fc_hz, r.tl_ram_db - r.tl_ram_db_a9, mk, color=GREEN, ms=8, mec="k", ls="none", label=f"coupled-mode (parabolic equation) check, {lab} path")''')
s=s.replace('ax.set_title("a  Even the least-lossy path within ±20 km stays 33–41 dB above the measurement", fontsize=9, loc="left")',
 'ax.set_title("a  Every mode-by-mode path stays 33 dB or more above the measurement;\\n   the coupled-mode check brings the straight path down to about 20 dB", fontsize=9, loc="left")')
open('tl_recal_block9_charts.py','w').write(s); print('ok')
EOF
ls "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/digitised" 2>/dev/null; cd hydro && git fetch -q origin hypothesis/hydroacoustics 2>/dev/null; git ls-tree -r --name-only origin/hypothesis/hydroacoustics | grep -i "digitis" | head; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-digitisation/ -R | head -20; date -u