A="audit/repo/Claude Science Project Sep 29/results/hydroacoustics-audit"; cd "$A/scripts"; python3 - <<'EOF'
s=open('fig_residuals.py').read()
s=s.replace('"Deep explosive charges, 2003: station difference within 5 dB','"Deep charges, 2003: station difference within 5 dB')
s=s.replace("Below 30 Hz the charges were too weak to see.","Below 30 Hz the charges were too weak to see at both stations at once.")
open('fig_residuals.py','w').write(s)
EOF
cd - >/dev/null; python "$A/scripts/fig_residuals.py" "$A/data/air9_residuals.csv" "$A/data/sus_bands.csv" "$A/hydroacoustics-audit-calibration-checks" && echo ok; cp audit/work/sus/sus_spectra.npz "$A/data/"; for o in held-out r600-bto-only r600-bto-raw-bfo; do mkdir -p "$A/data/sensitivity/$o"; for v in audit/work/sens/out/$o/*; do vv=$(basename $v); cp $v/power_check.json "$A/data/sensitivity/$o/power_check_$vv.json"; cp audit/work/sens/rhyd/$o/$vv/rhyd_pkg.json "$A/data/sensitivity/$o/rhyd_pkg_$vv.json" 2>/dev/null; done; done; cp -r audit/work/sens/rhyd/held-out/lvl+8 /dev/null 2>&1; ls "$A/data/sensitivity/held-out" | head; du -sh "$A/data"