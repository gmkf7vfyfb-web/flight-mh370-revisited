P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
cd "$P" && python - <<'EOF'
import pathlib
p=pathlib.Path("imos_ram_grid.py"); s=p.read_text()
s=s.replace('JUMP_DB = 20.0   # amendment 1, see build()','JUMP_DB = 20.0   # amendment 1, see build()\nCORE_BANDS = [10.0, 20.0, 40.0]   # follow-up 22 Oct: a node counts when the core bands are done; 5 and 8 Hz are used where present')
s=s.replace('''        if set(g.fc_hz.round(3)) != set(np.round(bands, 3)): continue   # a node counts only with every band done (partial nodes = not covered)''',
            '''        if not set(np.round(CORE_BANDS, 3)) <= set(g.fc_hz.round(3)): continue   # a node counts with the core bands done (partial nodes = not covered); 5/8 Hz extend it where run''')
s=s.replace('''        def band_vals(lat_node, col):
            g = nd[lat_node]; return _interp_logf(np.array(bands), g[col].reindex(bands).values, [r.fc_hz])[0]''','''        def band_vals(lat_node, col):
            g = nd[lat_node]; return _interp_logf(np.array(bands), g[col].reindex(bands).values, [r.fc_hz])[0]
        def lo_band(*lat_nodes): return min(float(nd[k].index.min()) for k in lat_nodes)''')
# track used nodes' lowest band
s=s.replace('''dlt = -band_vals(l0, "ram_minus_kraken_db"); ram = band_vals(l0, "tl_ram_db"); mode = "node"; used = f"{l0:g}"''','''dlt = -band_vals(l0, "ram_minus_kraken_db"); ram = band_vals(l0, "tl_ram_db"); mode = "node"; used = f"{l0:g}"; lob = lo_band(l0)''')
s=s.replace('''dlt = -band_vals(k, "ram_minus_kraken_db"); ram = band_vals(k, "tl_ram_db"); mode = "jump_similar"; used = f"{k:g}"; jump = abs(d0 - d1)''','''dlt = -band_vals(k, "ram_minus_kraken_db"); ram = band_vals(k, "tl_ram_db"); mode = "jump_similar"; used = f"{k:g}"; jump = abs(d0 - d1); lob = lo_band(k)''')
s=s.replace('''dlt = (1 - w) * d0 + w * d1; ram = (1 - w) * r0 + w * r1; mode = "interp"; used = f"{l0:g} {l1:g}"; jump = abs(d0 - d1)''','''dlt = (1 - w) * d0 + w * d1; ram = (1 - w) * r0 + w * r1; mode = "interp"; used = f"{l0:g} {l1:g}"; jump = abs(d0 - d1); lob = lo_band(l0, l1)''')
s=s.replace('''                    k = l0 if np.isfinite(d0) else l1; dlt = -band_vals(k, "ram_minus_kraken_db"); ram = band_vals(k, "tl_ram_db"); mode = "nearest"; used = f"{k:g}"''','''                    k = l0 if np.isfinite(d0) else l1; dlt = -band_vals(k, "ram_minus_kraken_db"); ram = band_vals(k, "tl_ram_db"); mode = "nearest"; used = f"{k:g}"; lob = lo_band(k)''')
s=s.replace('''            k = near[np.argmin(np.abs(near - r.lat))]; dlt = -band_vals(k, "ram_minus_kraken_db"); ram = band_vals(k, "tl_ram_db"); mode = "nearest"; used = f"{k:g}"''','''            k = near[np.argmin(np.abs(near - r.lat))]; dlt = -band_vals(k, "ram_minus_kraken_db"); ram = band_vals(k, "tl_ram_db"); mode = "nearest"; used = f"{k:g}"; lob = lo_band(k)''')
s=s.replace('''new.at[i, "band_extrapolated"] = bool(r.fc_hz < min(bands) - 1e-9 or r.fc_hz > max(bands) + 1e-9); new.at[i, "delta_jump_db"] = jump''','''new.at[i, "band_extrapolated"] = bool(r.fc_hz < lob - 1e-9 or r.fc_hz > max(bands) + 1e-9); new.at[i, "delta_jump_db"] = jump''')
# coverage mask: complete = core bands done; record bands_done
s=s.replace('''np.where(cov.bands_done == " ".join(f"{b:g}" for b in bands), "complete",''','''np.where([set(f"{b:g}" for b in CORE_BANDS) <= set(str(x).split()) for x in cov.bands_done], "complete",''')
assert s.count("lob = lo_band")==5
p.write_text(s)
EOF
python -m py_compile imos_ram_grid.py && echo compiled
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
(PYTHONPATH=. nohup python imos_ram_grid.py run $OUT --at-bin "$OLDPWD/tools" --procs 6 --bands 5 8 --offsets 0 --deadline 2026-10-22T06:30 > $OUT/run3_lowband.log 2>&1 &)
sleep 90; grep -v Warning $OUT/run3_lowband.log | tail -3