cd kh && cp "../eof/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke/joined_v2.py" ../scorer/ && python3 - <<'E'
s=open('flight_leg_worker.py').read()
a=s.index('def process(job):')
body=s[a:]
new_proc='''def process(job):
    stratum, seed, P, K, eof_root, core_root, rows_dir = job
    sd = pathlib.Path(eof_root) / stratum / f'seed-{seed}'
    cells, f4, g = seed_cells(sd, pathlib.Path(core_root) / stratum / 'bto-bfo' / f'seed-{seed}' / 'handoff-m0011' / 'handoff.npy')
    c0 = float(np.log(P / K))
    lm = {k: cells[k] + c0 for k in KEYS}; del cells
    tau = np.load(sd / 'tau90_v1.npz'); att = np.load(sd / 'attitude_v1.npz')
    side = {'tau90_s': tau['tau90_s'], 'energy_transferred_j': tau['energy_transferred_j'], 'decel_g': tau['decel_g'],
            'bank_deg_att': att['bank_deg'], 'bank_source': att['bank_source'], 'n_pulses': att['n_pulses']}
    res = analyse(lm, KEYS, HEAD, f4, g, side, pathlib.Path(rows_dir) / f'{stratum}-seed-{seed}.npz')
    res.update({'stratum': stratum, 'seed': seed, 'c0': c0})
    return res


def process_joined(job):
    """Arm V2 joined at 00:11 (smoke/joined_v2.py main(), weights reproduced line for line; D0-D4, total q = 1/3, C2 silent)."""
    import joined_v2 as JV
    seed, K, jroot, core_root, rows_dir = job
    hd = pathlib.Path(core_root) / 'run-j-waypoints' / 'bto-bfo' / f'seed-{seed}'
    h2241, h0011 = hd / 'handoff-m2241' / 'handoff.toml.gz', hd / 'handoff-m0011' / 'handoff.toml.gz'
    T0, T1 = JV.stop_unix(h2241), JV.stop_unix(h0011); dlnz = JV.stop_lnz(h0011) - JV.stop_lnz(h2241)
    m1, g1, _ = JV.load(pathlib.Path(jroot) / 'J2241', seed); m2, g2, _ = JV.load(pathlib.Path(jroot) / 'J0011', seed)
    p1 = JV.Prior(m1["config"]["hypotheses"]["end-of-flight"]["onset"]); p2 = JV.Prior(m2["config"]["hypotheses"]["end-of-flight"]["onset"])
    tk1 = g1("takeover_unix_s"); fo1 = g1("latent:realised_flameout_unix_s"); mech1 = g1("latent:onset_mechanism")
    s1 = (tk1 < T1) & ((mech1 == 0) | (mech1 == 1)) & ~(np.isfinite(fo1) & (fo1 < JV.T_M0011_BURST))
    tau1 = g1("latent:onset_unix_s"); P1 = tau1 + g1("latent:predicted_endurance_at_onset_s")
    with np.errstate(invalid="ignore"):
        lr1 = np.where(s1, p2.log_density(mech1, tau1, P1, T0) - p1.log_density(mech1, tau1, P1, T0), -np.inf)
    s1 = s1 & np.isfinite(lr1)
    lw1 = np.log(g1("weight")) + np.where(s1, lr1, 0.0); c1 = JV.cells(m1, g1, "m0011+")
    tau2 = g2("latent:onset_unix_s"); P2 = tau2 + g2("latent:predicted_endurance_at_onset_s"); mech2 = g2("latent:onset_mechanism")
    with np.errstate(invalid="ignore"):
        lr = p2.log_density(mech2, tau2, P2, T0) - p2.log_density(mech2, tau2, P2, T1)
    s2 = np.isfinite(lr) & (P2 >= T1)
    lw2 = np.log(g2("weight")) + np.where(s2, lr, -np.inf); c2 = JV.cells(m2, g2, "")
    f4 = np.r_[JV.family(g1), JV.family(g2)]
    c0 = float(np.log(1.0 / K)); lm = {}
    jkeys = [f'D{d} joined V2' for d in range(5)]
    for d, kk in zip(range(5), jkeys):
        lm[kk] = np.r_[np.where(s1, lw1 + c1[f'D{d}'], -np.inf), lw2 + dlnz + c2[f'D{d}']] + c0
    del c1, c2
    n1 = len(lw1)
    def g(name):
        a = g1(name) if name in m1['impact_columns'] else np.full(n1, np.nan)
        b = g2(name) if name in m2['impact_columns'] else np.full(len(lw2), np.nan)
        return np.r_[a, b]
    side = {}
    res = analyse(lm, jkeys, jkeys, f4, g, side, pathlib.Path(rows_dir) / f'joined-v2-seed-{seed}.npz')
    res.update({'stratum': 'joined-v2', 'seed': seed, 'c0': c0, 'n_S1_rows': int(n1), 'n_S2_rows': int(len(lw2)),
                'lnZ_seed': {kk: (float(logsumexp(lm[kk][np.isfinite(lm[kk])])) - c0) for kk in jkeys}})
    return res


def analyse(lm, keys, head, f4, g, side, rows_path):
'''
# old body after "lm = ..." line until end becomes analyse body
b0=body.index("    lat, lon, t = g('latitude_deg')")
rest=body[b0:]
rest=rest.replace("""    res = {'stratum': stratum, 'seed': seed, 'rows': int(len(lat)), 'c0': c0,""","""    res = {'rows': int(len(lat)),""")
rest=rest.replace("for k in KEYS:","for k in keys:").replace("for k in HEAD:","for k in head:")
rest=rest.replace("""    tau = np.load(sd / 'tau90_v1.npz'); att = np.load(sd / 'attitude_v1.npz')
    out = {'row': idx, 'f4': f4[idx], 'd_km': d[idx], 'az_deg': az[idx], 'db_deg': db[idx], 'xt_km': xt[idx], 'dX_km': dx[idx], 'dH_km': dh[idx],
           'tau90_s': tau['tau90_s'][idx], 'energy_transferred_j': tau['energy_transferred_j'][idx], 'decel_g': tau['decel_g'][idx],
           'bank_deg_att': att['bank_deg'][idx], 'bank_source': att['bank_source'][idx], 'n_pulses': att['n_pulses'][idx],
           'in_strip'""","""    out = {'row': idx, 'f4': f4[idx], 'd_km': d[idx], 'az_deg': az[idx], 'db_deg': db[idx], 'xt_km': xt[idx], 'dX_km': dx[idx], 'dH_km': dh[idx],
           'in_strip'""")
rest=rest.replace("""    for c in KEEP_COLS:""","""    for c, v in side.items(): out[c] = v[idx]
    for c in KEEP_COLS:""")
rest=rest.replace("""        except KeyError: pass""","""        except (KeyError, ValueError): pass""")
rest=rest.replace("""    pathlib.Path(rows_dir).mkdir(parents=True, exist_ok=True)
    np.savez_compressed(pathlib.Path(rows_dir) / f'{stratum}-seed-{seed}.npz',""","""    rows_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(rows_path,""")
s=s[:a]+new_proc+rest
open('flight_leg_worker.py','w').write(s)
E
python3 -c "import ast;ast.parse(open('kh/flight_leg_worker.py').read())" 2>&1; grep -n "stratum\|seed\b" kh/flight_leg_worker.py | sed -n 1,40p | grep -v "^.*#" | head -30