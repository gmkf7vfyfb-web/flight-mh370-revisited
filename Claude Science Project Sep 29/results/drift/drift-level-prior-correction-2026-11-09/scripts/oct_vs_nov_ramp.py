"""Node-by-node: 18-20 October finds-only profile (4 environments, seeds 1-4) against the 7 Nov run (16/32 environments) on the same
84 points, nine finds, window to 30 Jun 2016, module 256 draws. Drift alone with a flat prior, one method for both."""
exec(open('offline/drift_alone_mc_ramp.py').read().split('rows = []')[0])
O = pd.read_csv('oct-profile.csv')
metaN.z = z256; Lall = score(metaN, recO, None, common, mu0, NINE, {})
L4 = score(metaN, sub(recO, 4), None, common, mu0, NINE, {})
nl = np.array([recO['globcurrent'][k]['lat'] for k in common]); nn_ = np.array([recO['globcurrent'][k]['lon'] for k in common])
idx = [int(np.argmin(np.hypot(O.node_lat.values - a, (O.node_lon.values - b) * np.cos(np.radians(a))))) for a, b in zip(nl, nn_)]
dmatch = np.hypot(O.node_lat.values[idx] - nl, (O.node_lon.values[idx] - nn_) * np.cos(np.radians(nl))).max(); print('max match distance deg', round(dmatch, 4))
oG = O['finds only [globcurrent, ln L]'].values[idx]; oY = O['finds only [glorys12, ln L]'].values[idx]
rows = []
for lab, g, y in (('18-20 Oct profile (4 environments)', oG, oY), ('7 Nov run, first 4 environments', L4['globcurrent'], L4['glorys12']),
                  ('7 Nov run, all environments', Lall['globcurrent'], Lall['glorys12'])):
    rows.append(dict(case=lab, **alone(g, y)))
print(pd.DataFrame(rows).round(2).to_string(index=False))
T = pd.DataFrame(dict(arc_lat=O.arc_lat.values[idx], position=O.position.values[idx], oct_GC=oG, nov_GC=Lall['globcurrent'], oct_GL=oY, nov_GL=Lall['glorys12']))
for c in ('oct_GC', 'nov_GC', 'oct_GL', 'nov_GL'): T[c] = T[c] - T[c].max()
T.to_csv('res-alone-ramp/diag/october-vs-november-profile-by-point.csv', index=False)
tr = T[T.position == 'track'].sort_values('arc_lat'); print(tr.round(1).to_string(index=False))
print('Oct state values:', O.state.value_counts().to_dict())
