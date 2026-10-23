
o=obs[obs.station=='H08S']; print('H08S trace f range',o.f_hz.min(),o.f_hz.max(),'H01W',obs[obs.station=='H01W'].f_hz.min(),obs[obs.station=='H01W'].f_hz.max())
print(o[o.f_hz<13].round(1).to_string()[:1500])
for zs in [10.0]:
    fa,ra=res[('H01W',zs)]; fb_,rb=res[('H08S',zs)]
    sh=[f for f in fa if f in fb_]; d=[ra[fa.index(f)]-rb[fb_.index(f)] for f in sh]
    s=stats(sh,d); print('C2',{k:(round(v,2) if isinstance(v,float) else v) for k,v in s.items()},verdict(s,(3.5,5)))
    print('d_b',dict(zip(sh,np.round(d,1))))
    print('r H01W',dict(zip(fa,np.round(ra,1)))); print('r H08S',dict(zip(fb_,np.round(rb,1))))
    # restrict H08S to >=12.5 for comparable span
    m=[i for i,f in enumerate(fb_) if f>=12.5]; s2=stats([fb_[i] for i in m],[rb[i] for i in m]); print('H08S >=12.5',round(s2['slope'],2),round(s2['level'],2))
