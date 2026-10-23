cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib
p=pathlib.Path('tl_grid_table.py'); s=p.read_text()
# 1. docstring additions
old="POINT LABELS: \"quantile\" carries the source_id"
new='''FLAGS (added after the pass-A inspection, before any table was used; raw values are never altered):
  source_water_depth_m, ridge_source   GEBCO depth at the source point; ridge_source = depth < 2000 m. At 32.0 S the arc
                                       crosses Broken Ridge (1,035 m): the adiabatic model then couples the 10 m source far
                                       more strongly into the deep channel (5-13 dB lower TL at the IMS triads, about 100 dB
                                       lower at Portland than the neighbouring rows). This is the source-end form of the
                                       declared reach gap G-N2/K5 (ridge paths; adiabatic assumption), so ridge_source rows
                                       are EXCLUDED from the drop-in interpolation (load_table ridge_policy='neighbours':
                                       the point is dropped and its neighbours interpolate across it) and from the
                                       evidence-alone summaries; they stay in the grid files, flagged.
  ramcorr_extrapolated                 IMOS only: |raw KRAKEN - raw KRAKEN of the reference path (imp500_3376 / imp500_3274)|
                                       > 10 dB in that band, i.e. the constant RAM delta of rule 2 is applied outside the
                                       range it was derived on. Reported as coverage gap G-TL1 (RAM along the grid needed).

POINT LABELS: "quantile" carries the source_id'''
assert old in s; s=s.replace(old,new,1)
# 2. build(): add source depth + ridge flag, ramcorr_extrapolated
old='''    d = load_raw(pass_dirs)
    arc = d[d.source_id.str.startswith("arc")].copy()'''
new='''    d = load_raw(pass_dirs)
    import tl_grid_run_j as TG
    m_, el_, _ = TG.gebco(); i_, j_ = TG._ij(m_, d.src_lat.values, d.src_lon.values)
    d["source_water_depth_m"] = -el_[i_, j_].astype(float); d["ridge_source"] = d.source_water_depth_m < 2000.0
    arc = d[d.source_id.str.startswith("arc")].copy()'''
assert old in s; s=s.replace(old,new,1)
old='''    pd.DataFrame(dict(station=ims.receiver, quantile=ims.source_id, fc_hz=ims.fc_hz, src_depth_m=ims.src_depth_m, range_km=ims.range_km,
                      tl_db=ims.tl_db, lat=ims.src_lat, lon=ims.src_lon, offset_nm=ims.offset_nm, status=ims.status,
                      ram_delta_available=ims.receiver.isin(["H01W", "H08S"]))).to_csv(out / "ims_tl_kraken_arc.csv", index=False)'''
new='''    pd.DataFrame(dict(station=ims.receiver, quantile=ims.source_id, fc_hz=ims.fc_hz, src_depth_m=ims.src_depth_m, range_km=ims.range_km,
                      tl_db=ims.tl_db, lat=ims.src_lat, lon=ims.src_lon, offset_nm=ims.offset_nm, status=ims.status,
                      ram_delta_available=ims.receiver.isin(["H01W", "H08S"]), source_water_depth_m=ims.source_water_depth_m,
                      ridge_source=ims.ridge_source)).to_csv(out / "ims_tl_kraken_arc.csv", index=False)'''
assert old in s; s=s.replace(old,new,1)
old='''                      min_profile_depth_m=im.min_profile_depth_m, lat=im.src_lat, lon=im.src_lon, offset_nm=im.offset_nm,
                      ram_delta_applied=im.ram_delta_applied)).to_csv(out / "imos_tl_ramcorr_arc.csv", index=False)'''
new='''                      min_profile_depth_m=im.min_profile_depth_m, lat=im.src_lat, lon=im.src_lon, offset_nm=im.offset_nm,
                      ram_delta_applied=im.ram_delta_applied, tl_db_raw_kraken=im.tl_db_raw_kraken, ramcorr_extrapolated=im.ramcorr_extrapolated,
                      source_water_depth_m=im.source_water_depth_m, ridge_source=im.ridge_source)).to_csv(out / "imos_tl_ramcorr_arc.csv", index=False)'''
assert old in s; s=s.replace(old,new,1)
old='''    g = g.copy(); g["ram_delta_applied"] = False
    lg = str(g.receiver.iloc[0])
    if lg not in RAM_GROUP:
        return g
    cmp_ = pd.read_csv(RD / "ram_check/ram_vs_kraken.csv")'''
new='''    g = g.copy(); g["ram_delta_applied"] = False; g["tl_db_raw_kraken"] = g.tl_db; g["ramcorr_extrapolated"] = False
    lg = str(g.receiver.iloc[0])
    if lg not in RAM_GROUP:
        return g
    cmp_ = pd.read_csv(RD / "ram_check/ram_vs_kraken.csv")
    ref = cmp_[(cmp_.path == RAM_GROUP[lg]) & np.isclose(cmp_.src_depth_m, 10.0)].set_index("fc_hz").tl_kraken_db
    ref_i = np.interp(np.log10(g.fc_hz.values), np.log10(ref.dropna().index.values), ref.dropna().values)
    g["ramcorr_extrapolated"] = (g.status == "ok") & (np.abs(g.tl_db.values - ref_i) > 10.0)'''
assert old in s; s=s.replace(old,new,1)
# 3. loader: ridge policy
old='''def load_table(table_dir, bands, src_depths, offset_nm=None):'''
new='''def load_table(table_dir, bands, src_depths, offset_nm=None, ridge_policy="neighbours"):'''
assert old in s; s=s.replace(old,new,1)
old='''    ims, imo = ims[ims.offset_nm == off], imo[imo.offset_nm == off]
    xs = np.array(sorted(ims.lat.unique()))'''
new='''    ims, imo = ims[ims.offset_nm == off], imo[imo.offset_nm == off]
    if ridge_policy == "neighbours":      # drop ridge-source points; np.interp over the remaining latitudes spans them
        ims, imo = ims[~ims.ridge_source], imo[~imo.ridge_source]
    xs = np.array(sorted(ims.lat.unique()))'''
assert old in s; s=s.replace(old,new,1)
s=s.replace('''  * Within a band, no interpolation across the blocked/open boundary is attempted: a NaN neighbour gives NaN.''',
'''  * Within a band, no interpolation across the blocked/open boundary is attempted: a NaN neighbour gives NaN.
  * ridge_source points (see FLAGS) are dropped before interpolation (ridge_policy='neighbours'; 'keep' retains them).''')
p.write_text(s)

# evidence: exclude ridge rows from the band summary and carry the flag
p=pathlib.Path('tl_grid_evidence.py'); s=p.read_text()
old='''            base = dict(source_id=sid, lat=lat, lon=lon, offset_nm=offn, receiver=rec, n_bands_blocked=n_block,
                        range_km=float(h.range_km.iloc[0]), status=h.status.mode().iloc[0])'''
new='''            base = dict(source_id=sid, lat=lat, lon=lon, offset_nm=offn, receiver=rec, n_bands_blocked=n_block,
                        range_km=float(h.range_km.iloc[0]), status=h.status.mode().iloc[0], ridge_source=bool(h.ridge_source.iloc[0]),
                        ramcorr_extrapolated_bands=int(h.ramcorr_extrapolated.sum()) if "ramcorr_extrapolated" in h else 0)'''
assert old in s; s=s.replace(old,new,1)
old='''    d0 = df[df.offset_nm == 0].copy(); d0["lat_band"]'''
new='''    d0 = df[(df.offset_nm == 0) & (~df.ridge_source)].copy(); d0["lat_band"]'''
assert old in s; s=s.replace(old,new,1)
s=s.replace("OUTPUTS: <out>/evidence_alone.csv (long table), detectable_by_band.csv (5-degree latitude bands x receiver x eta),",
            "OUTPUTS: <out>/evidence_alone.csv (long table; ridge_source rows flagged), detectable_by_band.csv (5-degree latitude bands x\nreceiver x eta, ridge_source points excluded as a declared reach gap, tl_grid_table.py FLAGS),")
p.write_text(s)
EOF
python -c "import ast; [ast.parse(open(f).read()) for f in ('tl_grid_table.py','tl_grid_evidence.py')]; print('ok')"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
python tl_grid_table.py /tmp/tlg_tables_A /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passA > /dev/null
python - <<'EOF'
import pandas as pd
t=pd.read_csv('/tmp/tlg_tables_A/imos_tl_ramcorr_arc.csv',dtype={'logger':str}); t=t[(t.src_depth_m==10)&(t.status=='ok')]
print(t.groupby('logger').agg(n=('tl_db','size'), extrap=('ramcorr_extrapolated','mean'), ridge=('ridge_source','mean')).round(3))
print(t[t.ramcorr_extrapolated & ~t.ridge_source].groupby(['logger','fc_hz']).lat.agg(['min','max','count']).to_string())
EOF