c=1.482
CANDS={
 'A':dict(title='Kadri 00:49:58 + Perth Canyon 3376 + Portland 3274', arr=[('H01W','00:49:58'),('3376','00:51:30'),('3274','01:15:51')]),
 'B':dict(title='Cape Leeuwin 00:48:21 + Perth Canyon 3315 + Portland 3274', arr=[('H01W','00:48:21'),('3315','00:49:48'),('3274','01:15:51')]),
 'C':dict(title='Kadri Table 1 00:53:31 (bearing 257.58 deg)', arr=[('H01W','00:53:31')], bearing=257.58),
 'D':dict(title='Perth Canyon 3376 00:52:11 + Portland 3274 01:15:51', arr=[('3376','00:52:11'),('3274','01:15:51')]),
 'E':dict(title='Perth Canyon 3376 00:55:01 + Portland 3275 01:20:35', arr=[('3376','00:55:01'),('3275','01:20:35')]),
 'F':dict(title='Perth Canyon 3315 01:00:34 + Portland 3275 01:24:02', arr=[('3315','01:00:34'),('3275','01:24:02')]),
}
fla=np.linspace(-41,-20,4201); flo=np.interp(fla,alat,alon)
def dist_arr(r):
    la,lo=rx[r]; return G.inv(flo,fla,np.full_like(flo,lo),np.full_like(fla,la))[2]/1000
DA={r:dist_arr(r) for r in ['H01W','H08S','3315','3376','3274','3275','3250']}
for k,cd in CANDS.items():
    if 'bearing' in cd:
        r=t1[t1.time_utc==cd['arr'][0][1]].iloc[0]; L=r.arc_crossing_lat; i=np.argmin(abs(fla-L))
        t0=hms(cd['arr'][0][1])-DA['H01W'][i]/c; res=[0.0]
    else:
        tt=np.array([hms(t) for _,t in cd['arr']]); D=np.vstack([DA[r] for r,_ in cd['arr']])/c
        t0s=(tt[:,None]-D).mean(0); rss=((tt[:,None]-D-t0s)**2).sum(0); i=np.argmin(rss); L=fla[i]; t0=t0s[i]
        res=list(tt-D[:,i]-t0)
    cd.update(lat=fla[i], lon=flo[i], t0=t0, resid=res)
    print(k, f"{fla[i]:.2f} S {flo[i]:.2f} E impact {fmt(t0)} residuals {np.round(res,1)}")