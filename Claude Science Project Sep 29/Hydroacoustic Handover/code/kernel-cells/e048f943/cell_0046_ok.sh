cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
python - <<'EOF'
import pathlib
p=pathlib.Path('run_j_levels_charts.py'); s=p.read_text()
s=s.replace('''def footnotes(fig, plain, tech, y0=0.005):
    fig.text(0.01, y0 + 0.055, textwrap.fill("Plain-language note: " + plain, 230), fontsize=6.3, va="bottom", ha="left", color="#333333")
    fig.text(0.01, y0, textwrap.fill("Technical note: " + tech, 230), fontsize=6.0, va="bottom", ha="left", color="#333333")''',
'''def footnotes(fig, plain, tech, y0=0.006):
    fw, fh = fig.get_size_inches(); width = int(fw * 21)
    t2 = textwrap.fill("Technical note: " + tech, width); n2 = t2.count("\\n") + 1
    lh = 6.0 / 72 * 1.35 / fh
    fig.text(0.01, y0, t2, fontsize=6.0, va="bottom", ha="left", color="#333333")
    fig.text(0.01, y0 + lh * (n2 + 0.8), textwrap.fill("Plain-language note: " + plain, width), fontsize=6.3, va="bottom", ha="left", color="#333333")''')
# minor tick labels off on log x
s=s.replace('''    ax.set_xlim(2.6, 46); ax.set_ylim(20, 125); ax.grid(alpha=0.25, lw=0.4)''','''    ax.set_xlim(2.6, 46); ax.set_ylim(20, 125); ax.grid(alpha=0.25, lw=0.4); ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())''')
s=s.replace('''            ax.set_xticks([1e-6, 1e-5, 1e-4, 1e-3, 1e-2]); ax.set_xticklabels(["0.000001", "0.00001", "0.0001", "0.001", "0.01"])
        for ax in axs[1]: ax.set_xlabel("Share of impact energy that becomes sound (coupling efficiency)")''','''            ax.set_xticks([1e-6, 1e-5, 1e-4, 1e-3, 1e-2]); ax.set_xticklabels(["0.000001", "0.00001", "0.0001", "0.001", "0.01"]); ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        fig.text(0.52, 0.165, "Share of impact energy that becomes sound (coupling efficiency)", ha="center", va="bottom", fontsize=8)''')
s=s.replace('''fig, axs = plt.subplots(2, 4, figsize=(14, 7.6), sharex=True, sharey=True); fig.subplots_adjust(left=0.05, right=0.99, top=0.86, bottom=0.22, wspace=0.08, hspace=0.25)''',
            '''fig, axs = plt.subplots(2, 4, figsize=(14, 7.6), sharex=True, sharey=True); fig.subplots_adjust(left=0.05, right=0.99, top=0.86, bottom=0.21, wspace=0.08, hspace=0.25)''')
# maps: tighter extents, taller usable area
s=s.replace('''fig, axs = plt.subplots(2, 4, figsize=(14.5, 8.8), sharex=True, sharey=True); fig.subplots_adjust(left=0.045, right=0.9, top=0.88, bottom=0.2, wspace=0.06, hspace=0.18)''',
            '''fig, axs = plt.subplots(2, 4, figsize=(14.5, 7.2), sharex=True, sharey=True); fig.subplots_adjust(left=0.06, right=0.9, top=0.9, bottom=0.2, wspace=0.06, hspace=0.12)''')
s=s.replace('''            ax.set_xlim(70, 125); ax.set_ylim(-45, -18); ax.set_aspect("equal"); ax.grid(alpha=0.2, lw=0.4)''','''            ax.set_xlim(80, 124); ax.set_ylim(-43, -17); ax.set_aspect("equal"); ax.grid(alpha=0.2, lw=0.4)''')
s=s.replace('''ax.annotate(STN[r].split(" logger")[0].replace("Diego Garcia ", "DG "), (rx[r][1], rx[r][0]), xytext=(3, 3), textcoords="offset points", fontsize=5.5)''',
            '''ax.annotate(STN[r].split(" logger")[0].replace("Cape Leeuwin H01W", "Cape Leeuwin"), (rx[r][1], rx[r][0]), xytext=(-3, 3), textcoords="offset points", fontsize=5.5, ha="right")''')
s=s.replace('''        axs[i, 0].text(-0.16, 0.5,''','''        axs[i, 0].text(-0.22, 0.5,''')
# traces: right margin and pressure label
s=s.replace('''fig, axs = plt.subplots(8, 1, figsize=(11, 13), sharex=True); fig.subplots_adjust(left=0.07, right=0.99, top=0.93, bottom=0.14, hspace=0.45)''',
            '''fig, axs = plt.subplots(8, 1, figsize=(11, 13), sharex=True); fig.subplots_adjust(left=0.07, right=0.93, top=0.93, bottom=0.12, hspace=0.5)''')
s=s.replace('''ax.set_ylabel("Pa ×10⁻³", fontsize=7)''','''ax.set_ylabel("Pressure (mPa)", fontsize=7)''')
s=s.replace('''ax2.set_ylabel("matched-filter\\nstatistic", fontsize=6.5, color="#c7742c")''','''ax2.set_ylabel("matched-filter\\nstatistic", fontsize=6.5, color="#c7742c", rotation=270, labelpad=18)''')
p.write_text(s)
EOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels
python run_j_levels_charts.py $OUT ../../../../../../charts_out 2>&1 | grep -v "^$" | tail -5; echo done