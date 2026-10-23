for q in ['"resid"', 'least_squares', 'CANDS[', 'travel time', 'tt_model', 'c = 1.482']:
    r=host.archive.search(q,k=4)
    print('==',q)
    for x in (r if isinstance(r,list) else r.get('results',[])):
        s=str(x); print(s[:300].replace('\\n','\n'))