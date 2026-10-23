cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python -c "import fitz; print(fitz.__doc__)" 2>&1 | head -2
head -60 "$H/prepare/digitise_kadri_2024_s1.py"; grep -n "import" "$H/prepare/digitise_brown_2026.py" | head; ls "$H/results-data/digitised/" | head -30; head -5 "$H/results-data/digitised/MANIFEST.csv"; wc -l "$H/results-data/digitised/MANIFEST.csv"