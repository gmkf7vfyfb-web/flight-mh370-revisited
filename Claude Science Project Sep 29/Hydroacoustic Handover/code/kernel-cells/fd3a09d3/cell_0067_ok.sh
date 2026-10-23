cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib
p=pathlib.Path('tl_grid_table.py'); s=p.read_text()
old='''        ok = (g.loc[m, "status"] == "ok").values; nm = (g.loc[m, "status"] == "no_modes").values
        tl = g.loc[m, "tl_db"].values.astype(float)
        tl[ok] = tl[ok] - delta[ok]
        tl[nm] = ram[nm]
        g.loc[m, "tl_db"] = tl; g.loc[m, "ram_delta_applied"] = True'''
new='''        ok = (g.loc[m, "status"] == "ok").values; nm = (g.loc[m, "status"] == "no_modes").values
        tl = g.loc[m, "tl_db"].values.astype(float)
        tl[ok] = tl[ok] - delta[ok]
        tl[nm] = ram[nm]
        # FLOOR (added after the pass-A inspection, before any use): the constant delta double-counts where the raw KRAKEN
        # value is already far below the reference (ridge-top sources: 35 dB "TL" over 4,100 km at Portland). Where the
        # correction is extrapolated (|raw - ref raw| > 10 dB) the corrected value may not fall below the reference RAM
        # value scaled cylindrically in range, minus 10 dB: floor = TL_RAM_ref(band) + 10 log10(R / R_ref) - 10.
        rref = float(cmp_[cmp_.path == RAM_GROUP[lg]].range_km.iloc[0])
        floor = ram + 10 * np.log10(g.loc[m, "range_km"].values / rref) - 10.0
        ext = g.loc[m, "ramcorr_extrapolated"].values
        bite = ok & ext & (tl < floor)
        tl[bite] = floor[bite]
        g.loc[m, "tl_db"] = tl; g.loc[m, "ram_delta_applied"] = True
        g.loc[g.index[m][bite], "ramcorr_floored"] = True'''
assert old in s; s=s.replace(old,new,1)
old='''    g = g.copy(); g["ram_delta_applied"] = False; g["tl_db_raw_kraken"] = g.tl_db; g["ramcorr_extrapolated"] = False'''
new='''    g = g.copy(); g["ram_delta_applied"] = False; g["tl_db_raw_kraken"] = g.tl_db; g["ramcorr_extrapolated"] = False; g["ramcorr_floored"] = False'''
assert old in s; s=s.replace(old,new,1)
s=s.replace('''                      ram_delta_applied=im.ram_delta_applied, tl_db_raw_kraken=im.tl_db_raw_kraken, ramcorr_extrapolated=im.ramcorr_extrapolated,''',
'''                      ram_delta_applied=im.ram_delta_applied, tl_db_raw_kraken=im.tl_db_raw_kraken, ramcorr_extrapolated=im.ramcorr_extrapolated,
                      ramcorr_floored=im.ramcorr_floored,''')
# docstring: ridge policy & floor
old='''                                       declared reach gap G-N2/K5 (ridge paths; adiabatic assumption), so ridge_source rows
                                       are EXCLUDED from the drop-in interpolation (load_table ridge_policy='neighbours':
                                       the point is dropped and its neighbours interpolate across it) and from the
                                       evidence-alone summaries; they stay in the grid files, flagged.'''
new='''                                       declared reach gap G-N2/K5 (ridge paths; adiabatic assumption). The effect is graded
                                       (2,200-2,500 m sources at 29.5-29.0 S and 22.0 S give 10-13 dB lower TL than their
                                       neighbours), and down-slope conversion of near-surface sound into the channel is a
                                       real mechanism, so the rows are KEPT in the drop-in table (ridge_policy='keep' default;
                                       'neighbours' drops flagged points and interpolates across them) and flagged; the
                                       evidence-alone band summaries are reported with and without them.
  ramcorr_floored                      IMOS only: see ram_correct_imos; the corrected value was raised to the reference RAM
                                       value (range-scaled, -10 dB) because the constant delta would otherwise give a
                                       physically impossible loss (ridge-top sources).'''
assert old in s; s=s.replace(old,new,1)
s=s.replace('def load_table(table_dir, bands, src_depths, offset_nm=None, ridge_policy="neighbours"):','def load_table(table_dir, bands, src_depths, offset_nm=None, ridge_policy="keep"):')
s=s.replace("  * ridge_source points (see FLAGS) are dropped before interpolation (ridge_policy='neighbours'; 'keep' retains them).",
            "  * ridge_source points (see FLAGS) are kept (ridge_policy='keep'); 'neighbours' drops them before interpolation.")
p.write_text(s)
p=pathlib.Path('tl_grid_evidence.py'); s=p.read_text()
old='''    d0 = df[(df.offset_nm == 0) & (~df.ridge_source)].copy(); d0["lat_band"] = pd.cut(d0.lat, [-41.01, -35, -30, -25, -20], labels=["41-35 S", "35-30 S", "30-25 S", "25-20 S"])
    tb = d0.groupby(["receiver", "eta", "lat_band"], observed=True)[["frac_pd", "frac_above_noise_median", "frac_above_noise_hi"]].mean().reset_index()
    tb.to_csv(out / "detectable_by_band.csv", index=False)'''
new='''    d0 = df[df.offset_nm == 0].copy(); d0["lat_band"] = pd.cut(d0.lat, [-41.01, -35, -30, -25, -20], labels=["41-35 S", "35-30 S", "30-25 S", "25-20 S"])
    tb = d0[~d0.ridge_source].groupby(["receiver", "eta", "lat_band"], observed=True)[["frac_pd", "frac_above_noise_median", "frac_above_noise_hi"]].mean().reset_index()
    tb["ridge_points"] = "excluded"
    tb2 = d0.groupby(["receiver", "eta", "lat_band"], observed=True)[["frac_pd", "frac_above_noise_median", "frac_above_noise_hi"]].mean().reset_index(); tb2["ridge_points"] = "included"
    pd.concat([tb, tb2]).to_csv(out / "detectable_by_band.csv", index=False)'''
assert old in s; s=s.replace(old,new,1); p.write_text(s)
EOF
python -c "import ast; [ast.parse(open(f).read()) for f in ('tl_grid_table.py','tl_grid_evidence.py')]; print('ok')"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
python tl_grid_table.py /tmp/tlg_tables_A /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passA > /dev/null
python - <<'EOF'
import pandas as pd
t=pd.read_csv('/tmp/tlg_tables_A/imos_tl_ramcorr_arc.csv',dtype={'logger':str}); t=t[(t.src_depth_m==10)&(t.status=='ok')&(t.offset_nm==0)]
print(t.groupby('logger').agg(n=('tl_db','size'), extrap=('ramcorr_extrapolated','mean'), floored=('ramcorr_floored','mean')).round(3))
print(t[t.ramcorr_floored][['logger','lat','fc_hz','tl_db_raw_kraken','tl_db']].round(1).to_string(index=False))
EOF