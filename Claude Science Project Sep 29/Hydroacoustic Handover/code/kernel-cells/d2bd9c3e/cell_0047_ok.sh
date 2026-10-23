cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
p='run_j_windows_charts.py'; s=open(p).read()
s=s.replace('''    leg = [Patch(color="#1f4e9c", label="deep sound channel, dive probability 0.5"), Patch(color="#c7761a", label="acoustic-gravity wave branch (speed assumed), dive probability 0.5"),
           Line2D([], [], marker="|", color="black", ls="", label="window ends at dive probability 0 and 1")]''',
'''    leg = [Patch(color="#1f4e9c", label="deep sound channel"), Patch(color="#c7761a", label="acoustic-gravity wave branch (speed assumed)"),
           Line2D([], [], marker="|", color="black", ls="", label="window ends at dive probability 0 and 1")]''')
s=s.replace('ax.set_title("Data request windows per receiver: union over the 00:19 options with ESS >= 1,000, padded -10 / +20 min", loc="left")',
            'ax.set_title("Data request windows per receiver (dive probability 0.5): union over the 00:19 options with ESS >= 1,000, padded -10 / +20 min", loc="left")')
s=s.replace('ax2.legend(handles=h, frameon=False, loc="lower right", fontsize=6.0)','ax2.legend(handles=h, frameon=False, loc="upper right", fontsize=6.0)')
open(p,'w').write(s)
EOF
export PYTHONPATH=. MPLBACKEND=Agg; OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows
python run_j_windows_charts.py $OUT ../../../../../charts_out --prereg bc99b07 --repo-results "$PWD/../../../../../../repo/Claude Science Project Sep 29/results" 2>&1 | tail -1
# copy charts and tables into the work-branch results dir and module results-data
cp ../../../../../charts_out/hydroacoustics-run-j-*.p?? "../../../../../../repo/Claude Science Project Sep 29/results/"
ls ../results-data/windows_run_j/; du -sh $OUT