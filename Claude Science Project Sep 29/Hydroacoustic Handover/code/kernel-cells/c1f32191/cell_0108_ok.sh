RES="repo/Claude Science Project Sep 29/results"; python - <<'EOF'
p="repo/Claude Science Project Sep 29/results/hydroacoustics-composition-run-j.md"; s=open(p).read()
s=s.replace("the corrected table lowers the predicted levels at the loggers for the southern impacts (3315 and 3275 by 5–6 dB at the median, 3274 by 2 dB, 3376 by 0.6 dB) and raises them slightly north of 31°S.",
 "the corrected table lowers the predicted levels at the loggers for the southern impacts (median over a 20,000-row sample of waypoints seed 1: 3315 −6.4 dB, 3275 −4.8 dB, 3274 −1.9 dB, 3376 −0.6 dB) and the band table shows slightly higher detectability north of 31°S.")
s=s.replace("amplitude-weighted +0.13°, non-detection only −0.02°: G11-1 remains","amplitude-weighted +0.13°, non-detection only −0.02 to −0.03°: G11-1 remains")
open(p,"w").write(s); print("ok")
EOF
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/composition_run_j"; rm -f "$H/tables.md"; ls "$H"