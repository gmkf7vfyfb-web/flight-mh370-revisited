cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
python - <<'EOF'
s=open("run_kadri.py").read()
s=s.replace("cal = pd.DataFrame(cal); best = cal.iloc[(cal.rate - 1.0).abs().argmin()]\n    ctx[\"sr_k\"], ctx[\"sr_sigma\"] = float(best.k), float(best.sigma)",
            "cal = pd.DataFrame(cal); srbest = cal.iloc[(cal.rate - 1.0).abs().argmin()]\n    ctx[\"sr_k\"], ctx[\"sr_sigma\"] = float(srbest.k), float(srbest.sigma)")
s=s.replace("rate=float(best.rate)), q_band", "rate=float(srbest.rate)), q_band")
open("run_kadri.py","w").write(s)
EOF
WS=$(cd ../../../../../../..; pwd); export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python run_kadri.py "$WS/out/templates/templates_raw.npz" "$WS/out/kadri" 3 2>&1 | grep -v Warning | tail -3
python run_h08s.py "$WS/out/templates/templates_raw.npz" "$WS/out/h08s" 2>&1 | grep -v Warning | tail -4