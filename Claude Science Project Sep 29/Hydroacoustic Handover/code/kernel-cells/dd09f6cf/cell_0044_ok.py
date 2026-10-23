byday=collections.defaultdict(list)
for nm,dn,g in polys: byday[dn].append((nm,g))
for dn in sorted(byday):
    gs=[g for _,g in byday[dn]]; u_=unary_union(gs); b=u_.bounds
    print(dn,(dt.date(2014,3,7)+dt.timedelta(days=dn)).strftime('%d %b'),len(gs),'lat %.1f..%.1f lon %.1f..%.1f'%(b[1],b[3],b[0],b[2]))