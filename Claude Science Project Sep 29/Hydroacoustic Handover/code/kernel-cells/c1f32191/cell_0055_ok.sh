cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
w=open("worker.py").read()
w=w.replace('''    gib = free_gib(stg); write = list(R.COLUMNS) if gib >= R.DISK_FLOOR_GIB else ["hydro-lnL-imos-margeta"]''',
'''    gib = free_gib(stg); write = list(R.COLUMNS) if (gib >= R.DISK_FLOOR_GIB or os.environ.get("B11_TOPUP") == "1") else ["hydro-lnL-imos-margeta"]
    # B11_TOPUP=1: re-run of a seed that was short-written while another process held the disk below the floor (amendment A2)''')
open("worker.py","w").write(w); print("ok")
EOF