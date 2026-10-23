X['tp']=X.pred.map(hms)
def royer_near(r,t):
    g=X[X.rx==str(r)]; d=(g.tp-t); i=d.abs().idxmin(); row=g.loc[i]
    return int(row.event), row.label, row.cls, d[i], row.tol_s
mem=set()
for _,r in F.iterrows(): mem.add((r.rx_a,r.t_a)); mem.add((r.rx_b,r.t_b))
for r,t in sorted(mem):
    e,l,c,d,tol=royer_near(r,hms(t)); print(r,t,'nearest Royer ev',e,l,c,f"dt {-d:+.0f}s tol {tol}", 'MATCH' if abs(d)<=tol+(16 if r=='H01W' else 0) else '')