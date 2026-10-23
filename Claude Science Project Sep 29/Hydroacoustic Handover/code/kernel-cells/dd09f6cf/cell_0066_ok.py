GLAT0,GLON0,GST=-46.0,78.0,0.25
lat_cells=GLAT0+(np.arange(GNY*GNX)//GNX+0.5)*GST
h0=H[('D0','all')][:-1]
for a,pk in [('0.012','csiro'),('0.012','field'),('0.012','item')]:
    Lg=Lgrid[(a,pk)][:-1]; out=[]
    for b0 in range(-42,-14,2):
        m=(lat_cells>=b0)&(lat_cells<b0+2)&(h0>0)&np.isfinite(Lg)
        if m.any(): out.append('%d:%.2f'%(b0,(h0[m]*Lg[m]).sum()/h0[m].sum()))
    print(a,pk,' '.join(out))