for m in OD:
    post=OD[m]*area; post/=post.sum(); t50,t90,_=hpd_levels(post)
    dd=hav(HX[0],HX[1],LL,LO)
    for t,nm in ((t50,'50'),(t90,'90')):
        sel=post>=t; print(m,nm,'dist km q05/med/q95', np.round(np.quantile(dd[sel],[0.05,0.5,0.95])), 'mass-weighted median', round(float(wq(dd[sel],post[sel],[0.5])[0])))
