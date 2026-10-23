cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
s=open("reduce.py").read()
s=s.replace('''                    # classical exclusion: weighted probability of no detection = 0.05''','''                    postN = P / P.sum(); cdfN = np.cumsum(postN); iN = int(np.searchsorted(cdfN, 0.95))
                    eta95_nd = 10 ** (LETA[iN] - 0.05 + 0.1 * (0.95 - (cdfN[iN - 1] if iN > 0 else 0.0)) / postN[iN]) if iN < NG else ETA[-1]
                    # classical exclusion: weighted probability of no detection = 0.05''')
s=s.replace('''"share": float(W), "ess": float(W * W / W2) if W2 > 0 else 0.0, "eta95_bayes_logu_1e-6_1e-2": float(eta95),''',
'''"share": float(W), "ess": float(W * W / W2) if W2 > 0 else 0.0, "eta95_bayes_nondetection_logu_1e-6_1e-2": float(eta95_nd), "eta95_bayes_full_likelihood": float(eta95), "eta95_prior_alone": float(10 ** (-6 + 0.95 * 4)),''')
open("reduce.py","w").write(s); print("ok")
EOF
S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging; tail -4 $S/driver.log; ls $S/_parts | wc -l; df -k /System/Volumes/Data | tail -1