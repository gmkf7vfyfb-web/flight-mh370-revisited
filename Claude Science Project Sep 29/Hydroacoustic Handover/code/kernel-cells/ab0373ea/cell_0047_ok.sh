P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
cd "$P" && python - <<'EOF'
import pathlib
p=pathlib.Path("imos_ram_grid.py"); s=p.read_text()
old_block='''                if np.isfinite(d0) and np.isfinite(d1): dlt = (1 - w) * d0 + w * d1; ram = (1 - w) * r0 + w * r1; mode = "interp"; used = f"{l0:g} {l1:g}"
                else:'''
new_block='''                if np.isfinite(d0) and np.isfinite(d1) and abs(d0 - d1) > JUMP_DB:
                    # AMENDMENT 1 (after the interim build, 22 Oct 01:50 local; disclosed in the note): across an open/blocked node pair the
                    # linear Delta gave physically impossible values (3275 at 29.5 S, 10 Hz: 83 dB over 4,000 km). Where the two node
                    # Deltas differ by more than JUMP_DB, take the Delta of the node whose RAW adiabatic KRAKEN value (same band) is the
                    # closer to this row's own raw value: Delta estimates the adiabatic error, so the node whose adiabatic solution
                    # resembles this row's is the better donor. A node with no raw value (no_modes) cannot be the donor unless both lack one.
                    k0, k1 = rawk.get((r.logger, r.offset_nm, l0, r.fc_hz), np.nan), rawk.get((r.logger, r.offset_nm, l1, r.fc_hz), np.nan)
                    s0, s1 = abs(k0 - r.tl_db_raw_kraken) if np.isfinite(k0) else np.inf, abs(k1 - r.tl_db_raw_kraken) if np.isfinite(k1) else np.inf
                    k = l0 if (s0 <= s1 if np.isfinite(min(s0, s1)) else w <= 0.5) else l1
                    dlt = -band_vals(k, "ram_minus_kraken_db"); ram = band_vals(k, "tl_ram_db"); mode = "jump_similar"; used = f"{k:g}"; jump = abs(d0 - d1)
                elif np.isfinite(d0) and np.isfinite(d1): dlt = (1 - w) * d0 + w * d1; ram = (1 - w) * r0 + w * r1; mode = "interp"; used = f"{l0:g} {l1:g}"; jump = abs(d0 - d1)
                else:'''
assert old_block in s; s=s.replace(old_block,new_block)
s=s.replace('''    for i, r in old.iterrows():
        if r.status in SKIP_STATUS or r.status == "zero_field": continue''','''    rawk = {(r.logger, r.offset_nm, r.lat, r.fc_hz): r.tl_db_raw_kraken for r in old[np.isclose(old.src_depth_m, 10.0)].itertuples()}
    new["delta_jump_db"] = np.nan
    for i, r in old.iterrows():
        jump = np.nan
        if r.status in SKIP_STATUS or r.status == "zero_field": continue''')
s=s.replace('''        new.at[i, "band_extrapolated"] = bool(r.fc_hz < min(bands) - 1e-9 or r.fc_hz > max(bands) + 1e-9)''','''        new.at[i, "band_extrapolated"] = bool(r.fc_hz < min(bands) - 1e-9 or r.fc_hz > max(bands) + 1e-9); new.at[i, "delta_jump_db"] = jump''')
s=s.replace('SKIP_STATUS = {"land", "no_modes_shallow"}','SKIP_STATUS = {"land", "no_modes_shallow"}\nJUMP_DB = 20.0   # amendment 1, see build()')
# physical floor diagnostic
s=s.replace('''    new.to_csv(odir / "imos_tl_ram_arc.csv", index=False)''','''    new["below_physical_floor"] = new.ram_grid_covered & (new.tl_db < 60.0 + 10 * np.log10(new.range_km))   # spherical to 1 km + cylindrical: a sanity flag, reported
    new.to_csv(odir / "imos_tl_ram_arc.csv", index=False)
    print("rows below the physical floor:", int(new.below_physical_floor.sum()), "| jump_similar rows:", int((new.ram_grid_mode == "jump_similar").sum()))''')
p.write_text(s)
EOF
python -m py_compile imos_ram_grid.py && PYTHONPATH=. python imos_ram_grid.py build /tmp/interim /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables /tmp/interim/tables 2>&1 | grep -v Warning | head -8
python - <<'EOF'
import pandas as pd, numpy as np
new=pd.read_csv("/tmp/interim/tables/imos_tl_ram_arc.csv",dtype={"logger":str})
print(new[(new.offset_nm==0)&np.isclose(new.src_depth_m,10)&(new.logger=="3275")&(new.lat.isin([-30,-29.5,-29]))&(new.fc_hz.isin([5,10,20,40]))][["lat","fc_hz","tl_db","tl_db_raw_kraken","ram_grid_mode","delta_jump_db","status"]].round(1).to_string(index=False))
print(new[new.ram_grid_mode=="jump_similar"].groupby("logger").size().to_dict(), new[new.below_physical_floor].groupby("logger").size().to_dict())
EOF