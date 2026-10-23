cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
s=open("charts.py").read()
s=s.replace('''    fig.suptitle("At dive probability 0.5, adding the hydroacoustic result moves the end-of-flight latitude distribution by 0.1–0.3°; the bumps near 33°S come from two time-matched Portland candidates that are too loud to be the aircraft", x=0.01, ha="left", y=0.995, fontsize=8.5)''',
'''    fig.suptitle("At dive probability 0.5, adding the hydroacoustic result moves the end-of-flight latitude distribution by 0.1–0.3°;\\nthe bumps near 33–36°S come from two time-matched Portland candidates that are too loud to be the aircraft (amplitude-blind matching)", x=0.01, ha="left", y=0.998, fontsize=8.5)''')
s=s.replace('''fig.subplots_adjust(left=0.06, right=0.99, top=0.83, bottom=0.42, wspace=0.08)
    nd =''','''fig.subplots_adjust(left=0.06, right=0.99, top=0.80, bottom=0.42, wspace=0.08)
    nd =''')
s=s.replace('''bbox_to_anchor=(0.06, 0.975), ncol=3, fontsize=6.5)''','''bbox_to_anchor=(0.06, 0.945), ncol=3, fontsize=6.5)''')
open("charts.py","w").write(s)
EOF
RES="$PWD/../../../../../../../repo/Claude Science Project Sep 29/results"; O=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated; python charts.py $O/reduce "$RES" "module commits 90d7181, dddfbd0" 2>&1 | grep -v Warn | head -1; cd - >/dev/null; rm -rf charts_test; mkdir charts_test; cp "repo/Claude Science Project Sep 29/results"/hydroacoustics-composition-run-j-evidence.png charts_test/