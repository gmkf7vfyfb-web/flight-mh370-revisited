
w=NR.w.values; print('ESS within150', w.sum()**2/(w**2).sum(), 'ESS time-consistent', w[inwin].sum()**2/(w[inwin]**2).sum())
m150=dG<150; print('sample ESS within 150', sw[m150].sum()**2/(sw[m150]**2).sum())
print('routes near ESS-like', f.sum()**2/(f**2).sum())
