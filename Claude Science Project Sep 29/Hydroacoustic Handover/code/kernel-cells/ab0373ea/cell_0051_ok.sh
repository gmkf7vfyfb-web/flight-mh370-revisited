P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
cd "$P" && python - <<'EOF'
import pathlib
p=pathlib.Path("imos_ram_grid_charts.py"); s=p.read_text()
s=s.replace('''                ax.plot(-g.lat, g.tl_db, ls, color=COL[fc],''','''                ax.plot(-g.lat, np.minimum(g.tl_db, CLIP_DB), ls, color=COL[fc],''')
s=s.replace('BANDS = [10.0, 20.0, 40.0]','BANDS = [10.0, 20.0, 40.0]\nCLIP_DB = 230.0   # values above (blocked paths, 250-630 dB) are drawn at the top edge')
s=s.replace('''        if len(nc): ax.scatter(-nc.lat, nc.tl_db, marker="x"''','''        if len(nc): ax.scatter(-nc.lat, np.minimum(nc.tl_db, CLIP_DB), marker="x"''')
s=s.replace('''        ax.set_title(NAMES[lg], loc="left"); ax.invert_xaxis(); ax.set_xlim(41.5, 19.5); ax.grid(alpha=0.25)
        if j == 0: ax.set_ylabel("Transmission loss, 10 m source (dB)")
        ax.set_xlabel("Latitude of the impact on the 7th arc (°S)")
        ax.margins(y=0.05)''','''        ax.set_title(NAMES[lg], loc="left"); ax.set_xlim(41.5, 19.5); ax.set_ylim(105, CLIP_DB + 8); ax.grid(alpha=0.25)
        ax.axhline(CLIP_DB, color="0.6", lw=0.6, ls=":"); 
        if j == 0: ax.set_ylabel("Transmission loss, 10 m source (dB)"); ax.text(41, CLIP_DB + 1.5, "above the line: path blocked (values up to 630 dB drawn at the edge)", fontsize=5.8, color="0.4", va="bottom")
        if j == 2: ax.set_xlabel("Latitude of the impact on the 7th arc (°S)")''')
s=s.replace('''fig.legend(h, l, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.955))''','''fig.legend(h, l, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.965))''')
s=s.replace('''fig.suptitle("Transmission loss to the five Australian seabed recorders, recomputed path by path with a coupled-mode model, and the resulting share of detectable impacts", x=0.01, ha="left", y=0.995, fontsize=9.5)''',
 '''fig.suptitle("Transmission loss to the five Australian seabed recorders, recomputed path by path with a coupled-mode model, and the resulting share of detectable impacts", x=0.01, ha="left", y=0.998, fontsize=9.5)''')
s=s.replace('''    fig.text(0.01, 0.075, textwrap.fill(fn1, 230), fontsize=6.2, va="top"); fig.text(0.01, 0.028, textwrap.fill(fn2, 230), fontsize=6.2, va="top")
    fig.subplots_adjust(left=0.05, right=0.99, top=0.9, bottom=0.14)''','''    fig.text(0.01, 0.118, textwrap.fill(fn1, 235), fontsize=6.2, va="top"); fig.text(0.01, 0.058, textwrap.fill(fn2, 235), fontsize=6.2, va="top")
    fig.subplots_adjust(left=0.05, right=0.99, top=0.89, bottom=0.2)''')
s=s.replace('figsize=(13.5, 6.8)','figsize=(13.5, 7.6)')
p.write_text(s)
EOF
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
PYTHONPATH=. python imos_ram_grid_charts.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables /tmp/interim/tables /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/tables/detectable.csv $OUT/levels-rerun/tables/detectable.csv /tmp/interim/chart_test.png --commit 4920cc2 2>&1 | grep -v Warning | tail -1; cp /tmp/interim/chart_test.png "$OLDPWD/chart_test2.png"