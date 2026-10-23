date -u +%H:%M:%SZ; df -k /System/Volumes/Data | tail -1; uptime | cut -c30-
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
d=open("driver.py").read()
d=d.replace('''out = R.STATS_DIR_RAMGRID if STATS_ONLY else R.EXCHANGE_OUT; stg = out if STATS_ONLY else pathlib.Path(str(out) + ".staging"); stg.mkdir(parents=True, exist_ok=True)''',
'''out = R.STATS_DIR_RAMGRID if STATS_ONLY else pathlib.Path(os.environ.get("B11_OUT", str(R.EXCHANGE_OUT)))   # B11_OUT: product folder (A4 rewrite -> run-j-gated-v2)
stg = out if STATS_ONLY else pathlib.Path(str(out) + ".staging"); stg.mkdir(parents=True, exist_ok=True)
RAMGRID = os.environ.get("B11_IMOS_RAMGRID") == "1"''')
d=d.replace('''hdr = f"""Hydroacoustics block 11 (composition) on end of flight run J, all four strata (74 seeds). Written {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}.
Pre-registration prepare/composition_run_j/prereg.py (module branch, commit 90d7181); worker.py / driver.py; {NPROC} single-thread workers.''',
'''hdr = f"""Hydroacoustics block 11 (composition) on end of flight run J, all four strata (74 seeds). Written {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}.
{'PRODUCT v2 (amendment A4, prereg e13a32e): IMOS TL from the RAM-along-grid drop-in imos_tl_ram_arc.csv (G-TL1 closed on the offset-0 line); supersedes run-j-gated (old IMOS table).' if RAMGRID else 'IMOS TL: imos_tl_ramcorr_arc.csv (constant rule-2 correction, gap G-TL1).'}
Pre-registration prepare/composition_run_j/prereg.py (module branch, commit 90d7181{' + A4 e13a32e' if RAMGRID else ''}); worker.py / driver.py; {NPROC} single-thread workers.''')
d=d.replace('''(IMOS M1b p <= 0.05: 3275 01:20:35 and 01:07:47, both louder than any impact could be at Portland, eta_needed 30 / 19 -- matching is
amplitude-blind, gap G11-1; H01W M1b p <= 0.05: 00:52:04 text time; H08S residual: none). TL = block 2 arc grid (41-20 S, offset 0,
10 m source; IMOS RAM-corrected, G-TL1; IMS raw KRAKEN minus imp500 RAM delta).''','''(IMOS M1b p <= 0.05: 3275 01:20:35 and 01:07:47, both louder than any impact could be at Portland, eta_needed 30 / 19 -- matching is
amplitude-blind, gap G11-1; H01W M1b p <= 0.05: 00:52:04 text time; H08S residual: none). TL = block 2 arc grid (41-20 S, offset 0,
10 m source; IMOS {'RAM along the grid, imos_tl_ram_arc.csv' if RAMGRID else 'RAM-corrected, G-TL1'}; IMS raw KRAKEN minus imp500 RAM delta).''')
open("driver.py","w").write(d); import ast; ast.parse(d); print("ok")
EOF
export B11_OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated-v2 B11_IMOS_RAMGRID=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mkdir -p $B11_OUT.staging; nohup python driver.py 4 > $B11_OUT.staging/driver.out 2>&1 &
sleep 45; tail -3 $B11_OUT.staging/driver.log; tail -1 $B11_OUT.staging/_w_run-j-waypoints_1.log