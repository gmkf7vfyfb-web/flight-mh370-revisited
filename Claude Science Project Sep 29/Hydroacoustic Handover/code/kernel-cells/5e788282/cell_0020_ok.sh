cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n 1,70p "$H/tl_grid_run_j.py"; grep -n "^def \|^    def " "$H/tl_grid_run_j.py" | head -40