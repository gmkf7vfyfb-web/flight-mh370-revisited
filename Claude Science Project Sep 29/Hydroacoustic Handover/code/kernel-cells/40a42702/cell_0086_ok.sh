cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
python - <<'EOF'
p='charts.py'; s=open(p).read()
s=s.replace('''    n2 = t2.count("\\n") + 1
    fig.text(0.01, y1, t2, fontsize=6.0, va="bottom", ha="left", color="#555")
    fig.text(0.01, y1 + n2 * 0.0105 + 0.012, t1, fontsize=6.5, va="bottom", ha="left", color="#333")''',
'''    n2 = t2.count("\\n") + 1; lh = 6.0 / 72 * 1.3 / fig.get_size_inches()[1]
    fig.text(0.01, y1, t2, fontsize=6.0, va="bottom", ha="left", color="#555")
    fig.text(0.01, y1 + n2 * lh + 0.012, t1, fontsize=6.5, va="bottom", ha="left", color="#333")''')
s=s.replace('ax.set_title("Impacts near 37 °S need the least coupling to be detected; the north needs more", fontsize=10, loc="left")',
            'ax.set_title("Coupling needed for an even chance of detection, by impact latitude band", fontsize=10, loc="left")')
s=s.replace('ax.set_yscale("log"); ax.set_ylim(5e-9, 2e-2)', 'ax.set_yscale("log"); ax.set_ylim(2e-5, 2e-2)')
s=s.replace('ax.set_yticks([1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]); ax.set_yticklabels(["10⁻⁸", "10⁻⁷", "10⁻⁶", "10⁻⁵", "10⁻⁴", "10⁻³", "10⁻²"])',
            'ax.set_yticks([1e-4, 1e-3, 1e-2]); ax.set_yticklabels(["10⁻⁴", "10⁻³", "10⁻²"])')
s=s.replace('ax2.set_title("Detection by any recorder against coupling, per 00:19 data option", fontsize=10, loc="left")',
            'ax2.set_title("Chance of detection by any recorder, per 00:19 data option", fontsize=10, loc="left")')
s=s.replace('ax1b.set_ylabel("Share of impact probability in the latitude band", color="#777")', 'ax1b.set_ylabel("Share of impact probability", color="#777")')
s=s.replace('"TL = block 2 grid pass A (PROVISIONAL, on-arc sources, source 10 m) "\n         f"+ RAM-KRAKEN band deltas for the IMOS loggers;', '"TL: IMOS loggers = module RAM-corrected quantile-path table (38.5-31.6 S, clamped beyond); H01W/H08S = block 2 grid pass A (PROVISIONAL, on-arc sources, source 10 m);')
open(p,'w').write(s)
EOF
grep -c "RAM-corrected quantile" charts.py
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
python charts.py $OUT/run $OUT/eta $OUT/inputs/inputs.json $OUT/figs 2>&1 | grep -v Warning | tail -2