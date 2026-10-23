cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
s=open('tl_recal_block9.py').read()
old='''OUTPUTS. results-data/tl_recal_block9/:'''
new='''AMENDMENT 3 (22 Oct 2026 02:50 UTC, after the first RAM result; EXPLORATORY, labelled). RAM at 31.5 and 40 Hz on the
  geodesic cut the air7 - air9 excess from about 43-53 dB (adiabatic) to about 20 dB, so the RAM set is extended to 50
  and 63 Hz and to the +50 km path (the ridge-clearing corridor), with air9 -> H01W at the same bands as the reference.
  Reported beside the registered result; the step (d) verdict stays on the registered adiabatic set.
OUTPUTS. results-data/tl_recal_block9/:'''
assert old in s; s=s.replace(old,new,1)
old2='''def cmd_ram(sections, at, scratch, out, nproc=4):
    sec = Path(sections); out = Path(out); rd = STATIONS["H01W"][1]
    paths = {"air7off+0_H01W": sec / "builder" / "bathy_air7off+0_H01W.csv", "air7off+20_H01W": sec / "builder" / "bathy_air7off+20_H01W.csv"}
    jobs = [(tag, p, sec / "builder" / "ssp_air7_H01W.csv", fc, 10.0, rd) for tag, p in paths.items() for fc in (31.5, 40.0)]
    jobs.append(("builder_air9_H01W", sec / "builder" / "bathy_air9_H01W.csv", sec / "builder" / "ssp_air9_H01W.csv", 31.5, 10.0, rd))
    jobs.append(("builder_air9_H01W", sec / "builder" / "bathy_air9_H01W.csv", sec / "builder" / "ssp_air9_H01W.csv", 40.0, 10.0, rd))'''
new2='''def cmd_ram(sections, at, scratch, out, nproc=4, ext=False):
    sec = Path(sections); out = Path(out); rd = STATIONS["H01W"][1]
    if not ext:
        paths = {"air7off+0_H01W": sec / "builder" / "bathy_air7off+0_H01W.csv", "air7off+20_H01W": sec / "builder" / "bathy_air7off+20_H01W.csv"}
        jobs = [(tag, p, sec / "builder" / "ssp_air7_H01W.csv", fc, 10.0, rd) for tag, p in paths.items() for fc in (31.5, 40.0)]
        jobs += [("builder_air9_H01W", sec / "builder" / "bathy_air9_H01W.csv", sec / "builder" / "ssp_air9_H01W.csv", fc, 10.0, rd) for fc in (31.5, 40.0)]
    else:   # amendment 3
        paths = {"air7off+0_H01W": sec / "builder" / "bathy_air7off+0_H01W.csv", "air7off+20_H01W": sec / "builder" / "bathy_air7off+20_H01W.csv", "air7off+50_H01W": sec / "builder" / "bathy_air7off+50_H01W.csv"}
        jobs = [(tag, p, sec / "builder" / "ssp_air7_H01W.csv", fc, 10.0, rd) for tag, p in paths.items() for fc in (50.0, 63.0)]
        jobs += [("air7off+50_H01W", paths["air7off+50_H01W"], sec / "builder" / "ssp_air7_H01W.csv", fc, 10.0, rd) for fc in (31.5, 40.0)]
        jobs += [("builder_air9_H01W", sec / "builder" / "bathy_air9_H01W.csv", sec / "builder" / "ssp_air9_H01W.csv", fc, 10.0, rd) for fc in (50.0, 63.0)]'''
assert old2 in s; s=s.replace(old2,new2,1)
s=s.replace('''    R = R.merge(pd.DataFrame(krows), on=["tag", "fc_hz"]); R.to_csv(out / "air7_ram.csv", index=False); print(R.round(1).to_string(index=False))''',
'''    R = R.merge(pd.DataFrame(krows), on=["tag", "fc_hz"])
    f = out / ("air7_ram_ext.csv" if ext else "air7_ram.csv"); R.to_csv(f, index=False); print(R.round(1).to_string(index=False))''')
s=s.replace('''    elif cmd == "ram":
        cmd_ram(*sys.argv[2:6], *(sys.argv[6:7] or ["4"]))''','''    elif cmd == "ram":
        cmd_ram(*sys.argv[2:6], *(sys.argv[6:7] or ["4"]))
    elif cmd == "ram_ext":
        cmd_ram(*sys.argv[2:6], int(sys.argv[6]) if len(sys.argv) > 6 else 4, ext=True)''')
open('tl_recal_block9.py','w').write(s); import ast; ast.parse(s); print('ok')
EOF
AT=$OLDPWD/tools; W=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python tl_recal_block9.py ram_ext $W/sections $AT $W/scratch_ram ../results-data/tl_recal_block9 4 > $W/ram_ext.log 2>&1; tail -12 $W/ram_ext.log