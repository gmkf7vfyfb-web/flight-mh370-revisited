"""Drift alone (flat prior), nine finds, old window: scatter of the result over disjoint four-environment subsets, 256 module draws
(the 18-20 October configuration) and 16384 draws."""
exec(open('offline/drift_alone_mc_ramp.py').read().split('rows = []')[0])
def subj(R, j, n=4):
    return {m: {k: {'sets': [{p: R[m][k]['sets'][si][p][j * n:(j + 1) * n] for p in ('full', 'half_a', 'half_b')} for si in range(4)]} for k in common} for m in MODELS}
rows = []
for lab, R in (('7 Nov run', recO), ('this run, old window', recN)):
    for j in range(4):
        for zname, z in (('256', z256), ('16384', z16)):
            metaN.z = z; L = score(metaN, subj(R, j), None, common, mu0, NINE, {})
            rows.append(dict(run=lab, envs=f'{4*j+1}-{4*j+4}', level_draws=zname, **alone(L['globcurrent'], L['glorys12'])))
D = pd.DataFrame(rows); D.to_csv('res-alone-ramp/diag/drift-alone-four-environment-subsets.csv', index=False); print(D.round(2).to_string(index=False))
