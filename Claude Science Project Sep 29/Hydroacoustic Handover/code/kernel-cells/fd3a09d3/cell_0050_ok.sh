cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib
p = pathlib.Path('per_impact_lnl.py'); s = p.read_text()
old = '''Usage (from prepare/, PYTHONPATH=.:exploratory/pleiades_test):'''
new = '''AMENDMENT 9 (22 Oct 2026, work order 2026-10-21 block 2; committed before any run J row is scored with it). --tl-table
  arc-grid replaces the five-quantile TL latitude tables (38.46-31.64 S, clamped outside) by the whole-arc grid tables
  results-data/tl_grid_run_j/{ims_tl_kraken_arc.csv, imos_tl_ramcorr_arc.csv} (41-20 S, offset-0 arc line; tl_grid_table.py
  states the interpolation rule: linear in latitude, clamped at 41 S and 20 S, blocked bands NaN -> zero energy). The RAM
  deltas are applied exactly as before (IMS: lhyd rule from ims_ram_delta.csv; IMOS: inside the table). Default stays
  --tl-table quantile5 (no value changes to anything already written); the arc-grid tables are the drop-in for block 3,
  which closes the reach gap "TL clamped at the table edge" for rows between 41 S and 20 S. Receivers without a RAM
  delta (H08N, 3250) are in the grid tables but are not scored by this chain (unchanged).

Usage (from prepare/, PYTHONPATH=.:exploratory/pleiades_test):'''
assert old in s; s = s.replace(old, new, 1)
old2 = '''    ap.add_argument("--part")   # amendment 8(e): parallel worker tag; no README/READY
'''
new2 = '''    ap.add_argument("--part")   # amendment 8(e): parallel worker tag; no README/READY
    ap.add_argument("--tl-table", choices=["quantile5", "arc-grid"], default="quantile5")   # amendment 9
    ap.add_argument("--tl-table-dir", default=str(HERE.parent / "results-data/tl_grid_run_j"))
'''
assert old2 in s; s = s.replace(old2, new2, 1)
old3 = '''    m = Terms(a.module_dir, a.imos_events, a.kadri_csv); summ = {"options": dict(calerr=a.calerr, noise=a.noise, tau=a.tau, tau_k=a.tau_k, noise_sd=a.noise_sd)}
'''
new3 = '''    m = Terms(a.module_dir, a.imos_events, a.kadri_csv); summ = {"options": dict(calerr=a.calerr, noise=a.noise, tau=a.tau, tau_k=a.tau_k, noise_sd=a.noise_sd, tl_table=a.tl_table)}
    if a.tl_table == "arc-grid":   # amendment 9
        import tl_grid_table as TT
        summ["options"]["tl_table_dir"] = a.tl_table_dir; summ["options"]["tl_span_deg"] = TT.apply_to_model(m, a.tl_table_dir)
'''
assert old3 in s; s = s.replace(old3, new3, 1)
p.write_text(s)

p = pathlib.Path('tl_grid_table.py'); s = p.read_text()
old = '''def tl_at(xs, col, lat):'''
new = '''def apply_to_model(m, table_dir):
    """Swap the lhyd.Model / per_impact_lnl.Terms tables for the grid tables (amendment 9). IMS: RAM delta subtracted as
    lhyd.Model.__init__ does (imp500 path delta, 10 m for z < 30, log-f interpolation). Returns the latitude span."""
    F = m.F
    xs, tabs = load_table(table_dir, F.BANDS, F.SRC)
    rd = pd.read_csv(RD / "near_limits/ims_ram_delta.csv")
    m.xs = xs
    for lg in m.B.LOGGERS:
        m.tl_imos[lg] = tabs[lg]
    for stn in ("H01W", "H08S"):
        dd = rd[rd.path == f"imp500_{stn}"]; tab = {}
        for fc in F.BANDS:
            for z in F.SRC:
                zz = 30.0 if z >= 30 else 10.0; h = dd[np.isclose(dd.src_depth_m, zz)].set_index("fc_hz").delta_db
                delta = float(np.interp(np.log10(fc), np.log10(h.index.values), h.values))
                tab[(fc, z)] = tabs[stn][(fc, z)] - delta
        m.tl_ims[stn] = tab
    return [float(xs.min()), float(xs.max())]


def tl_at(xs, col, lat):'''
assert old in s; s = s.replace(old, new, 1); p.write_text(s)
EOF
python -c "import ast; [ast.parse(open(f).read()) for f in ('per_impact_lnl.py','tl_grid_table.py','tl_grid_evidence.py')]; print('ok')"