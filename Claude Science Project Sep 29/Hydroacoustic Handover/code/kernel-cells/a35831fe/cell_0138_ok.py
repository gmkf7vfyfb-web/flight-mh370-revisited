print({k:v for k,v in CANDS['A'].items() if k!='members'} if isinstance(CANDS['A'],dict) else CANDS['A'])
print(CANDS['A'].get('members') if isinstance(CANDS['A'],dict) else '')
cands_fns=[n for n,v in globals().items() if callable(v) and any(s in n.lower() for s in ('fit','refit','locus','arrival','tt','bearing','line'))]
print(cands_fns)