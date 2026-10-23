sw_md=swt.to_markdown(index=False)
sel=pt[pt['Case'].str.startswith('4-person raft, 1000 ft, vis >40')|pt['Case'].str.startswith('1-person')]
pt_md=pt.to_markdown(index=False)
open('pod/sw.md','w').write(sw_md); open('pod/pt.md','w').write(pt_md); print(sw_md[:300])