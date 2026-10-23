cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
python - <<'EOF'
import re,pathlib
p=pathlib.Path('run_j_levels.py'); s=p.read_text()
s=s.replace('''def band_fraction_table():
    import imos_stageB_map as B
    import lhyd_tau_grid as _  # noqa  (placeholder import guard; see below)


''','')
s=s.replace('rng = np.random.default_rng([20261022, 3, 7, abs(hash(key)) % 1000])','rng = np.random.default_rng([20261022, 3, 7, KEYS.index(key)])')
s=s.replace('np.trapz(','np.trapezoid(')
s=s.replace('''                nz_k = 10 * np.log10(sum(10 ** ((nz[rec] - 10 * np.log10(len(BANDS))) / 10) * kw[fc] for fc in BANDS))   # noise after chain, flat-per-band approximation''',
'''                nz_k = nz[rec] + noise_chain_shift(rec, kw)   # noise after the chain: Blackman per-band shape, scaled to the 5-40 Hz median''')
s=s.replace('''def levels_eta1(''','''def noise_chain_shift(rec, kw):
    """10 log10 of the share of the station's 5-40 Hz noise energy that passes the Kadri chain (Blackman per-band medians x width)."""
    bs = json.loads((RD / "blackman_noise/blackman_noise_summary.json").read_text())["stations"][rec]["psd_R_band_db"]
    e = {fc: 10 ** (bs[str(fc).rstrip("0").rstrip(".") if str(fc).endswith(".0") else str(fc)]["median"] / 10) * fc * (2 ** (1 / 6) - 2 ** (-1 / 6)) for fc in BANDS}
    return float(10 * np.log10(sum(e[fc] * kw[fc] for fc in BANDS) / sum(e.values())))


def levels_eta1(''')
s=s.replace('''            for fp in files:
                assert "/S/" not in str(fp)''','''            s_files = {str(P.IMOS / f) for f in recs[(recs.logger == int(cid)) & (recs.role == "S")].file}
            for fp in files:
                assert str(fp) not in s_files, "role S recording must never be opened"''')
p.write_text(s)
EOF
python -c "
import json;bs=json.load(open('../results-data/blackman_noise/blackman_noise_summary.json'))['stations']['H01W']['psd_R_band_db'];print(list(bs.keys()))"
python -c "import ast,sys;ast.parse(open('run_j_levels.py').read());print('syntax ok')"
python -c "import numpy;print(numpy.__version__)"