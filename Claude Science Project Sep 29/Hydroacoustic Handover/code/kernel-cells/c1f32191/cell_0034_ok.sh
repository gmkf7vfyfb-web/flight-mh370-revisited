S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging; tail -3 $S/driver.log; ls $S/_parts | wc -l; df -k /System/Volumes/Data | tail -1
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
s=open("reduce.py").read()
s=s.replace('''                            nd_imos=band_sum(mx[f"wPnd_{ALPHA_TAGS[a]}"][j], -41, -20)[:NG].mean() / Z if False else (mx[f"wPnd_{ALPHA_TAGS[a]}"][j].sum(0)[:NG].mean() / Z)) for a in R.ALPHAS}''',
'''                            nd_imos=mx[f"wPnd_{ALPHA_TAGS[a]}"][j].sum(0)[:NG].mean() / Z) for a in R.ALPHAS}''')
open("reduce.py","w").write(s)
EOF
mkdir -p /tmp/b11test && OMP_NUM_THREADS=1 timeout 600 python reduce.py $S /tmp/b11test 2>&1 | grep -v Warn | tail -30