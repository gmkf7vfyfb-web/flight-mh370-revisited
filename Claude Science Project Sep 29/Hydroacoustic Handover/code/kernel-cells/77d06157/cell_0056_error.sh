cd gfx && python - <<'E'
s=open('charts_levels.py').read()
s=s.replace('POST_ESS = {"D0": 110383, "D2": 6431, "D3": 403, "D4": 2031}   # geometry/lags.csv (run J mixture, p = 0.5)','POST_ESS = {"D0": 1336700, "D2": 107226, "D3": 5671, "D4": 25414}   # run-j-windows/ess.json, Kish ESS of the full run J mixture at p = 0.5')
s=s.replace("Posterior ESS of the run J mixture (geometry/lags.csv): D0′ 110 k, D2 6.4 k, D3 403, D4 2.0 k (D3 below 1,000: \"\n            f\"read as provisional); subsample Kish ESS 1.80–1.93 M.","Posterior ESS = Kish ESS of the full run J mixture at p = 0.5 (run-j-windows/ess.json): D0′ 1.34 M, D2 107 k, D3 5.7 k, D4 25 k; \"\n            f\"Kish ESS of the 2 M-draw subsample 1.80–1.93 M.")
s=s.replace("(posterior ESS of the underlying run J \"\n         f\"mixture for D0′ 110 k, geometry/lags.csv)","(Kish ESS of the full run J \"\n         f\"mixture for D0′ at p = 0.5: 1.34 M, run-j-windows/ess.json)")
open('charts_levels.py','w').write(s)
E
grep -n "lags.csv\|110 k" charts_levels.py