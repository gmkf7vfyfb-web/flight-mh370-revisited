
top5=pm.head(5).copy()
def hms2s(s): h,m,x=map(int,s.split(':')); return h*3600+m*60+x
res=[]
for _,r in top5.iterrows():
    L=locus2(r.lag_s, str(r.rx_a), str(r.rx_b))
    res.append(L); print(r.rx_a,r.rx_b,r.t_a,r.t_b,round(r.lag_s,1),L)
