cd leg/out; python - <<'E'
import json, pandas as pd
r=json.load(open('L_regions.json')); print(r['logZ'])
for d in ['D0','D2','D5']:
    for rn in ['strip','disc50_crossing','disc100_crossing','disc200_crossing','disc400_crossing','disc50_haixun','disc400_haixun']:
        v=r['regions'][f'{d}|{rn}']; print(d,rn, f"mass {v['mass']:.3g} ess {v['ess']:.1f} effpar {v.get('eff_parents',0):.1f} n {v['n_rows']}", v.get('family_share'), v.get('t_impact_q'), [f"{x:.2g}" for x in (v.get('e_tr_q') or [])], [f"{x:.2g}" for x in (v.get('tau90_q') or [])])
q=json.load(open('q2_crosscheck.json'))
for k,v in q.items(): print(k, None if v['log10_B'] is None else round(v['log10_B'],2), round(v['ess_wL'],1), v['impact_q'], [round(x,2) for x in (v['lat_q'] or [])])
E