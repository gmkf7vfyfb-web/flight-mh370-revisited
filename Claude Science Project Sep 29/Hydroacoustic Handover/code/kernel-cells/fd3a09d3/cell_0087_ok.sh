OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid; grep paths $OUT/raw/passC.log | tail -1; ls $OUT/raw | grep -c ALLDONE; date -u
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib
p=pathlib.Path('tl_grid_table.py'); s=p.read_text()
old='''    d["source_water_depth_m"] = -el_[i_, j_].astype(float); d["ridge_source"] = d.source_water_depth_m < 2000.0
    arc = d[d.source_id.str.startswith("arc")].copy()'''
new='''    d["source_water_depth_m"] = -el_[i_, j_].astype(float); d["ridge_source"] = d.source_water_depth_m < 2000.0
    d = adiabatic_flags(d)
    arc = d[d.source_id.str.startswith("arc")].copy()'''
assert old in s; s=s.replace(old,new,1)
old='''def ram_correct_imos(g):'''
new='''def axis_depth(lat, lon):
    """WOA23 March sound-channel axis depth (minimum c between 200 and 2,500 m) at a point."""
    import tl_grid_run_j as TG
    z, p = TG.woa_profile(float(lat), float(lon)); c = p["c_mean"]
    m = (z >= 200) & (z <= 2500) & np.isfinite(c)
    return float(z[m][np.argmin(c[m])]) if m.any() else np.nan


def adiabatic_flags(d):
    """TL-recalibration track result (22 Oct, architecture message): on sill-crossing paths the adiabatic KRAKEN excess is largely
    an artefact (air7 -> H01W: adiabatic +55 dB, RAM +16 to +22 dB). Per path: axis_depth_m at the path midpoint;
    adiabatic_suspect = 1 where the minimum corridor depth anywhere on the path (receiver end included) is shallower than
    axis + 1,500 m, or any feature is shallower than 2,000 m. Because the IMS hydrophones sit on slopes (seafloor 1,570-1,590 m
    under H01W/H08S) and the IMOS loggers on the seabed, this rule flags every path; adiabatic_suspect_excl_rx applies the
    same rule to the on-track depth excluding the last 100 km (the receiver approach), which separates sill crossings from
    the terminal slope. TL on a suspect path is an UPPER BOUND on loss (adiabatic)."""
    from pyproj import Geod
    G = Geod(ellps="WGS84")
    keys = d.drop_duplicates(["source_id", "receiver"])[["source_id", "receiver", "src_lat", "src_lon", "rcv_lat", "rcv_lon"]]
    ax = {}
    for _, r in keys.iterrows():
        mid = G.npts(r.src_lon, r.src_lat, r.rcv_lon, r.rcv_lat, 1)[0]
        ax[(r.source_id, r.receiver)] = axis_depth(mid[1], mid[0])
    d = d.copy()
    d["axis_depth_m"] = [ax[(a, b)] for a, b in zip(d.source_id, d.receiver)]
    d["adiabatic_suspect"] = ((d.min_corridor_depth_m < d.axis_depth_m + 1500.0) | (d.min_corridor_depth_m < 2000.0)).astype(int)
    d["adiabatic_suspect_excl_rx"] = ((d.min_depth_excl_last100_m < d.axis_depth_m + 1500.0) | (d.min_depth_excl_last100_m < 2000.0)).astype(int)
    return d


def ram_correct_imos(g):'''
assert old in s; s=s.replace(old,new,1)
# carry flags into the two tables
s=s.replace('''                      ram_delta_available=ims.receiver.isin(["H01W", "H08S"]), source_water_depth_m=ims.source_water_depth_m,
                      ridge_source=ims.ridge_source)).to_csv(out / "ims_tl_kraken_arc.csv", index=False)''',
'''                      ram_delta_available=ims.receiver.isin(["H01W", "H08S"]), source_water_depth_m=ims.source_water_depth_m,
                      ridge_source=ims.ridge_source, axis_depth_m=ims.axis_depth_m, min_corridor_depth_m=ims.min_corridor_depth_m,
                      adiabatic_suspect=ims.adiabatic_suspect, adiabatic_suspect_excl_rx=ims.adiabatic_suspect_excl_rx)).to_csv(out / "ims_tl_kraken_arc.csv", index=False)''')
s=s.replace('''                      ramcorr_floored=im.ramcorr_floored,
                      source_water_depth_m=im.source_water_depth_m, ridge_source=im.ridge_source)).to_csv(out / "imos_tl_ramcorr_arc.csv", index=False)''',
'''                      ramcorr_floored=im.ramcorr_floored,
                      source_water_depth_m=im.source_water_depth_m, ridge_source=im.ridge_source, axis_depth_m=im.axis_depth_m,
                      min_corridor_depth_m=im.min_corridor_depth_m, adiabatic_suspect=im.adiabatic_suspect,
                      adiabatic_suspect_excl_rx=im.adiabatic_suspect_excl_rx)).to_csv(out / "imos_tl_ramcorr_arc.csv", index=False)''')
s=s.replace('''  ramcorr_extrapolated                 IMOS only:''','''  axis_depth_m, adiabatic_suspect,     see adiabatic_flags (architecture message of 22 Oct, TL-recalibration track): TL on a
  adiabatic_suspect_excl_rx            suspect path is an upper bound on loss (adiabatic).
  ramcorr_extrapolated                 IMOS only:''')
p.write_text(s)
EOF
python -c "import ast; ast.parse(open('tl_grid_table.py').read()); print('ok')"