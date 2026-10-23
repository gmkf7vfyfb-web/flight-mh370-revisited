A="audit/repo/Claude Science Project Sep 29/results/hydroacoustics-audit"; cd "$A/scripts"; python3 - <<'EOF'
s=open('fig_residuals.py').read()
s=s.replace('a2.set_title(f"Deep explosive charges, 2003: the two stations agree ({k} shots)"','a2.set_title(f"Deep explosive charges, 2003: station difference within 5 dB ({k} shots)"')
s=s.replace("removes \"\n       \"about two thirds of this.","removes \"\n       \"about two thirds of the change with frequency, but leaves the model 2 to 5 dB too lossy.")
s=s.replace("The difference between \"\n       \"the stations agrees with the model within 3 dB above 30 Hz.","The difference between \"\n       \"the stations agrees with the model within 5 dB above 30 Hz, and its median is within 3 dB.")
open('fig_residuals.py','w').write(s)
EOF
grep -c "two thirds of the change" fig_residuals.py; grep -c "median is within 3 dB" fig_residuals.py; cd - >/dev/null; python "$A/scripts/fig_residuals.py" "$A/data/air9_residuals.csv" "$A/data/sus_bands.csv" "$A/hydroacoustics-audit-calibration-checks" && echo ok