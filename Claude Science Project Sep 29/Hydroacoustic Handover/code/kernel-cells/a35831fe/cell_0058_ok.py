errmap=dict(zip(ev['index'],ev.err_time_s))
best['origin_err_s']=best.event.map(errmap)
best['strong']=(best.rx=='H01W')|(best.origin_err_s<=20)
def royer_flag(r,t):
    t=hms(t); g=best[(best.rx==str(r))&best.strong]; out=[]
    for _,b in g.iterrows():
        if abs(hms(b.candidate.split(' ')[0])-t)<=2 and b.chance_expect<0.5:
            out.append(f"Royer event {b.label or '#'+str(b.event)} ({b.cls}) predicted {b.predicted}, dt {b.dt_s:+.0f} s")
    if str(r)=='H01W' and abs(t-hms('00:52:03'))<=3: out.append('Royer event A pick bar (icequake)')
    if str(r)=='H01W' and abs(t-hms('00:54:30'))<=3: out.append('Royer event 5 arrow (uncertain, 49.8 S 133.1 E)')
    return '; '.join(out)
for d in reg:
    if d['id'].startswith('MP-') and d['group'].startswith('Module search: two-site'):
        ra,rb=d['receivers'].split(' x '); ta,tb=[x.strip()[:8] for x in d['times'].split('(')[0].split('/')]
        d['known_event']='; '.join(x for x in [royer_flag(ra,ta),royer_flag(rb,tb)] if x)
R=pd.DataFrame(reg); R['verdict']=R.apply(verdict,axis=1)
print(R[R.group.str.startswith('Module search: two')][['id','receivers','times','implied_lat','implied_lon','implied_impact','verdict','known_event']].to_string())
print(best[best.strong][['event','label','cls','rx','predicted','candidate','dt_s','chance_expect','origin_err_s']].to_string())