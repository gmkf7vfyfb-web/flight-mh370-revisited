
src6=inspect.getsource(chart6)
src6=src6.replace('"Near the pair locus the stored trajectories mostly hit the sea earlier than the pair implies; 18 % of the nearby weight falls within 2 min of 00:31:41"',
 '"Near the pair locus the simulated impacts span 00:20-00:45 UTC (median 00:31:21); 18 % of the nearby weight falls within 2 min of the implied 00:31:41"')
src6=src6.replace("bbox_to_anchor=(0.06,0.355),ncol=3","bbox_to_anchor=(0.06,0.375),ncol=4")
src6=src6.replace("; weight share {r.share:.1e}; seed {T['k']}, route {T['j']}\"))","; weight share {r.share:.1e}\"))")
src6=src6.replace("    y=0.29\n","    y=0.305\n").replace("fontsize=6.3,color=c); y-=0.022","fontsize=6.3,color=c); y-=0.02")
src6=src6.replace("ls='-','highest weight within 150 km and impact within 2 min of 00:31:41'","ls='-','highest weight with impact within 2 min of 00:31:41'") 
src6=src6.replace("joined to end-of-flight rows by POSITION at 00:10:59 (distances: \"+', '.join(f\"{TJ[k]['dd']:.1f}\" for k,_,_,_ in SEL)+\" km)",
 "joined to end-of-flight rows by POSITION at 00:10:59 (seed/route/distance: \"+'; '.join(f\"{TJ[k]['k']}/{TJ[k]['j']}/{TJ[k]['dd']:.1f} km\" for k,_,_,_ in SEL)+\")")
SEL=[('hw',C_HW,'-','highest weight within 150 km'),('tc',C_TC,'-','highest weight with impact within 2 min of 00:31:41'),('cl',C_CL,(0,(4,2)),'closest to G (any non-zero weight)')]
exec(src6); fig=chart6(); save(fig,'chart6-neighbourhood-pair-g')
