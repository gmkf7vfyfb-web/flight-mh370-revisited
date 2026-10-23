WS=$PWD
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import re, pathlib
p = pathlib.Path('tl_grid_run_j.py'); s = p.read_text()
old = """    rprof, profiles = A.build_profiles(bathy, ssp)
    minD = float(min(p[0] for p in profiles))
"""
new = """    rprof, profiles = A.build_profiles(bathy, ssp)
    minD = float(min(p[0] for p in profiles))
    if minD < SHALLOW_M and not no_prescreen:
        # Pre-screen equivalent to the KRAKEN rule, not a new threshold: over the hard bottom (cp 1650) the first
        # Pekeris mode cuts off at D_c = c_w c_b / (4 f sqrt(c_b^2 - c_w^2)) = 22 m at 40 Hz, so a 5-km profile
        # shallower than 15 m has no propagating mode in any band <= 40 Hz and KRAKEN would stop with "No modes".
        # Validated in the timing run (arc020.0S_+0-3250: KRAKEN no_modes in all 10 bands, 7 m minimum).
        for fc in bands:
            for zs in SRC:
                rows.append(dict(base, fc_hz=fc, src_depth_m=zs, rcv_depth_m=np.nan, tl_db=np.nan, status="no_modes_shallow",
                                 n_modes_first=0, n_modes_min=0, min_profile_depth_m=minD))
        return rows, time.time() - t0, 0.0
"""
assert old in s; s = s.replace(old, new)
s = s.replace("    name, src, rcv, bands, at_bin, work, keep_paths, pathdir = job\n", "    name, src, rcv, bands, at_bin, work, keep_paths, pathdir, no_prescreen = job\n")
s = s.replace("IMOS = [\"3315\", \"3376\", \"3250\", \"3274\", \"3275\"]\n", "IMOS = [\"3315\", \"3376\", \"3250\", \"3274\", \"3275\"]\nSHALLOW_M = 15.0                    # pre-screen depth, see run_path\n")
s = s.replace("a.bands, a.at_bin, str(work), a.keep_paths, pathdir))", "a.bands, a.at_bin, str(work), a.keep_paths, pathdir, a.no_prescreen))")
s = s.replace('    ap.add_argument("--select", nargs="*", default=None, help="run only these path names (source_id-receiver)")\n',
              '    ap.add_argument("--select", nargs="*", default=None, help="run only these path names (source_id-receiver)")\n    ap.add_argument("--no-prescreen", action="store_true", help="run KRAKEN even on profiles shallower than SHALLOW_M (validation)")\n')
p.write_text(s)
EOF
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
time python tl_grid_run_j.py /tmp/tlg_val --at-bin "$WS/tools" --lat-south -20 --lat-north -20 --offsets 0 --receivers 3250 H08N --procs 2 --no-prescreen 2>&1 | tail -2
python -c "
import pandas as pd; d=pd.read_csv('/tmp/tlg_val/tl_grid.csv'); print(d[d.src_depth_m==10][['source_id','receiver','fc_hz','tl_db','status','n_modes_min','range_km','min_track_depth_m','min_profile_depth_m','km_shallower_1000','land_on_track']].round(1).to_string())"
cat /tmp/tlg_val/wall.json | grep -A3 '"arc'