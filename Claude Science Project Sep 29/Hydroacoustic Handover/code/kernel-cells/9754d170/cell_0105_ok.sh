A="audit/repo/Claude Science Project Sep 29/results/hydroacoustics-audit"; cd "$A/scripts"; python3 - <<'EOF'
s=open('charts.py').read()
s=s.replace('fig = plt.figure(figsize=(7.2, 6.4))','fig = plt.figure(figsize=(9.0, 6.6))')
s=s.replace('ax = fig.add_axes([0.09, 0.33, 0.62, 0.60])','ax = fig.add_axes([0.075, 0.34, 0.60, 0.56])')
s=s.replace('ax.text(4.35, 22, "no recorded data\\nchecks the model here", fontsize=6.5, color=GREY, va="bottom")',
            'ax.text(4.35, 123, "no recorded data checks\\nthe model in this range", fontsize=6.5, color=GREY, va="top")')
s=s.replace('ax.set_ylim(10, 125)','ax.set_ylim(10, 126)')
s=s.replace('bbox_to_anchor=(0.725, 0.93)','bbox_to_anchor=(0.685, 0.90), labelspacing=0.6, handlelength=2.2')
s=s.replace('textwrap.fill(ste, 170)','textwrap.fill(ste, 205)').replace('textwrap.fill(tech, 200)','textwrap.fill(tech, 245)')
s=s.replace('fig.text(0.01, 0.235,','fig.text(0.01, 0.24,').replace('fig.text(0.01, 0.135,','fig.text(0.01, 0.145,')
open('charts.py','w').write(s)
EOF
cd -; M="audit/hb/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; python "$A/scripts/charts.py" "$M" "$A/data/markers_audit.json" "$A" 2>&1 | tail -3