for tid in ['00:40:34','00:48:55','00:49:58','00:52:50','00:53:31']:
    r=t1[t1.time_utc==tid].iloc[0]; L,Lo=r.arc_crossing_lat,r.arc_crossing_lon; ti=hms(r.implied_impact_utc)
    out=[]
    for rr in ['3315','3376','3274','3275','H08S']:
        la,lo=rx[rr]; d=G.inv(Lo,L,lo,la)[2]/1000; tp=ti+d/1.482
        spans=held[rr] if rr!='H08S' else kadri_cov['H08S']
        h=any(a<=tp<=b for a,b in spans)
        srch=any(a<=tp<=b for a,b in cov[rr])
        near=C[(C.rx==rr)&((C.t-tp).abs()<=20)]
        out.append(f"{rr} {fmt(tp)} held={'Y' if h else 'N'} searched={'Y' if srch else 'N'} cand={len(near)}{('('+','.join(fmt(x)[:8] for x in near.t)+')') if len(near) else ''}")
    print(tid, f"{L:.2f} {Lo:.2f} {r.implied_impact_utc}", ' | '.join(out))