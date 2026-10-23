OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
cd "$P" && python - <<'EOF'
import pandas as pd, pathlib, os
d=pathlib.Path("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/paths")
tags=sorted({f.name.split("_",1)[1][:-4] for f in d.glob("bathy_*.csv")})
bad=0
for t in tags:
    ok=True
    for pre,cols in (("bathy",{"range_km","elevation_m"}),("ssp",{"node","depth_m","c_m_s"})):
        f=d/f"{pre}_{t}.csv"
        try:
            x=pd.read_csv(f); ok &= cols<=set(x.columns) and len(x)>10
        except Exception: ok=False
    ok &= (d/f"info_{t}.json").exists()
    if not ok:
        bad+=1
        for pre in ("bathy","ssp"): (d/f"{pre}_{t}.csv").unlink(missing_ok=True)
        (d/f"info_{t}.json").unlink(missing_ok=True)
print("tags",len(tags),"bad removed",bad)
# harden: write tmp then rename
p=pathlib.Path("imos_ram_grid.py"); s=p.read_text()
s=s.replace('''            bathy, ssp, info = TG.build_path(dict(lat=p.lat, lon=p.lon), rx[p.logger]); bathy.to_csv(bcsv, index=False); ssp.to_csv(scsv, index=False)
            json.dump(info, open(pdir / f"info_{p.tag}.json", "w"))''','''            bathy, ssp, info = TG.build_path(dict(lat=p.lat, lon=p.lon), rx[p.logger])
            for df, f in ((bathy, bcsv), (ssp, scsv)):
                df.to_csv(f.with_suffix(".tmp"), index=False); os.replace(f.with_suffix(".tmp"), f)
            json.dump(info, open(pdir / f"info_{p.tag}.json", "w"))''')
p.write_text(s)
EOF
python -m py_compile imos_ram_grid.py && echo ok
cd "$OLDPWD"; rm -rf $OUT/work; cp $OUT/ram_grid_rows_timing.csv $OUT/ram_grid_rows.csv
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$P" && (PYTHONPATH=. nohup python imos_ram_grid.py run $OUT --at-bin "$OLDPWD/tools" --procs 6 --deadline 2026-10-22T03:50 > $OUT/run.log 2>&1 &) ; sleep 45; grep -v Warning $OUT/run.log | tail -3; date; uptime