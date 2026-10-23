cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
python - <<'EOF'
p='charts.py'; s=open(p).read()
s=s.replace('''def foot(fig, plain, tech):
    fig.text(0.01, 0.055, "\\n".join(textwrap.wrap("(i) " + plain, 190)), fontsize=6.5, va="bottom", ha="left", color="#333")
    fig.text(0.01, 0.005, "\\n".join(textwrap.wrap("(ii) " + tech, 190)), fontsize=6.0, va="bottom", ha="left", color="#555")''',
'''def foot(fig, plain, tech, y1=0.005, width=175):
    t2 = "\\n".join(textwrap.wrap("(ii) " + tech, width)); t1 = "\\n".join(textwrap.wrap("(i) " + plain, width))
    n2 = t2.count("\\n") + 1
    fig.text(0.01, y1, t2, fontsize=6.0, va="bottom", ha="left", color="#555")
    fig.text(0.01, y1 + n2 * 0.0105 + 0.012, t1, fontsize=6.5, va="bottom", ha="left", color="#333")''')
s=s.replace('''    for ax in axes[1]:
        ax.set_xlabel("Received peak level relative to the background median (dB)")''',
'''    fig.supxlabel("Received peak level relative to the background median (dB)", y=0.175, fontsize=10)''')
s=s.replace('label=f"matched filter, source duration {t:.2g} s"', 'label=f"matched filter, source duration {t:.3g} s"')
s=s.replace('fig.tight_layout(rect=(0, 0.10, 1, 0.95))', 'fig.tight_layout(rect=(0, 0.19, 1, 0.95))')
s=s.replace('fig.tight_layout(rect=(0, 0.14, 1, 0.97))', 'fig.tight_layout(rect=(0, 0.24, 1, 0.97))')
s=s.replace('figsize=(12.0, 5.2)', 'figsize=(12.0, 6.4)')
open(p,'w').write(s)
EOF
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
python charts.py $OUT/run $OUT/eta $OUT/inputs/inputs.json $OUT/figs 2>&1 | grep -v Warning | tail -2