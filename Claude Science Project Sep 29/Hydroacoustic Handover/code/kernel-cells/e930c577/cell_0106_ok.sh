cd leg/out; python - <<'E'
import json
r=json.load(open('L_regions.json'))['regions']
for d in ['D0','D1','D2','D3','D4','D5']:
    v=r[f'{d}|strip']; print(d, f"{v['mass']:.3g}", round(v['ess'],1), round(v.get('eff_parents',0),1), {k:round(x,3) for k,x in v['family_share'].items()})
for d in ['D2']:
    for rn in ['disc50_crossing','disc100_crossing','disc200_crossing','disc400_crossing','disc50_haixun','disc100_haixun','disc200_haixun','disc400_haixun']:
        v=r[f'{d}|{rn}']; print(rn, f"{v['mass']:.3g}", round(v['ess'],1))
E
ls; du -sh .