cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
python - <<'EOF'
import pathlib
p=pathlib.Path('run_j_levels_charts.py'); s=p.read_text()
s=s.replace('''        fig, ax = plt.subplots(figsize=(7.2, 5.4)); fig.subplots_adjust(left=0.1, right=0.98, top=0.9, bottom=0.3)''',
            '''        fig, ax = plt.subplots(figsize=(8.5, 7.6)); fig.subplots_adjust(left=0.09, right=0.98, top=0.92, bottom=0.37)''')
s=s.replace('''        ax.annotate("no prediction\\nbelow 5 Hz", (3.2, float(nz.p50.iloc[0])), xytext=(0, 10), textcoords="offset points", fontsize=5.8, ha="center", color="#555555")''',
            '''        ax.annotate("no prediction\\nbelow 5 Hz", (3.2, 118), fontsize=5.6, ha="center", va="top", color="#555555")''')
s=s.replace('''fig, axs = plt.subplots(2, 4, figsize=(14.5, 7.2), sharex=True, sharey=True); fig.subplots_adjust(left=0.06, right=0.9, top=0.9, bottom=0.2, wspace=0.06, hspace=0.12)''',
            '''fig, axs = plt.subplots(2, 4, figsize=(14.5, 6.4), sharex=True, sharey=True); fig.subplots_adjust(left=0.06, right=0.9, top=0.9, bottom=0.22, wspace=0.06, hspace=0.05)''')
s=s.replace('''cb.set_label("Predicted signal-to-noise ratio at the best open station (dB)")''','''cb.set_label("Predicted signal-to-noise ratio at the best open station (dB)", labelpad=48)''')
s=s.replace('''cax = fig.add_axes([0.915, 0.3, 0.012, 0.5])''','''cax = fig.add_axes([0.915, 0.32, 0.012, 0.46])''')
p.write_text(s)
EOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels
python run_j_levels_charts.py $OUT ../../../../../../charts_out 2>&1 | grep -v "^$" | tail -5; echo done