cp "eof/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke/tau_sidecar.py" scorer/; cat >> kh/flight_leg_worker.py <<'E'


def process_targeted(job):
    """Run J waypoints seed k with the selected parents' production children REPLACED by the targeted run's fresh children
    (targeted_build.py). Production rows keep end of flight's cells; targeted rows use the same cells with the seed normaliser
    of production (cells_t + ln W_t - ln W_prod), so the combined rows estimate exactly the quantities of the production seed."""
    k, P, K, eof_root, core_root, tgt_sd, sub_handoff, sel_json, rows_dir = job
    stratum = 'run-j-waypoints'
    sd = pathlib.Path(eof_root) / stratum / f'seed-{k}'
    cp, fp, gp = seed_cells(sd, pathlib.Path(core_root) / stratum / 'bto-bfo' / f'seed-{k}' / 'handoff-m0011' / 'handoff.npy')
    ct, ft, gt = seed_cells(pathlib.Path(tgt_sd), pathlib.Path(sub_handoff))
    sel = np.asarray(json.load(open(sel_json))['parents'], np.int64)
    Wp, Wt = gp('weight').sum(), gt('weight').sum()
    parp = gp('parent').astype(np.int64); keep = ~np.isin(parp, sel)
    c0 = float(np.log(P / K)); corr = float(np.log(Wt) - np.log(Wp))
    lm = {kk: np.r_[cp[kk][keep], ct[kk] + corr] + c0 for kk in KEYS}
    lnz_prod = {kk: lse(cp[kk] + c0) for kk in HEAD}
    del cp, ct
    f4 = np.r_[fp[keep], ft]; nt = len(ft)
    part = sel[gt('parent').astype(np.int64)]
    def g(name):
        if name == 'parent': return np.r_[parp[keep], part].astype(float)
        return np.r_[gp(name)[keep], gt(name)]
    tau_p = np.load(sd / 'tau90_v1.npz'); att = np.load(sd / 'attitude_v1.npz')
    tau_t = np.load(pathlib.Path(tgt_sd) / 'tau90_v1.npz')
    side = {c: np.r_[tau_p[c][keep], tau_t[c]] for c in ('tau90_s', 'energy_transferred_j', 'decel_g')}
    side.update({'bank_deg_att': np.r_[att['bank_deg'][keep], np.full(nt, np.nan, np.float32)],
                 'bank_source': np.r_[att['bank_source'][keep], np.full(nt, 255, np.uint8)],
                 'n_pulses': np.r_[att['n_pulses'][keep], np.zeros(nt, np.uint8)],
                 'targeted': np.r_[np.zeros(keep.sum(), bool), np.ones(nt, bool)]})
    res = analyse(lm, KEYS, HEAD, f4, g, side, pathlib.Path(rows_dir) / f'{stratum}-seed-{k}.npz')
    res.update({'stratum': stratum, 'seed': k, 'c0': c0, 'targeted': True, 'n_selected_parents': int(len(sel)), 'rows_replaced': int((~keep).sum()),
                'rows_targeted': int(nt), 'lnZ_prod': lnz_prod, 'lnZ_combined': {kk: lse(lm[kk]) for kk in HEAD}, 'W_prod': float(Wp), 'W_tgt': float(Wt),
                'W_prod_selected': float(gp('weight')[~keep].sum())})
    return res


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'targeted':
    import pickle
    k = int(sys.argv[2]); T = pathlib.Path(sys.argv[3])
    r = process_targeted((k, 0.9982, 24, '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j', '/Users/pete/Downloads/mh370-exchange/core/run-j',
                          T / f'compact-seed-{k}', T / 'RT' / 'bto-bfo' / f'seed-{1000 + k}' / 'handoff.npy',
                          T / 'RT' / 'bto-bfo' / f'seed-{1000 + k}' / 'selection.json', str(T / 'rows')))
    pickle.dump(r, open(T / f'res-seed-{k}.pkl', 'wb'))
    print('targeted seed', k, 'lnZ prod/comb D0', r['lnZ_prod'][HEAD[0]], r['lnZ_combined'][HEAD[0]], 'rows', r['rows_targeted'])
E
python3 -c "import ast;ast.parse(open('kh/flight_leg_worker.py').read());print('ok')"