cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
s=open("charts.py").read()
s=s.replace('''    fig.suptitle("Adding the hydroacoustic result to the end-of-flight posterior moves the latitude distribution by a fraction of a degree", x=0.01, ha="left", y=0.995, fontsize=9)''',
'''    fig.suptitle("At dive probability 0.5, adding the hydroacoustic result moves the end-of-flight latitude distribution by 0.1–0.3°; the bumps near 33°S come from two time-matched Portland candidates that are too loud to be the aircraft", x=0.01, ha="left", y=0.995, fontsize=8.5)''')
open("charts.py","w").write(s)
EOF
O=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated; RES="repo/Claude Science Project Sep 29/results"; python charts.py $O/reduce "$RES" "module commits 90d7181, dddfbd0" 2>&1 | grep -v Warn; rm -rf charts_test; mkdir charts_test; cp "$RES"/hydroacoustics-composition-run-j-*.png charts_test/; ls charts_test