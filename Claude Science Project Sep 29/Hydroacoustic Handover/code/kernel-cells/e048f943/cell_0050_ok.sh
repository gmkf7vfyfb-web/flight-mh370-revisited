cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels
python -c "
import pandas as pd; c=pd.read_csv('tables/coverage.csv'); print(c[['key','lat_q01','lat_q99','E_q05_gj','E_q50_gj','E_q95_gj','n_supplement']].round(3).to_string(index=False))"
cat > README.md <<'EOF'
run-j-levels — hydroacoustics block 3 (level half) + block 6 charts on end of flight run J. Hydroacoustic Module (levels track), 22 Oct 2026.
Pre-registration: prepare/run_j_levels.py (hypothesis/hydroacoustics commit 4277320, before any draw). Note: results/hydroacoustics-run-j-levels.md (claude-science-sep29).
PREDICTIVE, NOT CALIBRATED; caveats C1 and C2 on every number. Likelihood 0.0 everywhere; nothing here is a detection.
draws/<stratum>/seed-k.npz   per key (option/p) 2 M-draw weighted subsample fields (idx, lat, lon, t, E, tau90, bank_deg, arc_nm, bank_source, family4, pushover_to_surface); meta = per-key weight sums
draws/supplement.npz         the same for the northern supplement (technique >= 1); E = 1/2 m v^2 (amendment 1), tau90 absent (G-L2)
levels/<option>_p<p>.npz     per receiver: weighted SNR histogram at eta = 1 (0.1 dB bins, grid -200..100 dB), blocked_mass, tau_k / tau_scenario / kadri_chain variants; map/* best-receiver samples (150k)
tables/*.csv                 detectable.csv (quantiles + shares per receiver x key x eta), band_levels_eta1.csv, eta_50.csv, power_screen.csv, best_receiver.csv, coverage.csv, sensitivities.csv, illustrative_traces.csv, math_check.json
noise/                       imos_thirdoctave_percentiles.csv (1 s band SPL percentiles, 8 Mar role-B set and 14-day background set), files_used.csv
run.json                     constants, noise medians, Kadri chain weights, per-key ESS
Inputs: run J impacts32 (74 seeds; SHA256 per seed in each draw file's meta), run-j-supplement/reduced/impacts-ruleB.npz, TL grid results-data/tl_grid_run_j, module noise summaries.
EOF
find . -type f ! -name SHA256SUMS ! -path "./logs/*" -exec shasum -a 256 {} \; | sed 's# \./#  #' > SHA256SUMS; wc -l SHA256SUMS; du -sh .