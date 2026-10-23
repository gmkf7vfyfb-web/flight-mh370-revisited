for st,P in panels.items():
    sub=im.copy(); a,b,c,d=P["legend"]; sub[a:b,c:d]=255; sub[P["y0"]:P["y0"]+24, 52:115]=255
    pts=[]; prev=None; gaps=0
    for x in range(54, 337):
        ys=np.where(sub[P["y0"]+2:P["y1"]-1, x]<95)[0]+P["y0"]+2
        if len(ys)==0: continue
        cl=[((s+e)/2, e-s+1) for s,e in clusters(ys)]
        if prev is None: y=cl[0][0]
        else:
            y=min(cl, key=lambda t:abs(t[0]-prev))[0]
            if abs(y-prev)>14: gaps+=1; continue
        prev=y; pts.append((x, F(x), 150-(y-P["ytop"])/3.6, len(cl)))
    traces[st]=pd.DataFrame(pts, columns=["x_px","f_hz","tl_db","n_clusters"])
    t=traces[st]; print(st, len(t), "gaps", gaps, "f", t.f_hz.min().round(1), t.f_hz.max().round(1), "TL", t.tl_db.min().round(1), t.tl_db.max().round(1))