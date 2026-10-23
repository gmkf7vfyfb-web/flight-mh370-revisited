def g(D,br,m,o,f='all',bs='0.5 deg'):
    r=RC2[(RC2.D==D)&(RC2.branch==br)&(RC2.model==m)&(RC2.australia==o)&(RC2.family==f)&(RC2.bearing_sd==bs)].iloc[0]; return r
tab=[]
for br in 'TC':
    for o in ['none','populated (current, ~10x)','populated 5x','populated 3x','populated 1x','B','C']:
        rr=[g('D0',br,m,o) for m in MODELS]
        tab.append(f"| {br} | {o} | {rr[2].LLR:+.2f} ± {rr[2].sd_total:.2f} | {rr[1].LLR:+.2f} ± {rr[1].sd_total:.2f} | {rr[0].LLR:+.2f} ± {rr[0].sd_total:.2f} |")
print("\n".join(tab))
tabD=[]
for D in Ds:
    a=[g(D,br,'mean',o) for br in 'TC' for o in ('none','populated (current, ~10x)')]
    w=[g(D,br,'mean','none',bs='1.0 deg') for br in 'TC']
    tabD.append(f"| {D} | {a[0].ESS_branch:.0f} / {a[2].ESS_branch:.0f} | {a[0].LLR:+.2f} ± {a[0].sd_total:.2f} | {a[1].LLR:+.2f} ± {a[1].sd_total:.2f} | {a[2].LLR:+.2f} ± {a[2].sd_total:.2f} | {a[3].LLR:+.2f} ± {a[3].sd_total:.2f} | {w[0].LLR:+.2f} / {w[1].LLR:+.2f} |")
print("\n".join(tabD))
pt=[]
for name in ['crossing','strip50','strip100','strip150','strip200','haixun']:
    a=ex[(ex.point==name)&(ex.D=='D0')&(ex.model=='mean')].set_index('option')
    def f_(o): 
        v=a.loc[o]; return 'not computed' if not np.isfinite(v.LLR) else f"{v.LLR:+.2f} ± {v.sd_LLR:.2f}"
    gm=ex[(ex.point==name)&(ex.D=='D0')&(ex.option=='none')].set_index('model').LLR
    pt.append(f"| {name} | {f_('none')} | {f_('populated')} | {gm['glorys12']:+.2f} / {gm['globcurrent']:+.2f} |")
print("\n".join(pt))
