cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n 46,60p ram_tl_check.py; sed -n 124,134p ram_tl_check.py
PYTHONPATH=. python -c "import ram_tl_check as RC; print(RC.delta_interp({5.0:1.0,10.0:2.0,20.0:3.0,40.0:4.0}, [5.0,6.3,8.0,40.0,50.0]))"