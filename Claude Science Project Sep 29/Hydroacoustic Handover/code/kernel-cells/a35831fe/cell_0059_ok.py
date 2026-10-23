best['sigma']=np.where(best.rx=='H01W',3.0,best.tol_s/3)
best['strong']=((best.rx=='H01W')&(best.dt_s.abs()<=25))|((best.origin_err_s<=20)&(best.dt_s.abs()<=2*best.sigma)&(best.chance_expect<0.5))
best['weak_note']=(~best.strong)
for d in reg:
    if d['id'].startswith('MP-') and d['group'].startswith('Module search: two-site'):
        ra,rb=d['receivers'].split(' x '); ta,tb=[x.strip()[:8] for x in d['times'].split('(')[0].split('/')]
        d['known_event']='; '.join(x for x in [royer_flag(ra,ta),royer_flag(rb,tb)] if x)
        d['questions']=('3376 00:55:01 lies 28 s before the predicted arrival of Royer icequake A (about 3 sigma); ' if '00:55:01' in d['times'] else '')+\
            ('3274 is a low-power logger (power screen DROP); ' if '3274' in d['receivers'] else '')+'IMOS has no bearing, so the place is set only by the time difference; permutation test at chance level'
R=pd.DataFrame(reg); R['verdict']=R.apply(verdict,axis=1)
print(R.verdict.value_counts())
print(best[best.strong][['event','label','cls','rx','predicted','candidate','dt_s','chance_expect']].to_string())