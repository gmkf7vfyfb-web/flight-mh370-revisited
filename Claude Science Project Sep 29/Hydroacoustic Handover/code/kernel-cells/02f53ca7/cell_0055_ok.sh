cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
s=open('tl_recal_block9_charts.py').read()
s=s.replace('''def footnotes(fig, plain, tech, y0=0.005):
    fig.text(0.01, y0 + 0.075, plain, fontsize=6.3, color="#444", ha="left", va="bottom", wrap=True)
    fig.text(0.01, y0, tech, fontsize=6.3, color="#444", ha="left", va="bottom", wrap=True)''',
'''def footnotes(fig, plain, tech, y0=0.008):
    lh = 6.3 * 1.45 / 72 / fig.get_size_inches()[1]
    fig.text(0.01, y0, tech, fontsize=6.3, color="#444", ha="left", va="bottom")
    fig.text(0.01, y0 + lh * (tech.count("\\n") + 1) + 0.6 * lh, plain, fontsize=6.3, color="#444", ha="left", va="bottom")''')
s=s.replace('axes[0].set_ylabel("Received level (dB; measured = source peak level − chart-read loss)")','axes[0].set_ylabel("Received level (dB)")')
s=s.replace('def wrapt(s, n=190):','def wrapt(s, n=175):')
s=s.replace('fig.subplots_adjust(top=0.84, bottom=0.30, left=0.08, right=0.98, wspace=0.08)','fig.subplots_adjust(top=0.84, bottom=0.33, left=0.07, right=0.98, wspace=0.08)')
s=s.replace('fig.subplots_adjust(top=0.85, bottom=0.30, left=0.07, right=0.99, wspace=0.08)','fig.subplots_adjust(top=0.85, bottom=0.33, left=0.06, right=0.99, wspace=0.08)')
s=s.replace('fig.subplots_adjust(top=0.88, bottom=0.30, left=0.07, right=0.93, wspace=0.35)','fig.subplots_adjust(top=0.88, bottom=0.33, left=0.07, right=0.93, wspace=0.35)')
s=s.replace('ax.set_ylabel("Measured minus predicted received level, median removed (dB)")','ax.set_ylabel("Measured minus predicted level, median removed (dB)")')
s=s.replace('ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Extra loss of the air7 path relative to the air9 path at Cape Leeuwin (dB)")','ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Extra loss of the air7 path relative to air9 (dB)")')
open('tl_recal_block9_charts.py','w').write(s)
EOF
RES="$PWD/../../../../../../repo/Claude Science Project Sep 29/results"
python tl_recal_block9_charts.py ../results-data/tl_recal_block9 "$RES" "$RES/hydroacoustics-audit/data/air9_residuals.csv" 2>&1 | tail -2