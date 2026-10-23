lines=[]
for d in DK:
    for key in ['Tcore','Ccore','strip']:
        e=res[d][key]['ESS']; sb=g_('seabed',d,key,'rho 05'); su=g_('surface',d,key,SUC)
        sbr=[g_('seabed',d,key,c) for c in SBC]; sur=T[(T.term=='surface')&(T.option==d)&(T.locality==key)].lnB
        Ph=res[d][key]['Ls']['s05']; Su=surf[(d,REF_A,'csiro')][key]
        lines.append(f"| {d} | {dict(Tcore='00:52:03 (T)',Ccore='00:54:30 (C)',strip='bearing strip, prior only')[key]} | {e:.0f}{' (not converged)' if e<30 else ''} | {Ph:.3f} / {res[d]['strip']['Ls_comp']['s05']:.3f} | {sb:+.2f} ± {BOOT[d][key]['seabed_sd']:.2f} | {min(sbr):+.2f} to {max(sbr):+.2f} | {Su:.3f} / {surf[(d,REF_A,'csiro')]['strip_comp']:.3f} | {su:+.2f} ± {BOOT[d][key]['surface_sd']:.2f} | {sur.min():+.2f} to {sur.max():+.2f} | {sb+su:+.2f} |")
print('\n'.join(lines))
for d in DK: print(d, 'Haixun seabed %.2f (rho0 %.2f, rho.5 %.2f, ATSB %.2f) surface %.2f (%.2f..%.2f)'%(g_('seabed',d,'Haixun point (sensitivity)','rho 05'),g_('seabed',d,'Haixun point (sensitivity)','rho 00'),g_('seabed',d,'Haixun point (sensitivity)','rho 50'),g_('seabed',d,'Haixun point (sensitivity)','ATSB only (no OI), rho 0.05'),g_('surface',d,'Haixun point (sensitivity)',SUC),T[(T.term=='surface')&(T.option==d)&(T.locality=='Haixun point (sensitivity)')].lnB.min(),T[(T.term=='surface')&(T.option==d)&(T.locality=='Haixun point (sensitivity)')].lnB.max()), 'strip mass %.5f'%res[d]['strip']['mass'], 'fam strip',{k:round(v,2) for k,v in res[d]['strip']['fam'].items()})