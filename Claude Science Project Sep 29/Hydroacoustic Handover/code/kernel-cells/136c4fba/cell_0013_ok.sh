cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
wc -l h08s_shot_template.py h08s_shot_outliers.py kadri_trace_pairs.py shared_paths.py
echo "=== shared_paths ==="; cat shared_paths.py
echo "=== template head 120 ==="; sed -n 1,120p h08s_shot_template.py