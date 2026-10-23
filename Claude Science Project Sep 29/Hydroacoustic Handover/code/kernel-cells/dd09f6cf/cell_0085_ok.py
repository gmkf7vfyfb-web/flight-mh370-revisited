T.to_csv('search-likelihood-terms-all-cases.csv',index=False)
def g_(term,d,loc,case): return float(T[(T.term==term)&(T.option==d)&(T.locality==loc)&(T.case==case)].lnB.iloc[0])
SBC=['rho 00','rho 05','rho 25','rho 50','ATSB only (no OI), rho 0.05']; SUC='windage 0.5%, POD csiro, floor 0.0'
tab=[]
for d in DK:
    for loc in ['Tcore','Twide','Ccore','Cwide','strip','X50','X200','Haixun point (sensitivity)']:
        row={'option':d,'locality':loc,'ESS':res[d][loc]['ESS'] if loc in res[d] else np.nan}
        for c in SBC: row['seabed '+c]=g_('seabed',d,loc,c)
        row['surface ref']=g_('surface',d,loc,SUC)
        su=T[(T.term=='surface')&(T.option==d)&(T.locality==loc)].lnB; row['surface min']=su.min(); row['surface max']=su.max()
        if loc in BOOT[d]: row['seabed seedSE']=BOOT[d][loc]['seabed_sd']; row['surface seedSE']=BOOT[d][loc]['surface_sd']
        if loc in res[d] and 'Ls' in res[d][loc]: row['P_nofind_seabed_H(rho.05)']=res[d][loc]['Ls']['s05']
        tab.append(row)
TAB=pd.DataFrame(tab); TAB.to_csv('search-likelihood-terms-summary.csv',index=False)
print(TAB[TAB.option.isin(['D0','D1'])].round(3).to_string(index=False))
print({d:(round(res[d]['strip']['Ls_comp']['s05'],3),round(res[d]['strip']['Ls_comp']['x05'],3),round(surf[(d,REF_A,'csiro')]['strip_comp'],3), round(surf[(d,REF_A,'csiro')]['Tcore'],3), round(surf[(d,REF_A,'csiro')]['Ccore'],3)) for d in DK})