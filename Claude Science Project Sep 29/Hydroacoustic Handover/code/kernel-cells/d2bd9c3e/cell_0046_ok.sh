cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
p='run_j_windows_charts.py'; s=open(p).read()
# footnotes: dynamic spacing
s=s.replace('''def footnotes(fig, plain, tech, y0=0.005):
    fig.text(0.01, y0 + 0.055, plain, fontsize=6.3, color="#333333", va="bottom", ha="left", wrap=True)
    fig.text(0.01, y0, tech, fontsize=5.8, color="#555555", va="bottom", ha="left", wrap=True)''',
'''def footnotes(fig, plain, tech, y0=0.005):
    lh = 0.105 / fig.get_size_inches()[1]          # one 5.8 pt line, as a figure fraction
    ytech = y0; yplain = y0 + lh * (tech.count("\\n") + 1) + 0.6 * lh
    fig.text(0.01, ytech, tech, fontsize=5.8, color="#555555", va="bottom", ha="left")
    fig.text(0.01, yplain, plain, fontsize=6.3, color="#333333", va="bottom", ha="left")''')
# y tick labels shorter
s=s.replace('ax.set_yticklabels(["impact time", OPT_PLAIN["D0"], OPT_PLAIN["D2"], "00:19 both BFOs as recorded", "00:19 both BFOs with start-up offset", "recordings held"])',
            'ax.set_yticklabels(["impact time", "00:19 held out", "00:19 R600 BTO + BFO", "00:19 both BFOs, as recorded", "00:19 both BFOs, start-up offset", "recordings held"])')
# coverage text above the held row
s=s.replace('''ax.text(x1 - 60, 0.0, f"{100 * float(covr[0]['held_fraction']):.0f} % of arrivals inside held records", fontsize=5.8, color="black", ha="right", va="center")''',
            '''ax.text(x1 - 60, -0.95, f"{100 * float(covr[0]['held_fraction']):.0f} % of the predicted arrival lies inside the recordings held", fontsize=5.8, color="black", ha="right", va="center")''')
# royer labels staggered
s=s.replace('''        for ev, tv in royer_times(repo_results, rx).items():
            if x0 <= tv <= x1:
                ax.plot(tv, -0.75, "^", ms=4, color="#1b7f3b", mec="black", mew=0.3, clip_on=False)
                ax.text(tv, -1.15, ev, fontsize=5.5, color="#1b7f3b", ha="center", va="top", clip_on=False)''',
'''        for j, (ev, tv) in enumerate(sorted(royer_times(repo_results, rx).items(), key=lambda kv: kv[1])):
            if x0 <= tv <= x1:
                ax.plot(tv, -0.75, "^", ms=4, color="#1b7f3b", mec="black", mew=0.3, clip_on=False)
                ax.text(tv, -1.05 - 0.45 * (j % 2), ev, fontsize=5.5, color="#1b7f3b", ha="center", va="top", clip_on=False)''')
s=s.replace('ax.set_ylim(-1.4, 6.2); ax.set_xlim(x0, x1)','ax.set_ylim(-1.9, 6.2); ax.set_xlim(x0, x1)')
# title/legend spacing in timelines
s=s.replace('fig.legend(handles=leg, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.975))\n    fig.suptitle(title, y=0.995, fontsize=9.5, ha="center")',
            'fig.legend(handles=leg, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.965))\n    fig.suptitle(title, y=0.992, fontsize=9.5, ha="center")')
s=s.replace('fig.subplots_adjust(top=0.90, bottom=0.17, left=0.15, right=0.985, hspace=0.45, wspace=0.42)',
            'fig.subplots_adjust(top=0.86 if nrow > 3 else 0.84, bottom=0.17 if nrow > 3 else 0.2, left=0.15, right=0.985, hspace=0.5, wspace=0.42)')
# request legend
s=s.replace('ax.legend(handles=leg, loc="lower right", frameon=False)','ax.legend(handles=leg, loc="upper right", frameon=False)')
s=s.replace('fig.subplots_adjust(top=0.92, bottom=0.30, left=0.2, right=0.97)','fig.subplots_adjust(top=0.92, bottom=0.33, left=0.2, right=0.97)')
# pubcov x range for (b) and bottom
s=s.replace('ax2.set_ylim(-40, -19.5); ax2.set_xlim(x0, x1)','ax2.set_ylim(-40, -19.5); ax2.set_xlim(R.T0 - 15 * 60, R.T0 + 75 * 60)')
s=s.replace('fig.subplots_adjust(top=0.9, bottom=0.30, left=0.07, right=0.98, wspace=0.25)','fig.subplots_adjust(top=0.9, bottom=0.33, left=0.07, right=0.98, wspace=0.28)')
s=s.replace('ax2.legend(handles=h, frameon=False, loc="lower right", fontsize=6.2)','ax2.legend(handles=h, frameon=False, loc="lower right", fontsize=6.0)')
open(p,'w').write(s)
EOF
export PYTHONPATH=. MPLBACKEND=Agg; OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows
python run_j_windows_charts.py $OUT ../../../../../charts_out --prereg bc99b07 --repo-results "$PWD/../../../../../../repo/Claude Science Project Sep 29/results" 2>&1 | tail -2