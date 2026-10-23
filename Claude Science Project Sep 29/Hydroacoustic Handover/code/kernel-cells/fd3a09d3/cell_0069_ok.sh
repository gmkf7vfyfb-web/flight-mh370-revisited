cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib
p=pathlib.Path('tl_grid_table.py'); s=p.read_text()
old='''        # FLOOR (added after the pass-A inspection, before any use): the constant delta double-counts where the raw KRAKEN
        # value is already far below the reference (ridge-top sources: 35 dB "TL" over 4,100 km at Portland). Where the
        # correction is extrapolated (|raw - ref raw| > 10 dB) the corrected value may not fall below the reference RAM
        # value scaled cylindrically in range, minus 10 dB: floor = TL_RAM_ref(band) + 10 log10(R / R_ref) - 10.
        rref = float(cmp_[cmp_.path == RAM_GROUP[lg]].range_km.iloc[0])
        floor = ram + 10 * np.log10(g.loc[m, "range_km"].values / rref) - 10.0
        ext = g.loc[m, "ramcorr_extrapolated"].values
        bite = ok & ext & (tl < floor)'''
new='''        # FLOOR (added after the pass-A inspection, before any use; ridge-source rows ONLY, so the old rule is unchanged
        # everywhere else): the constant delta double-counts where a ridge-top source already lowers the raw KRAKEN value
        # (35 dB "TL" over 4,100 km at Portland from 32.0 S). On ridge_source rows the corrected value may not fall below
        # the reference RAM value scaled cylindrically in range, minus 10 dB: floor = TL_RAM_ref(band) + 10 log10(R/R_ref) - 10.
        rref = float(cmp_[cmp_.path == RAM_GROUP[lg]].range_km.iloc[0])
        floor = ram + 10 * np.log10(g.loc[m, "range_km"].values / rref) - 10.0
        ridge = g.loc[m, "ridge_source"].values
        bite = ok & ridge & (tl < floor)'''
assert old in s; s=s.replace(old,new,1)
old='''  ramcorr_floored                      IMOS only: see ram_correct_imos; the corrected value was raised to the reference RAM
                                       value (range-scaled, -10 dB) because the constant delta would otherwise give a
                                       physically impossible loss (ridge-top sources).'''
new='''  ramcorr_floored                      IMOS only, ridge_source rows only: see ram_correct_imos; the corrected value was raised
                                       to the reference RAM value (range-scaled, -10 dB) because the constant delta would
                                       otherwise give a physically impossible loss. Elsewhere rule 2 is applied unchanged,
                                       including where it is extrapolated (flag only).'''
assert old in s; s=s.replace(old,new,1); p.write_text(s)
EOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
python tl_grid_table.py /tmp/tlg_tables_A /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passA > /dev/null
python -c "
import pandas as pd
t=pd.read_csv('/tmp/tlg_tables_A/imos_tl_ramcorr_arc.csv',dtype={'logger':str}); t=t[(t.src_depth_m==10)&(t.status=='ok')&(t.offset_nm==0)]
print(t.groupby('logger').agg(n=('tl_db','size'), extrap=('ramcorr_extrapolated','mean'), floored=('ramcorr_floored','mean')).round(3))
print(t[t.ramcorr_floored].groupby(['logger','lat']).size())"
grep paths /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passB.log | tail -1; date -u